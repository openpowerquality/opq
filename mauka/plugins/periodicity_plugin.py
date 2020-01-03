"""
This module contains the plugin for Periodic Phenomena.
"""
import collections
import datetime
import functools
from dataclasses import dataclass
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

THD: str = "thd"
VOLTAGE: str = "voltage"
FREQUENCY: str = "frequency"
MINV: str = "min"
MEANV: str = "average"
MAXV: str = "max"


@dataclass
class Measurement:
    """
    Measurement
    """
    box_id: str
    timestamp_ms: int
    voltage: float
    thd: float
    frequency: float


@dataclass
class TrendValue:
    """
    TrendValue
    """
    name: str
    minv: float
    meanv: float
    maxv: float


@dataclass
class Trend:
    """
    Trend
    """
    box_id: str
    timestamp_ms: int
    trend_values: Dict[str, TrendValue]


T = TypeVar("T")
S = TypeVar("S")


@dataclass
class CycleResult:
    """
    CycleResult
    """
    box_id: str
    peaks: int
    mean_diff: float
    std_diff: float
    peak_dts: List[datetime.datetime]
    peak_diffs_from_mean: List[float]
    start_ts_ms: int
    end_ts_ms: int

    def timestamps_s(self) -> List[int]:
        epoch = datetime.datetime(1970, 1, 1)
        return list(map(lambda dt: round((dt - epoch).total_seconds()), self.peak_dts))


def search_for_sub_daily_voltage_cycles(box_id: str, measurements: List[Measurement]) -> Optional[CycleResult]:
    vs_raw = np.array(list(map(lambda measurement: measurement.voltage, measurements)))
    (b, a) = scipy.signal.butter(4, 1 / 3600, btype="highpass", fs=1.0)
    vs = scipy.signal.filtfilt(b, a, vs_raw)
    vs_minus_dc = vs - vs.mean()
    corr = np.correlate(vs_minus_dc, vs_minus_dc, mode="same")
    peaks = scipy.signal.find_peaks(corr, prominence=1000)[0]

    if peaks.size >= 3:
        dts = np.array(list(
                map(lambda measurement: datetime.datetime.utcfromtimestamp(measurement.timestamp_ms / 1000.0),
                    measurements)))

        epoch = datetime.datetime(1970, 1, 1)
        start_timestamp_ms: int = round((min(dts) - epoch).total_seconds() * 1000.0)
        end_timestamp_ms: int = round((max(dts) - epoch).total_seconds() * 1000.0)
        peak_diffs = np.diff(peaks)
        diff_mean = peak_diffs.mean()
        diff_std = peak_diffs.std()
        sag_peaks = scipy.signal.find_peaks(-vs_raw, distance=(diff_mean - diff_std))[0]
        deviations = list(vs_raw[sag_peaks] - 120.0)

        return CycleResult(box_id,
                           peaks.size,
                           diff_mean,
                           diff_std,
                           list(dts[sag_peaks]),
                           deviations,
                           start_timestamp_ms,
                           end_timestamp_ms)
    else:
        return None


def append_dict(other_dict: DefaultDict[S, List[T]],
                key: S,
                value: T) -> DefaultDict[S, List[T]]:
    """

    :param other_dict:
    :param key:
    :param value:
    :return:
    """
    other_dict[key].append(value)
    return other_dict


def get_measurements_map(start_time_s: int,
                         end_time_s: int,
                         mongo_client: pymongo.MongoClient) -> DefaultDict[str, List[Measurement]]:
    """

    :param start_time_s:
    :param end_time_s:
    :param mongo_client:
    :return:
    """
    database: pymongo.database.Database = mongo_client["opq"]
    coll: pymongo.collection.Collection = database["measurements"]

    query = {"timestamp_ms": {"$gte": start_time_s * 1_000.0,
                              "$lte": end_time_s * 1_000.0}}

    projection = {"_id": False,
                  "thd": True,
                  "voltage": True,
                  "frequency": True,
                  "timestamp_ms": True,
                  "box_id": True}

    cursor: pymongo.cursor.Cursor = coll.find(query, projection=projection).sort("timestamp_ms")
    measurements = list(
            map(lambda doc: Measurement(doc["box_id"],
                                        doc["timestamp_ms"],
                                        doc["voltage"] if "voltage" in doc else 0.0,
                                        doc["thd"] if "thd" in doc else 0.0,
                                        doc["frequency"] if "frequency" in doc else 0.0),
                list(cursor)))

    return functools.reduce(
            lambda measurement_dict, measurement: append_dict(measurement_dict, measurement.box_id, measurement),
            measurements,
            collections.defaultdict(list))


