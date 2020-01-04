"""
This module contains the plugin for Future Phenomena.
"""
import collections
import datetime
import functools
from dataclasses import dataclass
import sched
import time
from typing import DefaultDict, Dict, List, Optional, Set, TypeVar
import threading

import config
import numpy as np
import scipy.signal
from log import maybe_debug
import mongo
import plugins.base_plugin
import protobuf.mauka_pb2
import protobuf.pb_util
import pymongo
import pymongo.database

from plugins.routes import Routes
import plugins.threshold_optimization_plugin as threshold_plugin


def future_phenomena_already_exists(box_id: str,
                                    timestamp_ms: int,
                                    phenomena_coll: pymongo.collection.Collection) -> bool:
    phenomena_query: Dict = {"phenomena_type.type": "future",
                             "affected_opq_boxes": box_id,
                             "start_ts_ms": {"$lt": timestamp_ms},
                             "end_ts_ms": {"$gt": timestamp_ms}}

    phenomena_projection: Dict[str, bool] = {"_id": False,
                                             "phenomena_type": True,
                                             "affected_opq_boxes": True,
                                             "start_ts_ms": True,
                                             "end_ts_ms": True}

    phenomena_docs: List[Dict] = list(phenomena_coll.find(phenomena_query, projection=phenomena_projection))

    return len(phenomena_docs) > 0


def adjust_measurements_rate(box_id: str,
                             measurement_cycles: int,
                             future_plugin: 'FuturePlugin'):
    mauka_message = protobuf.mauka_pb2.MaukaMessage = protobuf.pb_util.build_box_optimization_request("FuturePlugin",
                                                                                                      [box_id],
                                                                                                      measurement_cycles)
    future_plugin.produce(Routes.box_optimization_request, mauka_message)


def adjust_event_thresholds(box_id: str,
                            percent_voltage_low: float,
                            percent_voltage_high: float,
                            future_plugin: 'FuturePlugin') -> None:
    threshold_optimization_req: protobuf.mauka_pb2.MaukaMessage = protobuf.pb_util.build_threshold_optimization_request(
            "FuturePhenomena",
            threshold_percent_v_low=percent_voltage_low,
            threshold_percent_v_high=percent_voltage_high,
            box_id=box_id
    )

    future_plugin.produce(Routes.threshold_optimization_request, threshold_optimization_req)


def adjust_metrics(box_id: str,
                   percent_voltage_low: float,
                   percent_voltage_high: float,
                   measurement_cycles: int,
                   future_plugin: 'FuturePlugin'):
    future_plugin.debug(f"Adjusting metrics for box_id={box_id} v_low={percent_voltage_low} v_high={percent_voltage_high} m_cycles={measurement_cycles}")
    adjust_measurements_rate(box_id, measurement_cycles, future_plugin)
    adjust_event_thresholds(box_id, percent_voltage_low, percent_voltage_high, future_plugin)


