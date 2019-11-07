"""
This plugin calculates total harmonic distortion (THD) over waveforms.
"""
import multiprocessing
import typing

import mauka_native_py

import config
import constants
import mongo
import log
import plugins.base_plugin
from plugins.routes import Routes
import protobuf.mauka_pb2
import protobuf.pb_util


def thd(mauka_message: protobuf.mauka_pb2.MaukaMessage,
        opq_mongo_client: mongo.OpqMongoClient,
        thd_plugin: typing.Optional['ThdPlugin'] = None) -> typing.List[int]:
    data: typing.List[float] = list(mauka_message.payload.data)
    log.maybe_debug("Found %d Vrms values." % len(data), thd_plugin)
    incidents = mauka_native_py.classify_rms(mauka_message.payload.start_timestamp_ms, data)
    log.maybe_debug("Found %d Incidents." % len(incidents), thd_plugin)
    incident_ids: typing.List[int] = []
    pass


class ThdPlugin(plugins.base_plugin.MaukaPlugin):
    """
    Mauka plugin that calculates THD over raw waveforms.
    """
    NAME = "ThdPlugin"

    def __init__(self, conf: config.MaukaConfig, exit_event: multiprocessing.Event):
        """
        Initializes this plugin
        :param conf: Mauka configuration
        :param exit_event: Exit event that can disable this plugin from parent process
        """
        super().__init__(conf, [Routes.adc_samples, Routes.thd_request_event], ThdPlugin.NAME, exit_event)
        self.threshold_percent = float(self.config.get("plugins.ThdPlugin.threshold.percent"))
        self.sliding_window_ms = float(self.config.get("plugins.ThdPlugin.window.size.ms"))

    def on_message(self, topic, mauka_message):
        """
        Fired when this plugin receives a message. This will wait a certain amount of time to make sure that data
        is in the database before starting thd calculations.
        :param topic: Topic of the message.
        :param mauka_message: Contents of the message.
        """
        if protobuf.pb_util.is_payload(mauka_message, protobuf.mauka_pb2.ADC_SAMPLES):
            self.debug("on_message {}:{} len:{}".format(mauka_message.payload.event_id,
                                                        mauka_message.payload.box_id,
                                                        len(mauka_message.payload.data)))
            incident_ids = thd(mauka_message, self.mongo_client, self)

            for incident_id in incident_ids:
                # Produce a message to the GC
                self.produce(Routes.laha_gc, protobuf.pb_util.build_gc_update(self.name,
                                                                              protobuf.mauka_pb2.INCIDENTS,
                                                                              incident_id))
        else:
            self.logger.error("Received incorrect mauka message [%s] at ThdPlugin",
                              protobuf.pb_util.which_message_oneof(mauka_message))
