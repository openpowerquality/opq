"""
This module contains the frequency threshold plugin which is responsible for classifying frequency dips and swells
"""

import multiprocessing
import typing

import mongo
import plugins.threshold_plugin
import protobuf.util
import protobuf.mauka_pb2


def extract_frequency(measurement: protobuf.mauka_pb2.Measurement) -> float:
    """Extracts the frequency value from the TriggeringMessage

    :param measurement: Deserialized triggering message instance
    :return: The frequency value
    """
    return measurement.frequency


class FrequencyThresholdPlugin(plugins.threshold_plugin.ThresholdPlugin):
    """
    This class contains the frequency threshold plugin which is responsible for classifying frequency dips and swells
    """

    NAME = "FrequencyThresholdPlugin"

    def __init__(self, config: typing.Dict, exit_event: multiprocessing.Event):
        """Initializes this plugin

        :param config: Configuration dictionary
        """
        super().__init__(config, FrequencyThresholdPlugin.NAME, exit_event)

        self.frequency_ref = float(self.config_get("plugins.ThresholdPlugin.frequency.ref"))
        """Reference frequency (steady state)"""

        self.frequency_percent_low = float(self.config_get("plugins.ThresholdPlugin.frequency.threshold.percent.low"))
        """Percent below reference that is the low threshold"""

        self.frequency_percent_high = float(self.config_get("plugins.ThresholdPlugin.frequency.threshold.percent.high"))
        """Percent above reference that is the high threshold"""

        self.subscribe_threshold(extract_frequency, self.frequency_ref, self.frequency_percent_low,
                                 self.frequency_percent_high)

    def on_event(self, threshold_event):
        """Called when base plugin records a complete threshold event.

        This will produce a FrequencyEvent message to the system.

        :param threshold_event: The recorded event
        """
        threshold_type = threshold_event.threshold_type

        if threshold_type == "LOW":
            event_type = mongo.BoxEventType.FREQUENCY_DIP.value
        elif threshold_type == "HIGH":
            event_type = mongo.BoxEventType.FREQUENCY_SWELL.value
        else:
            self.logger.error("Unknown threshold type %s", threshold_type)
            return

        makai_trigger = protobuf.util.build_makai_trigger(
            self.name,
            threshold_event.start,
            threshold_event.end,
            event_type,
            threshold_event.max_value,
            threshold_event.device_id
        )
        self.produce("FrequencyEvent", makai_trigger)