def find_incidents(cycle_result: CycleResult,
                   opq_mongo_client: mongo.OpqMongoClient) -> List[Dict]:
    incidents_coll: pymongo.collection.Collection = opq_mongo_client.incidents_collection
    incident_queries: List[Dict] = []
    for ts_s in cycle_result.timestamps_s():
        start_ts_ms: int = round((ts_s - cycle_result.std_diff) * 1000.0)
        end_ts_ms: int = round((ts_s + cycle_result.std_diff) * 1000.0)
        incident_queries.append({"start_timestamp_ms": {"$gte": start_ts_ms,
                                                        "$lte": end_ts_ms}})

    incident_query: Dict = {"box_id": cycle_result.box_id,
                            "classifications": "VOLTAGE_SAG",
                            "$and": incident_queries}

    incident_projection: Dict[str, bool] = {"_id": False,
                                            "box_id": True,
                                            "classifications": True,
                                            "incident_id": True,
                                            "event_id": True,
                                            "start_timestamp_ms": True}

    incidents_cursor: pymongo.cursor.Cursor = incidents_coll.find(incident_query, projection=incident_projection)

    return list(incidents_cursor)


def find_events(cycle_result: CycleResult,
                opq_mongo_client: mongo.OpqMongoClient) -> List[Dict]:
    events_coll: pymongo.collection.Collection = opq_mongo_client.events_collection
    event_queries: List[Dict] = []
    for ts_s in cycle_result.timestamps_s():
        start_ts_ms: int = round((ts_s - cycle_result.std_diff) * 1000.0)
        end_ts_ms: int = round((ts_s + cycle_result.std_diff) * 1000.0)

        event_queries.append({"target_event_start_timestamp_ms": {"$gte": start_ts_ms,
                                                                  "$lte": end_ts_ms}})

    events_query: Dict = {"boxes_received": cycle_result.box_id,
                          "$and": event_queries}

    events_projection: Dict[str, bool] = {"_id": False,
                                          "box_id": True,
                                          "target_event_start_timestamp_ms": True,
                                          "event_id": True}

    events_cursor: pymongo.cursor.Cursor = events_coll.find(events_query, projection=events_projection)

    return list(events_cursor)


def handle_cycle_result(cycle_result: CycleResult,
                        box_id: str,
                        opq_mongo_client: mongo.OpqMongoClient,
                        periodicity_plugin: 'PeriodicityPlugin') -> Optional[int]:
    """

    :param cycle_result:
    :return:
    """
    if cycle_result.peaks > 3 and cycle_result.std_diff < 600:
        maybe_debug(f"Found viable cycle result with {cycle_result.peaks} peaks and std={cycle_result.std_diff}",
                    periodicity_plugin)

        affected_incidents: List[Dict] = find_incidents(cycle_result, opq_mongo_client)
        affected_events: List[Dict] = find_events(cycle_result, opq_mongo_client)

        incident_ids: List[int] = list(map(lambda incident: incident["incident_id"], affected_incidents))
        event_ids_from_incidents: Set[int] = set(map(lambda incident: incident["event_id"], affected_incidents))
        event_ids_from_events: Set[int] = set(map(lambda event: event["event_id"], affected_events))
        event_ids: List[int] = list(event_ids_from_incidents.union(event_ids_from_events))

        maybe_debug(f"Found {len(incident_ids)} related incident ids and {len(event_ids)} event ids",
                    periodicity_plugin)

        # Check to see if a periodic incident already exists
        phenomena_query: Dict = {"phenomena_type.type": "periodic",
                                 "affected_opq_boxes": box_id}

        phenomena_projection: Dict[str, bool] = {"_id": False,
                                                 "phenomena_id": True,
                                                 "phenomena_type": True,
                                                 "affected_opq_boxes": True,
                                                 "related_event_ids": True,
                                                 "related_incident_ids": True}

        phenomena_doc: Dict = opq_mongo_client.phenomena_collection.find_one(phenomena_query,
                                                                             projection=phenomena_projection)

        # If it does
        if phenomena_doc is not None:
            maybe_debug("Phenomena already exists. Updating...", periodicity_plugin)
            prev_phenomena_id: int = phenomena_doc["phenomena_id"]

            # Update list of affected Events and Incidents
            phenomena_coll: pymongo.collection.Collection = opq_mongo_client.phenomena_collection

            related_event_ids: Set[int] = set(phenomena_doc["related_event_ids"])
            related_incident_ids: Set[int] = set(phenomena_doc["related_incident_ids"])

            event_ids_to_add: List[int] = list(set(event_ids) - related_event_ids)
            incident_ids_to_add: List[int] = list(set(incident_ids) - related_incident_ids)

            maybe_debug(f"Adding {len(event_ids_to_add)} new event ids and {len(incident_ids_to_add)} new incident ids",
                        periodicity_plugin)

            # Update list of timestamps and peak deviations
            peaks_ts: List[int] = phenomena_doc["phenomena_type"]["period_timestamps"]
            peaks_ts_set: Set[int] = set(peaks_ts)

            related_period_timestamps_to_add: List[int] = []
            related_period_deviations_to_add: List[float] = []

            for i, timestamp in enumerate(cycle_result.timestamps_s()):
                if timestamp not in peaks_ts_set:
                    related_period_timestamps_to_add.append(timestamp)
                    related_period_deviations_to_add.append(cycle_result.peak_diffs_from_mean[i])

            maybe_debug(f"Adding {len(related_period_timestamps_to_add)} timestamps and {len(related_period_deviations_to_add)} deviations",
                        periodicity_plugin)

            # Perform the update
            update: Dict = {"$push": {"related_event_ids": {"$each": event_ids_to_add},
                                      "related_incident_ids": {"$each": incident_ids_to_add},
                                      "phenomena_type.period_timestamps": {"$each": related_period_timestamps_to_add},
                                      "phenomena_type.deviation_from_mean_values": {
                                          "$each": related_period_deviations_to_add}},
                            "$set": {"updated_ts_ms": mongo.timestamp_ms(),
                                     "end_ts_ms": cycle_result.end_ts_ms,
                                     "expire_at": mongo.timestamp_s_plus_s(opq_mongo_client.get_ttl("phenomena"))}}

            # Update metrics
            prev_std_s: float = phenomena_doc["phenomena_type"]["std_s"]
            if cycle_result.std_diff < prev_std_s:
                maybe_debug("Updating metrics", periodicity_plugin)
                update["$set"]["phenomena_type.std_s"] = cycle_result.std_diff
                update["$set"]["phenomena_type.period_s"] = cycle_result.mean_diff
                update["$set"]["phenomena_type.peaks"] = cycle_result.peaks
            else:
                maybe_debug("Not updating metrics", periodicity_plugin)

            phenomena_coll.update_one({"phenomena_id": prev_phenomena_id}, update)
            maybe_debug(f"Prev phenomena with id={prev_phenomena_id} updated", periodicity_plugin)
            return prev_phenomena_id
        else:
            # Store a new phenomena
            maybe_debug("Phenomena does not exists, creating a new one", periodicity_plugin)
            return mongo.store_periodic_phenomena(opq_mongo_client,
                                                  cycle_result.start_ts_ms,
                                                  cycle_result.end_ts_ms,
                                                  [box_id],
                                                  incident_ids,
                                                  event_ids,
                                                  cycle_result.mean_diff,
                                                  cycle_result.std_diff,
                                                  cycle_result.timestamps_s(),
                                                  cycle_result.peak_diffs_from_mean,
                                                  cycle_result.peaks)

    maybe_debug(f"No cycle result found for {box_id}", periodicity_plugin)
    return None


