"""
This module contains the voltage threshold plugin which is responsible for classifying voltage dips and swells
"""

import datetime
import multiprocessing
import typing

import mongo.mongo
import plugins.ThresholdPlugin


def extract_voltage(measurement) -> float:
    """Extracts the voltage value from the TriggeringMessage

    :param measurement: Deserialized triggering message instance
    :return: The voltage rms value
    """
    return measurement.rms


class VoltageThresholdPlugin(plugins.ThresholdPlugin.ThresholdPlugin):
    """
    This module contains the voltage threshold plugin which is responsible for classifying voltage dips and swells
    """

    NAME = "VoltageThresholdPlugin"

    def __init__(self, config: typing.Dict, exit_event: multiprocessing.Event):
        """Initializes this plugin

        :param config: Configuration dictionary
        """
        super().__init__(config, VoltageThresholdPlugin.NAME, exit_event)

        self.voltage_ref = float(self.config_get("plugins.ThresholdPlugin.voltage.ref"))
        """Reference frequency (steady state)"""

        self.voltage_percent_low = float(self.config_get("plugins.ThresholdPlugin.voltage.threshold.percent.low"))
        """Percent below reference that is the low threshold"""

        self.voltage_percent_high = float(self.config_get("plugins.ThresholdPlugin.voltage.threshold.percent.high"))
        """Percent above reference that is the high threshold"""

        self.subscribe_threshold(extract_voltage, self.voltage_ref, self.voltage_percent_low, self.voltage_percent_high)

    def on_event(self, threshold_event):
        """Called when base plugin records a complete threshold event.

        This will produce a VoltageEvent message to the system.

        :param threshold_event: The recorded event
        """
        type = threshold_event.threshold_type

        if type == "LOW":
            event_type = mongo.mongo.BoxEventType.VOLTAGE_DIP
        elif type == "HIGH":
            event_type = mongo.mongo.BoxEventType.VOLTAGE_SWELL
        else:
            print("Unknown threshold type", type)
            return

        voltage_event = {"eventStart": datetime.datetime.utcfromtimestamp(threshold_event.start / 1000.0),
                         "eventEnd": datetime.datetime.utcfromtimestamp(threshold_event.end / 1000.0),
                         "eventType": event_type,
                         "percent": threshold_event.max_value,
                         "deviceId": threshold_event.device_id}

        event_id = self.box_events_collection.insert_one(voltage_event).inserted_id

        self.produce("VoltageEvent".encode(), self.to_json({"eventStart": threshold_event.start,
                                                            "eventEnd": threshold_event.end,
                                                            "eventType": event_type,
                                                            "percent": threshold_event.max_value,
                                                            "deviceId": threshold_event.device_id,
                                                            "eventId": event_id}).encode())
