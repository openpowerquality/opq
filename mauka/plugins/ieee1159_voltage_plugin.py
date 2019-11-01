# pylint: disable=I1101
"""
This plugin calculates the IEEE 1159 voltage events
"""

import typing
import multiprocessing

import numpy as np

import config
import log
import mongo
import mauka_native
import plugins.base_plugin
from plugins.routes import Routes
import protobuf.mauka_pb2
import protobuf.pb_util


INCIDENT_MAP = {
    "Momentary:Interruption": mongo.IncidentClassification.VOLTAGE_INTERRUPTION,
    "Temporary:Interruption": mongo.IncidentClassification.VOLTAGE_INTERRUPTION,
    "Instantaneous:Sag": mongo.IncidentClassification.VOLTAGE_SAG,
    "Momentary:Sag": mongo.IncidentClassification.VOLTAGE_SAG,
    "Temporary:Sag": mongo.IncidentClassification.VOLTAGE_SAG,
    "Instantaneous:Swell": mongo.IncidentClassification.VOLTAGE_SWELL,
    "Momentary:Swell": mongo.IncidentClassification.VOLTAGE_SWELL,
    "Temporary:Swell": mongo.IncidentClassification.VOLTAGE_SWELL,
    "Overvoltage": mongo.IncidentClassification.OVERVOLTAGE,
    "Undervoltage": mongo.IncidentClassification.UNDERVOLTAGE
}

DURATION_MAP = {
    "Momentary:Interruption": mongo.IEEEDuration.MOMENTARY,
    "Temporary:Interruption": mongo.IEEEDuration.TEMPORARY,
    "Instantaneous:Sag": mongo.IEEEDuration.INSTANTANEOUS,
    "Momentary:Sag": mongo.IEEEDuration.MOMENTARY,
    "Temporary:Sag": mongo.IEEEDuration.TEMPORARY,
    "Instantaneous:Swell": mongo.IEEEDuration.INSTANTANEOUS,
    "Momentary:Swell": mongo.IEEEDuration.MOMENTARY,
    "Temporary:Swell": mongo.IEEEDuration.TEMPORARY,
    "Overvoltage": mongo.IEEEDuration.SUSTAINED,
    "Undervoltage": mongo.IEEEDuration.SUSTAINED
}


def ieee1159_voltage(mauka_message: protobuf.mauka_pb2.MaukaMessage,
                     opq_mongo_client: mongo.OpqMongoClient,
                     ieee1159_voltage_plugin: typing.Optional['Ieee1159VoltagePlugin'] = None) -> typing.List[int]:
    """
    Calculate the ieee1159 voltage incidents and add them to the mongo database
    """
    data: typing.List[float] = list(mauka_message.payload.data)
    log.maybe_debug("Found %d Vrms values." % len(data), ieee1159_voltage_plugin)
    incidents = mauka_native.classify_rms(mauka_message.payload.start_timestamp_ms, data)
    log.maybe_debug("Found %d Incidents." % len(incidents), ieee1159_voltage_plugin)
    incident_ids: typing.List[int] = []
    array_data: np.ndarray = np.array(data)
    array_data = array_data - 120.0

    for incident in incidents:
        incident_id = mongo.store_incident(
            mauka_message.payload.event_id,
            mauka_message.payload.box_id,
            incident.start_time_ms,
            incident.end_time_ms,
            mongo.IncidentMeasurementType.VOLTAGE,
            max(np.abs(array_data.min()), np.abs(array_data.max())),
            [INCIDENT_MAP[incident.incident_classification]],
            [],
            {},
            opq_mongo_client,
            ieee_duration=DURATION_MAP[incident.incident_classification]
        )
        log.maybe_debug("Stored incident with id=%s" % incident_id, ieee1159_voltage_plugin)
        incident_ids.append(incident_id)

    return incident_ids


class Ieee1159VoltagePlugin(plugins.base_plugin.MaukaPlugin):
    """
    Mauka plugin that calculates IEEE1159 voltage incidents from rms_waveform
    """
    NAME = "Ieee1159VoltagePlugin"

    def __init__(self, conf: config.MaukaConfig, exit_event: multiprocessing.Event):
        """
        Initializes this plugin
        :param conf: Configuration dictionary
        :param exit_event: Exit event
        """
        super().__init__(conf, [Routes.rms_windowed_voltage], Ieee1159VoltagePlugin.NAME, exit_event)

    def on_message(self, topic, mauka_message):
        """
        Called async when a topic this plugin subscribes to produces a message
        :param topic: The topic that is producing the message
        :param mauka_message: The message that was produced
        """
        self.debug("on_message")
        if protobuf.pb_util.is_payload(mauka_message, protobuf.mauka_pb2.VOLTAGE_RMS_WINDOWED):
            incident_ids = ieee1159_voltage(mauka_message, self.mongo_client, self)
            for incident_id in incident_ids:
                # Produce a message to the GC
                self.produce(Routes.laha_gc, protobuf.pb_util.build_gc_update(self.name,
                                                                              protobuf.mauka_pb2.INCIDENTS,
                                                                              incident_id))

        else:
            self.logger.error("Received incorrect mauka message [%s] at IticPlugin",
                              protobuf.pb_util.which_message_oneof(mauka_message))