def create_new_future_phenomena(start_ts_ms: int,
                                end_ts_ms: int,
                                box_id: str,
                                periodic_phenomena_id: int,
                                opq_mongo_client: mongo.OpqMongoClient,
                                scheduler: sched.scheduler,
                                future_plugin: 'FuturePlugin') -> Optional[int]:
    if start_ts_ms < mongo.timestamp_ms():
        future_plugin.debug(f"start ts {start_ts_ms} > now {mongo.timestamp_ms()}")
        return None

    future_plugin.debug("Creating new future phenomena...")
    makai_config_doc: threshold_plugin.MakaiConfigType = opq_mongo_client.makai_config_collection.find_one()
    makai_config: threshold_plugin.MakaiConfig = threshold_plugin.MakaiConfig(makai_config_doc)

    if box_id in makai_config.box_id_to_triggering_override:
        future_plugin.debug(f"{box_id} has overrides")
        triggering_override: threshold_plugin.TriggeringOverride = makai_config.box_id_to_triggering_override[box_id]
        default_percent_deviation_low: float = triggering_override.threshold_percent_v_low
        default_percent_deviation_high: float = triggering_override.threshold_percent_v_high
    else:
        future_plugin.debug(f"{box_id} does not have overrides")
        default_percent_deviation_low: float = makai_config.default_threshold_percent_v_low
        default_percent_deviation_high: float = makai_config.default_threshold_percent_v_high

    altered_percent_deviation_low: float = 1.0
    altered_percent_deviation_high: float = 1.0

    default_measurement_cycles: int = 60
    altered_measurement_cycles: int = 10

    future_plugin.debug(f"default_m_cycles={default_measurement_cycles} "
                        f"default_v_low={default_percent_deviation_low} "
                        f"default_v_high={default_percent_deviation_high} "
                        f"altered_m_cycles={altered_measurement_cycles} "
                        f"altered_v_low={altered_percent_deviation_low} "
                        f"altered_b_high={altered_percent_deviation_high}")

    # Create the phenomena
    phenomena_id: int = mongo.store_future_phenomena(opq_mongo_client,
                                                     start_ts_ms,
                                                     end_ts_ms,
                                                     [box_id],
                                                     [],
                                                     [],
                                                     "voltage",
                                                     default_measurement_cycles,
                                                     default_percent_deviation_low,
                                                     default_percent_deviation_high,
                                                     altered_measurement_cycles,
                                                     altered_percent_deviation_low,
                                                     altered_percent_deviation_high,
                                                     periodic_phenomena_id,
                                                     False,
                                                     False)

    # Schedule modifying the metrics
    start_ts_s: float = start_ts_ms / 1_000.0
    end_ts_s: float = end_ts_ms / 1_000.0

    future_plugin.debug(f"adjust start_ts_s={start_ts_s} ({datetime.datetime.utcfromtimestamp(start_ts_s)}) which is {start_ts_s - mongo.timestamp_s()} seconds from now")
    future_plugin.debug(f"adjust end_ts_s={end_ts_s} ({datetime.datetime.utcfromtimestamp(end_ts_s)}) which is {end_ts_s - mongo.timestamp_s()} seconds from now")


    scheduler.enterabs(start_ts_s,
                       1,
                       adjust_metrics,
                       (box_id,
                        altered_percent_deviation_low,
                        altered_percent_deviation_high,
                        altered_measurement_cycles,
                        future_plugin))

    scheduler.enterabs(end_ts_s,
                       1,
                       adjust_metrics,
                       (box_id,
                        default_percent_deviation_low,
                        default_percent_deviation_high,
                        default_measurement_cycles,
                        future_plugin))

    return phenomena_id


def handle_periodic_doc(phenomena_doc: Dict,
                        opq_mongo_client: mongo.OpqMongoClient,
                        phenomena_coll: pymongo.collection.Collection,
                        scheduler: sched.scheduler,
                        future_plugin: 'FuturePlugin') -> Optional[int]:
    future_plugin.debug("Handling periodic doc")
    box_id: str = phenomena_doc["affected_opq_boxes"][0]
    periodic_phenomena: Dict = phenomena_doc["phenomena_type"]
    periodic_phenomena_id: int = phenomena_doc["phenomena_id"]
    period_s: float = periodic_phenomena["period_s"]
    std_s: float = periodic_phenomena["std_s"]
    period_timestamps: List[int] = periodic_phenomena["period_timestamps"]
    last_period_timestamp: int = max(period_timestamps)

    future_timestamp_s: int = round(last_period_timestamp + period_s)
    future_timestamp_ms: int = round((last_period_timestamp + period_s) * 1000.0)

    if not future_phenomena_already_exists(box_id,
                                           future_timestamp_ms,
                                           phenomena_coll):
        future_plugin.debug("Future phenomena does not exist, creating one")
        start_ts_ms: int = round((future_timestamp_s - std_s) * 1000.0)
        end_ts_ms: int = round((future_timestamp_s + std_s) * 1000.0)

        phenomena_id = create_new_future_phenomena(start_ts_ms,
                                                   end_ts_ms,
                                                   box_id,
                                                   periodic_phenomena_id,
                                                   opq_mongo_client,
                                                   scheduler,
                                                   future_plugin)
        return phenomena_id
    else:
        future_plugin.debug("Future phenomena already exists, ignoring...")
        return None


