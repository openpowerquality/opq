"""This module contains classes and functions for classifying power outages."""

import datetime
import multiprocessing
import typing

import mongo
import protobuf.mauka_pb2
import protobuf.util
from plugins.base_plugin import MaukaPlugin

BOX_STATUS_UP = "UP"
BOX_STATUS_DOWN = "DOWN"

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
    if opq_box is None or len(opq_box) == 0:
        return True
    else:
        return opq_box["unplugged"]


class OutagePlugin(MaukaPlugin):
    """This plugin identifies power outages by keeping track of the health collection for box status."""
    NAME = "OutagePlugin"

    def __init__(self, config: typing.Dict,
                 exit_event: multiprocessing.Event):
        super().__init__(config, ["heartbeat"], OutagePlugin.NAME, exit_event)
        self.last_update = datetime.datetime.utcnow()
        self.prev_incident_ids = {}

    def on_message(self, topic: str, mauka_message: protobuf.mauka_pb2.MaukaMessage):
        if protobuf.util.is_heartbeat_message(mauka_message):
            if OutagePlugin.NAME == mauka_message.source:
                box_statuses = list(self.mongo_client.health_collection.find({"service": "BOX",
                                                                              "timestamp": {"$gt": self.last_update}},
                                                                             {"_id": False,
                                                                              "info": False}))
                for box_status in box_statuses:
                    box_id = box_status["serviceID"]
                    status = box_status["status"]
                    timestamp = unix_time_millis(box_status["timestamp"])
                    unplugged = is_unplugged(self.mongo_client, box_id)

                    # No prev incidents
                    if box_id not in self.prev_incident_ids:
                        # No outages
                        if status == BOX_STATUS_UP:
                            continue

                        if status == BOX_STATUS_DOWN and unplugged:
                            continue

                        # New outage
                        if status == BOX_STATUS_DOWN and not unplugged:
                            incident_id = mongo.store_incident(-1,
                                                               box_id,
                                                               timestamp,
                                                               -1,
                                                               mongo.IncidentMeasurementType.HEALTH,
                                                               -1.0,
                                                               [mongo.IncidentClassification.OUTAGE],
                                                               opq_mongo_client=self.mongo_client,
                                                               copy_data=False)

                            self.prev_incident_ids[box_id] = incident_id

                    # Prev incidents
                    else:
                        prev_incident_id = self.prev_incident_ids[box_id]

                        # Update previous incident
                        self.mongo_client.incidents_collection.update_one({"incident_id": prev_incident_id},
                                                                          {"$SET":
                                                                               {"end_timestamp_ms": timestamp}})

                        # Outage over
                        if status == BOX_STATUS_UP or (status == BOX_STATUS_DOWN and unplugged):
                            del self.prev_incident_ids[box_id]

                        # Outage continues

                self.last_update = datetime.datetime.utcnow()

        else:
            self.logger.error("Received incorrect mauka message [%s] at %s",
                              protobuf.util.which_message_oneof(mauka_message),
                              OutagePlugin.NAME)
