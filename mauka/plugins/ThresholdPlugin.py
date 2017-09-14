"""
This module contains a base plugin that allows us to check for threshold crossings over time
"""

import collections
import multiprocessing
import typing

import mongo.mongo
import plugins.base

ThresholdEvent = collections.namedtuple("ThresholdEvent", "start "
                                                          "end "
                                                          "device_id "
                                                          "threshold_type "
                                                          "max_value")
"""Define a named tuple for organizing threshold event data"""


class ThresholdPlugin(plugins.base.MaukaPlugin):
    """
    This class contains a base plugin that allows us to check for threshold crossings over time
    """

    NAME = "ThresholdPlugin"

    def __init__(self, config: typing.Dict, name: str, exit_event: multiprocessing.Event):
        """ Initializes this plugin

        :param config: Configuration dictionary
        :param name: Name of the threshold
        """
        super().__init__(config, ["measurement"], name, exit_event)

        self.measurement_value_fn = None
        """Function that extracts measurement value from triggering measurement"""

        self.threshold_ref = None
        """Steady state reference"""

        self.threshold_percent_low = None
        """Low threshold percent"""

        self.threshold_percent_high = None
        """High threshold percent"""

        self.subscribed = False
        """Are we currently monitoring this threshold"""

        self.threshold_value_low = None
        """Low threshold value (calculated from steady state and percent)"""

        self.threshold_value_high = None
        """High threshold value (calculated from steady state and percent)"""

        self.box_events_collection = self.mongo_client.db[mongo.mongo.Collection.BOX_EVENTS]
        """OPQ events collection"""

        self.device_id_to_low_events = {}
        """Device id to current low events"""

        self.device_id_to_high_events = {}
        """Device id to current high events"""

    def subscribe_threshold(self,
                            measurement_value_fn: typing.Callable,
                            threshold_ref: float,
                            threshold_percent_low: float,
                            threshold_percent_high: float):
        """Setup the conditions for checking threshold values based off of steady state and threshold percentages

        :param measurement_value_fn: Function that extracts measurement value from triggering measurement
        :param threshold_ref: Steady state reference
        :param threshold_percent_low: Low threshold percent
        :param threshold_percent_high: High threshold percent
        """
        self.subscribed = True
        self.measurement_value_fn = measurement_value_fn
        self.threshold_ref = threshold_ref
        self.threshold_percent_low = threshold_percent_low
        self.threshold_percent_high = threshold_percent_high
        self.threshold_value_low = self.threshold_ref - (self.threshold_ref * (0.01 * self.threshold_percent_low))
        self.threshold_value_high = self.threshold_ref + (self.threshold_ref * (0.01 * self.threshold_percent_high))

    def open_event(self, start: int, device_id, value: float, is_low_threshold: bool):
        """ Start recording a threshold event

        :param start: Start time of event
        :param device_id: Device id that event is associated with
        :param value: Max magnitude of the event
        :param is_low_threshold: Is this a low or high threshold event?
        :return: Partial event recording
        """
        threshold_type = "LOW" if is_low_threshold else "HIGH"
        event = ThresholdEvent(start,
                               0,
                               device_id,
                               threshold_type,
                               value)

        if is_low_threshold:
            self.device_id_to_low_events[device_id] = event
        else:
            self.device_id_to_high_events[device_id] = event

    def update_event(self, threshold_event, value):
        """Update a threshold event with new information

        :param threshold_event: The event to update
        :param value: The new maximum magnitude value of the event
        :return: The updated event
        """
        event = ThresholdEvent(threshold_event.start,
                               threshold_event.end,
                               threshold_event.device_id,
                               threshold_event.threshold_type,
                               value)

        if event.threshold_type == "LOW":
            self.device_id_to_low_events[event.device_id] = event
        else:
            self.device_id_to_high_events[event.device_id] = event

    def close_event(self, threshold_event, end: int, value=None):
        """Close out an existing threshold event, completing the event

        :param threshold_event: The event to complete
        :param end: The end timestamp
        :param value: The maximum magnitude of the event
        :return: The completed event
        """
        if value is None:
            val = threshold_event.max_value
        else:
            val = value

        event = ThresholdEvent(threshold_event.start,
                               end,
                               threshold_event.device_id,
                               threshold_event.threshold_type,
                               val)

        if event.threshold_type == "LOW":
            del self.device_id_to_low_events[event.device_id]
        else:
            del self.device_id_to_high_events[event.device_id]

        self.on_event(event)

    def on_message(self, topic, message):
        """Subscribed messages occur async

        Messages cause our FSM to be ran and can create new events, update events, and close out events

        :param topic: The topic that this message is associated with
        :param message: The message
        """

        if not self.subscribed:
            pass

        measurement = plugins.base.protobuf_decode_measurement(message)
        device_id = measurement.id
        timestamp_ms = measurement.time
        value = self.measurement_value_fn(measurement)

        is_low = value < self.threshold_value_low
        is_high = value > self.threshold_value_high
        is_stable = not is_low and not is_high

        prev_low_event = self.device_id_to_low_events[device_id] if device_id in self.device_id_to_low_events else None
        prev_high_event = self.device_id_to_high_events[
            device_id] if device_id in self.device_id_to_high_events else None

        # Low to low, update low event
        if is_low and prev_low_event is not None:
            if value < prev_low_event.max_value:
                self.update_event(prev_low_event, value)

        # Low to stable, complete low event, produces event message
        elif is_stable and prev_low_event is not None:
            self.close_event(prev_low_event, timestamp_ms)

        # Low to high, complete low event, start high, produces event message
        elif is_high and prev_low_event is not None:
            self.close_event(prev_low_event, timestamp_ms)
            self.open_event(timestamp_ms, device_id, value, False)

        # Stable to low, start low
        elif is_low and prev_low_event is None:
            self.open_event(timestamp_ms, device_id, value, True)

        # Stable to stable, no problem, move along citizen
        elif is_stable and prev_low_event is None and prev_high_event is None:
            pass

        # Stable to high, start high
        elif is_high and prev_high_event is None:
            self.open_event(timestamp_ms, device_id, value, False)

        # High to low, complete high, start low, produces event message
        elif is_low and prev_high_event is not None:
            self.close_event(prev_high_event, timestamp_ms)
            self.open_event(timestamp_ms, device_id, value, True)

        # High to stable, complete high, produces event message
        elif is_stable and prev_high_event is not None:
            self.close_event(prev_high_event, timestamp_ms)

        # High to high, update high
        elif is_high and prev_high_event is not None:
            if value > prev_high_event.max_value:
                self.update_event(prev_high_event, value)

        else:
            print("Unknown configuration", is_low, is_high, prev_low_event is None, prev_high_event is None)

    def on_event(self, threshold_event):
        """This should be implemented in all child classes and is called async as events are completed

        :param threshold_event: The completed event
        """
        pass