def find_incidents(box_id: str,
                   start_ts_ms: int,
                   end_ts_ms: int,
                   opq_mongo_client: mongo.OpqMongoClient) -> List[Dict]:
    incidents_coll: pymongo.collection.Collection = opq_mongo_client.incidents_collection

    incident_query: Dict = {"box_id": box_id,
                            "classifications": "VOLTAGE_SAG",
                            "start_timestamp_ms": {"$gte": start_ts_ms,
                                                   "$lte": end_ts_ms}}

    incident_projection: Dict[str, bool] = {"_id": False,
                                            "box_id": True,
                                            "classifications": True,
                                            "incident_id": True,
                                            "event_id": True,
                                            "start_timestamp_ms": True}

    incidents_cursor: pymongo.cursor.Cursor = incidents_coll.find(incident_query, projection=incident_projection)

    return list(incidents_cursor)


def find_events(box_id: str,
                start_ts_ms: int,
                end_ts_ms: int,
                opq_mongo_client: mongo.OpqMongoClient) -> List[Dict]:
    events_coll: pymongo.collection.Collection = opq_mongo_client.events_collection

    events_query: Dict = {"boxes_received": box_id,
                          "target_event_start_timestamp_ms": {"$gte": start_ts_ms,
                                                              "$lte": end_ts_ms}}

    events_projection: Dict[str, bool] = {"_id": False,
                                          "box_id": True,
                                          "target_event_start_timestamp_ms": True,
                                          "event_id": True}

    events_cursor: pymongo.cursor.Cursor = events_coll.find(events_query, projection=events_projection)

    return list(events_cursor)


def handle_future_doc(future_doc: Dict,
                      phenomena_coll: pymongo.collection.Collection,
                      opq_mongo_client: mongo.OpqMongoClient,
                      future_plugin: 'FuturePlugin') -> int:
    box_id: str = future_doc["affected_opq_boxes"][0]
    start_ts_ms: int = future_doc["start_ts_ms"]
    end_ts_ms: int = future_doc["end_ts_ms"]
    phenomena_id: int = future_doc["phenomena_id"]

    affected_incidents: List[Dict] = find_incidents(box_id, start_ts_ms, end_ts_ms, opq_mongo_client)
    affected_events: List[Dict] = find_events(box_id, start_ts_ms, end_ts_ms, opq_mongo_client)

    incident_ids: List[int] = list(map(lambda incident: incident["incident_id"], affected_incidents))
    event_ids_from_incidents: Set[int] = set(map(lambda incident: incident["event_id"], affected_incidents))
    event_ids_from_events: Set[int] = set(map(lambda event: event["event_id"], affected_events))
    event_ids: List[int] = list(event_ids_from_incidents.union(event_ids_from_events))

    future_plugin.debug(f"Found {len(event_ids)} event ids and {len(incident_ids)} incident ids")

    prev_incident_ids: Set[int] = set(future_doc["related_incident_ids"])
    prev_event_ids: Set[int] = set(future_doc["related_event_ids"])

    future_plugin.debug(f"Found {len(prev_event_ids)} prev event ids and {len(prev_incident_ids)} prev incident ids")

    new_event_ids: List[int] = list(set(event_ids) - prev_event_ids)
    new_incident_ids: List[int] = list(set(incident_ids) - prev_incident_ids)

    future_plugin.debug(f"Found {len(new_event_ids)} new event ids and {len(new_incident_ids)} new incident ids")

    realized: bool = len(event_ids) > 0 or len(incident_ids) > 0

    future_plugin.debug(f"realized={realized}")
    update: Dict = {"$set": {"phenomena_type.realized": realized,
                             "phenomena_type.checked": True,
                             "updated_ts_ms": mongo.timestamp_ms()}}

    if realized:
        array_updates: Dict = {}
        if len(new_event_ids) > 0:
            array_updates["related_events_ids"] = {"$each": new_event_ids}
        if len(new_incident_ids) > 0:
            array_updates["related_incident_ids"] = {"$each": new_incident_ids}
        update["$push"] = array_updates
    else:
        pass

    phenomena_coll.update_one({"phenomena_id": phenomena_id}, update)
    future_plugin.debug("Update of prev Future phenomena performed")

    return phenomena_id


