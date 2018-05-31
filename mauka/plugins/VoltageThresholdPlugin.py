"""
This module contains the voltage threshold plugin which is responsible for classifying voltage dips and swells
"""

import multiprocessing
import typing

import mongo
import plugins.ThresholdPlugin
import protobuf.util


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
        threshold_type = threshold_event.threshold_type

        if threshold_type == "LOW":
            event_type = mongo.BoxEventType.VOLTAGE_DIP.value
        elif threshold_type == "HIGH":
            event_type = mongo.BoxEventType.VOLTAGE_SWELL.value
        else:
            self.logger.error("Unknown threshold type {}".format(threshold_type))
            return

        # event = {"eventStart": threshold_event.start,
        #          "eventEnd": threshold_event.end,
        #          "eventType": event_type,
        #          "percent": threshold_event.max_value,
        #          "deviceId": threshold_event.device_id}
        # self.logger.info("Event: {}".format(str(event)))
        # self.produce("VoltageEvent".encode(), self.to_json(event).encode())
        makai_trigger = protobuf.util.build_makai_trigger(
            self.name,
            threshold_event.start,
            threshold_event.end,
            event_type,
            threshold_event.max_value,
            threshold_event.device_id
        )
        mauka_message_bytes = protobuf.util.serialize_mauka_message(makai_trigger)
        self.produce("VoltageEvent".encode(), mauka_message_bytes)
