"""
This module contains the frequency threshold plugin which is responsible for classifying frequency dips and swells
"""

import datetime
import typing

import mongo.mongo
import plugins.base
import plugins.ThresholdPlugin


def run_plugin(config: typing.Dict):
    """Runs this plugin using the given configuration

    :param config: Configuration dictionary
    """
    plugins.base.run_plugin(FrequencyThresholdPlugin, config)


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
    def __init__(self, config: typing.Dict):
        """Initializes this plugin

        :param config: Configuration dictionary
        """
        super().__init__(config, "FrequencyThresholdPlugin")

        self.frequency_ref = self.config_get("plugins.ThresholdPlugin.frequency.ref")
        """Reference frequency (steady state)"""

        self.frequency_percent_low = self.config_get("plugins.ThresholdPlugin.frequency.threshold.percent.low")
        """Percent below reference that is the low threshold"""

        self.frequency_percent_high = self.config_get("plugins.ThresholdPlugin.frequency.threshold.percent.high")
        """Percent above reference that is the high threshold"""

        self.subscribe_threshold(extract_frequency, self.frequency_ref, self.frequency_percent_low,
                                 self.frequency_percent_high)

    def on_event(self, threshold_event):
        """Called when base plugin records a complete threshold event.

        This will produce a FrequencyEvent message to the system.

        :param threshold_event: The recorded event
        """
        type = threshold_event.threshold_type

        if type =="LOW":
            event_type = mongo.mongo.BoxEventType.FREQUENCY_DIP
        elif type == "HIGH":
            event_type = mongo.mongo.BoxEventType.FREQUENCY_SWELL
        else:
            print("Unknown threshold type", type)
            return

        frequency_event = {"eventStart": datetime.datetime.utcfromtimestamp(threshold_event.start),
                           "eventEnd": datetime.datetime.utcfromtimestamp(threshold_event.end),
                           "eventType": event_type,
                           "percent": threshold_event.max_value,
                           "deviceId": threshold_event.device_id}

        event_id = self.box_events_collection.insert_one(frequency_event).inserted_id

        self.produce("FrequencyEvent".encode(), self.to_json({"eventStart": threshold_event.start,
                                                              "eventEnd": threshold_event.end,
                                                              "eventType": event_type,
                                                              "percent": threshold_event.max_value,
                                                              "deviceId": threshold_event.device_id,
                                                              "eventId": event_id}
                                                             ).encode())