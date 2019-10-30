"""
This plugin calculates the IEEE 1159 voltage events
"""

import typing
import multiprocessing

import mongo
import numpy as np
import mauka_native

import analysis
import config
import constants
import plugins.base_plugin
from plugins.routes import Routes
import protobuf.mauka_pb2
import protobuf.pb_util

IEEE_1159_TOLERANCE_RANGES = [
    [analysis.percent_nominal_to_rms(0.0), analysis.percent_nominal_to_rms(0.1)],
    [analysis.percent_nominal_to_rms(0.1), analysis.percent_nominal_to_rms(0.9)],
    [analysis.percent_nominal_to_rms(0.8), analysis.percent_nominal_to_rms(0.9)],
    [analysis.percent_nominal_to_rms(1.1), analysis.percent_nominal_to_rms(1.2)],
    [analysis.percent_nominal_to_rms(1.1), analysis.percent_nominal_to_rms(1.4)],
    [analysis.percent_nominal_to_rms(1.1), analysis.percent_nominal_to_rms(1.8)],
]

# def check_ranges(segment: np.ndarray):
#     ranges = mauka_native.ranges(list(segment), IEEE_1159_TOLERANCE_RANGES)



def ieee1159_voltage(mauka_message: protobuf.mauka_pb2.MaukaMessage, rms_features: np.ndarray,
                     opq_mongo_client: mongo.OpqMongoClient = None) -> typing.List[int]:
    """
    Calculate the ieee1159 voltage incidents and add them to the mongo database
    """
    # incidents, cycle_offsets = classify_ieee1159_voltage(rms_features)
    incident_ids = []
    segments = analysis.segment_array(rms_features)

    for idx, segment in enumerate(segments):
        ranges = mauka_native.ranges(list(segment), IEEE_1159_TOLERANCE_RANGES)



        # incident_id = mongo.store_incident(
        #     mauka_message.payload.event_id,
        #     mauka_message.payload.box_id,
        #     mauka_message.payload.start_timestamp_ms + analysis.c_to_ms(start_idx),
        #     mauka_message.payload.start_timestamp_ms + analysis.c_to_ms(end_idx),
        #     mongo.IncidentMeasurementType.VOLTAGE,
        #     max_deviation,
        #     [incident],
        #     [],
        #     {},
        #     opq_mongo_client
        # )
        #
        # incident_ids.append(incident_id)

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
            incident_ids = ieee1159_voltage(mauka_message,
                                            protobuf.pb_util.repeated_as_ndarray(
                                                mauka_message.payload.data
                                            ),
                                            self.mongo_client)
            for incident_id in incident_ids:
                # Produce a message to the GC
                self.produce(Routes.laha_gc, protobuf.pb_util.build_gc_update(self.name,
                                                                              protobuf.mauka_pb2.INCIDENTS,
                                                                              incident_id))

        else:
            self.logger.error("Received incorrect mauka message [%s] at IticPlugin",
                              protobuf.pb_util.which_message_oneof(mauka_message))

if __name
