"""
This module contains the plugin definition for classifying voltage incidents by the Semi F47 standard.
"""

import typing

import numpy

import config
import plugins.base_plugin
import protobuf.pb_util
import protobuf.mauka_pb2
import constants
import mongo

PU = 120.0


# time in msec (1e-3 sec),
# of one data in the array


def viol_check(data, lvl):
    """
    viol_check function checks the data for all
    possible instances of the SEMI_F47 violation. The
    level is specified by the second argument lvl.
    :param data: The data to test.
    :param lvl: Level of violation.
    :return: Violations.
    """
    time_datum = 200.0 * 1.0 / constants.SAMPLES_PER_MILLISECOND

    lvl_tym = 200 if lvl == 5 else 500 if lvl == 7 else 1000  # is in msec
    lvl = 0.5 if lvl == 5 else 0.7 if lvl == 7 else 0.8

    # pylint: disable=E1111
    data_bool = numpy.logical_and(data >= (lvl - 0.05) * PU, data <= (lvl + 0.05) * PU)

    prev = 0
    violations = []
    k = 0
    prev_ind = 0
    for k in range(0, data_bool.size):
        if data_bool[k]:
            prev += 1
            if prev == 1:
                prev_ind = k
        else:
            if prev * time_datum >= lvl_tym:
                violations.append([prev_ind, k - 1])
            prev = 0

    if prev * time_datum >= lvl_tym:
        violations.append([prev_ind, k])

    return violations


def semi_violation(mongo_client, mauka_message) -> typing.List[int]:
    """
    Calculate semi violations.
    :param mongo_client: Mongo client for DB access.
    :param mauka_message: Mauka message to calculate violations over.
    """
    event_id = mauka_message.payload.event_id
    box_id = mauka_message.payload.box_id
    data = protobuf.pb_util.repeated_as_ndarray(mauka_message.payload.data)
    start_time_ms = mauka_message.payload.start_timestamp_ms

    # this will check if a violation ocurred or not
    time_datum = 200.0 * 1.0 / constants.SAMPLES_PER_MILLISECOND
    lvl = [5, 7, 8]
    incident_ids = []
    for idx in range(3):
        possible_violations = viol_check(data, lvl[idx])
        if len(possible_violations) > 0:
            # there are violations
            for _, violation in enumerate(possible_violations):
                dev = max(abs(120.0 - numpy.max(data[violation[0], violation[1]])),
                          abs(120.0 - numpy.min(data[violation[0], violation[1]])))
                incident_id = mongo.store_incident(
                    event_id,
                    box_id,
                    start_time_ms + violation[0] * time_datum,
                    start_time_ms + (violation[1] + 1) * time_datum,
                    mongo.IncidentMeasurementType.VOLTAGE,
                    dev,
                    [mongo.IncidentClassification.SEMI_F47_VIOLATION],
                    [],
                    {},
                    mongo_client)

                incident_ids.append(incident_id)
    return incident_ids


class SemiF47Plugin(plugins.base_plugin.MaukaPlugin):
    """
    This plugin subscribes to RMS windowed voltage and classifies Semi F47 violations.
    """

    def __init__(self, conf: config.MaukaConfig, exit_event):
        super().__init__(conf, ["RmsWindowedVoltage"], "SemiF47Plugin", exit_event)

    def on_message(self, topic, mauka_message):
        if protobuf.pb_util.is_payload(mauka_message, protobuf.mauka_pb2.VOLTAGE_RMS_WINDOWED):
            incident_ids = semi_violation(self.mongo_client, mauka_message)
            for incident_id in incident_ids:
                # Produce a message to the GC
                self.produce("laha_gc", protobuf.pb_util.build_gc_update(self.name,
                                                                         protobuf.mauka_pb2.INCIDENTS,
                                                                         incident_id))


def rerun(mongo_client: mongo.OpqMongoClient, mauka_message):
    """
    Rerun this plugin over the provided mauka message.
    :param mongo_client: Mongo client to perform DB queries.
    :param mauka_message: Mauka message to rerun this plugin over.
    """
    if protobuf.pb_util.is_payload(mauka_message, protobuf.mauka_pb2.VOLTAGE_RMS_WINDOWED):
        client = mongo.get_default_client(mongo_client)
        semi_violation(client, mauka_message)
