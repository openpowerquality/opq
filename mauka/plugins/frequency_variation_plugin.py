"""
This plugin detects, classifies, and stores frequency variation incidents.
Frequency variations are classified as +/-0.10hz as specified by IEEE standards
"""
import multiprocessing
import typing

import numpy

import config
import constants
import plugins.base_plugin
from plugins.routes import Routes
import protobuf.mauka_pb2
import protobuf.pb_util
import mongo






class FrequencyVariationPlugin(plugins.base_plugin.MaukaPlugin):
    """
    Mauka plugin that classifies and stores frequency variation incidents for any event that includes a raw waveform
    """
    NAME = "FrequencyVariationPlugin"

    def __init__(self, conf: config.MaukaConfig, exit_event: multiprocessing.Event):
        """
        Initializes this plugin
        :param conf: Mauka configuration
        :param exit_event: Exit event that can disable this plugin from parent process
        """
        super().__init__(conf, [Routes.windowed_frequency], FrequencyVariationPlugin.NAME, exit_event)
        self.freq_var_low = float(self.config.get("plugins.FrequencyVariationPlugin.frequency.variation.threshold.low"))
        self.freq_var_high = float(self.config.get(
            "plugins.FrequencyVariationPlugin.frequency.variation.threshold.high"))

    def on_message(self, topic, mauka_message):
        """
        Called async when a topic this plugin subscribes to produces a message
        :param topic: The topic that is producing the message
        :param mauka_message: The message that was produced
        """
        self.debug("{} on_message".format(topic))
        if protobuf.pb_util.is_payload(mauka_message, protobuf.mauka_pb2.FREQUENCY_WINDOWED):
            self.debug("on_message {}:{} len:{}".format(mauka_message.payload.event_id,
                                                        mauka_message.payload.box_id,
                                                        len(mauka_message.payload.data)))

            incident_ids = []

            for incident_id in incident_ids:
                # Produce a message to the GC
                self.produce(Routes.laha_gc, protobuf.pb_util.build_gc_update(self.name,
                                                                              protobuf.mauka_pb2.INCIDENTS,
                                                                              incident_id))
        else:
            self.logger.error("Received incorrect mauka message [%s] at FrequencyVariationPlugin",
                              protobuf.pb_util.which_message_oneof(mauka_message))



