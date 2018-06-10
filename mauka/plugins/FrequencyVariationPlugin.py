"""
This plugin detects, classifies, and stores frequency variation incidents.
Frequency variations are classified as +/-0.10hz as specified by IEEE standards
"""
import typing
import multiprocessing
import numpy
import constants
import plugins.base
import protobuf.mauka_pb2
import protobuf.util

class FrequencyVariationPlugin(plugins.base.MaukaPlugin):
    """
    Mauka plugin that classifies and stores frequency variation incidents for any event that includes a raw waveform
    """
    NAME = "FrequencyVariationPlugin"

    def __init__(self, config: typing.Dict, exit_event: multiprocessing.Event):
        """
        Initializes this plugin
        :param config: Mauka configuration
        :param exit_event: Exit event that can disable this plugin from parent process
        """
        super().__init__(config, ["WindowedFrequency"], FrequencyVariationPlugin.NAME, exit_event)
        self.freq_ref = float(self.config_get("plugins.FrequencyVariationPlugin.frequency.ref"))
        self.freq_var_low = float(self.config_get("plugins.FrequencyVariationPlugin.frequency.variation.threshold.low"))
        self.freq_var_high = float(self.config_get("plugins.FrequencyVariationPlugin.frequency.variation.threshold.high"))

    def on_message(self, topic, mauka_message):
        """
        Called async when a topic this plugin subscribes to produces a message
        :param topic: The topic that is producing the message
        :param message: The message that was produced
        """
        self.debug("on_message")
        if protobuf.util.is_payload(mauka_message, protobuf.mauka_pb2.VOLTAGE_RMS_WINDOWED):
           """TODO"""
        else:
            self.logger.error("Received incorrect mauka message [{}] at FrequencyVariationPlugin".format(
                protobuf.util.which_message_oneof(mauka_message)
            ))
