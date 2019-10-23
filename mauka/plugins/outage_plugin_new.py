"""This module contains classes and functions for classifying power outages."""
import collections
import datetime
import multiprocessing
import typing

import config
import mongo
import protobuf.mauka_pb2
import protobuf.pb_util
from plugins.base_plugin import MaukaPlugin

from plugins.routes import Routes

EPOCH = datetime.datetime.utcfromtimestamp(0)


def unix_time_millis(date_time: datetime) -> float:
    """
    Turns a datetime into milliseconds since epoch.
    The datedate must already be in the timezone UTC.
    :param date_time: The datetime to convert to epoch.
    :return: The number of milliseconds since the epoch.
    """
    return (date_time - EPOCH).total_seconds() * 1000.0


def is_unplugged(mongo_client: mongo.OpqMongoClient, box_id: str) -> bool:
    """
    Checks the mongo database to determine if a device is marked as unplugged or not.
    :param mongo_client: An instance of a opq mongo client.
    :param box_id: The id of the box to check for.
    :return: Whether or not the box is unplugged. If a box can't be found or a value is not there then defaults True.
    """
    opq_box = mongo_client.opq_boxes_collection.find_one({"box_id": box_id}, {"_id": False, "unplugged": True})
    # pylint: disable=len-as-condition
    if opq_box is None or len(opq_box) == 0:
        return True
    else:
        return opq_box["unplugged"]


class OutagePlugin(MaukaPlugin):
    """This plugin identifies power outages by keeping track of the health collection for box status."""
    NAME = "OutagePlugin"

    def __init__(self, conf: config.MaukaConfig,
                 exit_event: multiprocessing.Event):
        super().__init__(conf, [Routes.heartbeat], OutagePlugin.NAME, exit_event)
        self.last_update = datetime.datetime.utcnow()
        self.prev_incident_ids = {}
        self.box_to_last_seen: typing.Dict[str, int] = {}

    def on_message(self, topic: str, mauka_message: protobuf.mauka_pb2.MaukaMessage):
        if protobuf.pb_util.is_heartbeat_message(mauka_message):
            if OutagePlugin.NAME == mauka_message.source:
                now = datetime.datetime.utcnow()
                box_to_max_timestamp: typing.Dict[str, int] = {}
                box_to_min_timestamp: typing.Dict[str, int] = {}
                measurements = self.mongo_client.measurements_collection.find({"timestamp_ms": {"$gte": unix_time_millis(self.last_update),
                                                                                                "$lte": unix_time_millis(now)}},
                                                                              projection={"_id": False,
                                                                                          "box_id": True,
                                                                                          "timestamp_ms": True})
                for measurement in measurements:
                    box_id = measurement["box_id"]
                    ts = measurement["timestamp_ms"]

                    if box_id not in box_to_max_timestamp:
                        box_to_max_timestamp[box_id] = 0
                        box_to_min_timestamp[box_id] = 9999999999999999999999

                    if ts > box_to_max_timestamp[box_id]:
                        box_to_max_timestamp[box_id] = ts

                    if ts < box_to_min_timestamp[box_id]:
                        box_to_min_timestamp[box_id] = ts

                self.box_to_last_seen = {**self.box_to_last_seen, **box_to_max_timestamp}

                for box_id, last_seen in self.box_to_last_seen.items():
                    if now - last_seen > 60_000:
                        if is_unplugged(self.mongo_client, box_id):
                            if box_id in self.prev_incident_ids:
                                del self.prev_incident_ids[box_id]
                            continue

                        # Fresh outage
                        if box_id not in self.prev_incident_ids:
                            incident_id = mongo.store_incident(-1,
                                                               box_id,
                                                               int(unix_time_millis(now)),
                                                               -1,
                                                               mongo.IncidentMeasurementType.HEALTH,
                                                               -1.0,
                                                               [mongo.IncidentClassification.OUTAGE],
                                                               opq_mongo_client=self.mongo_client,
                                                               copy_data=False)
                            # Produce a message to the GC
                            self.produce(Routes.laha_gc, protobuf.pb_util.build_gc_update(self.name,
                                                                                          protobuf.mauka_pb2.INCIDENTS,
                                                                                          incident_id))

                            self.prev_incident_ids[box_id] = incident_id
                        # Ongoing outage
                        else:
                            prev_incident_id = self.prev_incident_ids[box_id]

                            # Update previous incident
                            self.mongo_client.incidents_collection.update_one({"incident_id": prev_incident_id},
                                                                              {"$set": {"end_timestamp_ms": unix_time_millis(now)}})
                    else:
                        # Outage over
                        if box_id in self.prev_incident_ids:
                            prev_incident_id = self.prev_incident_ids[box_id]

                            # Update previous incident
                            self.mongo_client.incidents_collection.update_one({"incident_id": prev_incident_id},
                                                                              {"$set": {"end_timestamp_ms": box_to_min_timestamp[box_id]}})
                            del self.prev_incident_ids[box_id]


                self.last_update = now
