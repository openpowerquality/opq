"""
This module contains the frequency threshold plugin which is responsible for classifying frequency dips and swells
"""

import multiprocessing
import typing

import mongo
import plugins.ThresholdPlugin


def extract_frequency(measurement) -> float:
    """Extracts the frequency value from the TriggeringMessage

    :param measurement: Deserialized triggering message instance
    :return: The frequency value
    """
    return measurement.frequency


class FrequencyThresholdPlugin(plugins.ThresholdPlugin.ThresholdPlugin):
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
        type = threshold_event.threshold_type

        if type == "LOW":
            event_type = mongo.BoxEventType.FREQUENCY_DIP
        elif type == "HIGH":
            event_type = mongo.BoxEventType.FREQUENCY_SWELL
        else:
            self.logger.error("Unknown threshold type {}".format(type))
            return

        event = {"eventStart": threshold_event.start,
                 "eventEnd": threshold_event.end,
                 "eventType": event_type,
                 "percent": threshold_event.max_value,
                 "deviceId": threshold_event.device_id}

        self.logger.info("Event: {}".format(str(event)))
        self.produce("FrequencyEvent".encode(), self.to_json(event).encode())