def check_for_periodic_phenomena(interval_s: float,
                                 opq_mongo_client: mongo.OpqMongoClient,
                                 periodicity_plugin: 'PeriodicityPlugin'):
    """

    """
    maybe_debug("Collecting measurements for past 24 hours", periodicity_plugin)
    mongo_client: pymongo.MongoClient = opq_mongo_client.client
    now = int(round(time.time()))
    all_measurements = get_measurements_map(now - 86400, now, mongo_client)
    maybe_debug(f"Found measurements for {len(all_measurements)} devices", periodicity_plugin)
    for box_id, measurements in all_measurements.items():
        maybe_debug(f"Preparing to search for voltage cycles for {box_id} with {len(measurements)} measurements",
                    periodicity_plugin)
        # try:
        cycle_result: Optional[CycleResult] = search_for_sub_daily_voltage_cycles(box_id, measurements)
        if cycle_result is not None:
            maybe_debug("Got cycle result", periodicity_plugin)
            phenomena_id: Optional[int] = handle_cycle_result(cycle_result,
                                                              box_id,
                                                              opq_mongo_client,
                                                              periodicity_plugin)
            if phenomena_id is not None:
                gc_update = protobuf.pb_util.build_gc_update(PeriodicityPlugin.NAME,
                                                             protobuf.mauka_pb2.PHENOMENA,
                                                             phenomena_id)
                periodicity_plugin.produce(Routes.laha_gc, gc_update)
                maybe_debug(f"Performed GC update for {phenomena_id}", periodicity_plugin)
            else:
                maybe_debug("Did not get phenomena id", periodicity_plugin)
        else:
            maybe_debug("Did not get cycle result", periodicity_plugin)
        # except Exception as e:
        #     periodicity_plugin.logger.error("Error: %s", str(e))

    timer: threading.Timer = threading.Timer(interval_s,
                                             check_for_periodic_phenomena,
                                             (interval_s,
                                              opq_mongo_client,
                                              periodicity_plugin))
    timer.start()


class PeriodicityPlugin(plugins.base_plugin.MaukaPlugin):
    """
    This plugin subscribes to annotation request messages.
    """
    NAME: str = "PeriodicityPlugin"

    def __init__(self, conf: config.MaukaConfig, exit_event):
        super().__init__(conf, [], PeriodicityPlugin.NAME, exit_event)
        self.debug("Preparing to start checking for periodic phenomena")
        check_for_periodic_phenomena(120,
                                     self.mongo_client,
                                     self)

    def on_message(self, topic: str, mauka_message: protobuf.mauka_pb2.MaukaMessage):
        """

        :param topic:
        :param mauka_message:
        :return:
        """
        self.logger.warning("Received message: %s", str(mauka_message))