def schedule_future_phenomena(interval_s: float,
                              scheduler: sched.scheduler,
                              opq_mongo_client: mongo.OpqMongoClient,
                              future_plugin: 'FuturePlugin'):
    """

    """

    phenomena_coll: pymongo.collection.Collection = opq_mongo_client.phenomena_collection
    periodic_query: Dict = {"phenomena_type.type": "periodic"}
    periodic_docs: List[Dict] = list(phenomena_coll.find(periodic_query))

    future_plugin.debug(f"Loaded {len(periodic_docs)} periodic_docs")

    new_phenomena_ids: List[int] = []

    # Create new phenomena
    for periodic_doc in periodic_docs:
        phenomena_id = handle_periodic_doc(periodic_doc, opq_mongo_client, phenomena_coll, scheduler, future_plugin)
        if phenomena_id is not None:
            future_plugin.debug(f"Found new phenomena_id={phenomena_id}")
            new_phenomena_ids.append(phenomena_id)

    # Check status of old phenomena
    now_ms: int = mongo.timestamp_s()

    future_query: Dict = {"phenomena_type.type": "future",
                          "end_ts_ms": {"$lte": now_ms},
                          "phenomena_type.checked": False}

    future_projection: Dict[str, bool] = {"_id": False,
                                          "phenomena_id": True,
                                          "phenomena_type": True,
                                          "start_ts_ms": True,
                                          "end_ts_ms": True,
                                          "affected_opq_boxes": True}

    future_docs: List[Dict] = list(phenomena_coll.find(future_query, projection=future_projection))
    future_plugin.debug(f"Checking for Events and Incidents in {len(future_docs)} future phenomena")

    old_phenomena_ids: List[int] = []
    for future_doc in future_docs:
        phenomena_id = handle_future_doc(future_doc, phenomena_coll, opq_mongo_client, future_plugin)
        if phenomena_id is not None:
            old_phenomena_ids.append(phenomena_id)

    all_phenomena_ids: List[int] = new_phenomena_ids.extend(old_phenomena_ids)

    # Update GC for new phenomena ids

    timer: threading.Timer = threading.Timer(interval_s,
                                             schedule_future_phenomena,
                                             (interval_s,
                                              opq_mongo_client,
                                              future_plugin))
    timer.start()


class FuturePlugin(plugins.base_plugin.MaukaPlugin):
    """
    A Future Phenomena plugin.
    """
    NAME: str = "FuturePlugin"

    def __init__(self, conf: config.MaukaConfig, exit_event):
        super().__init__(conf, [], FuturePlugin.NAME, exit_event)
        self.debug("Starting the FuturePlugin")
        scheduler: sched.scheduler = sched.scheduler(time.time, time.sleep)
        schedule_future_phenomena(300,
                                  scheduler,
                                  self.mongo_client,
                                  self)

    def on_message(self, topic: str, mauka_message: protobuf.mauka_pb2.MaukaMessage):
        """

        :param topic:
        :param mauka_message:
        :return:
        """
        self.logger.warning("Received message: %s", str(mauka_message))
