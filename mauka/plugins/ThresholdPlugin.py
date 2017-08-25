import mongo.mongo
import plugins.base

import collections


def run_plugin(config):
    plugins.base.run_plugin(ThresholdPlugin, config)


ThresholdEvent = collections.namedtuple("ThresholdEvent", "start "
                                                          "end "
                                                          "device_id "
                                                          "threshold_type "
                                                          "max_value")


class ThresholdPlugin(plugins.base.MaukaPlugin):
    def __init__(self, config, name):
        super().__init__(config, ["measurement"], name)
        self.threshold_type = None
        self.measurement_value_fn = None
        self.threshold_ref = None
        self.threshold_percent_low = None
        self.threshold_percent_high = None
        self.subscribed = False
        self.threshold_value_low = None
        self.threshold_value_high = None

        self.box_events_collection = self.mongo_client.db[mongo.mongo.Collection.BOX_EVENTS]

        self.device_id_to_low_events = {}
        self.device_id_to_high_events = {}

    def subscribe_threshold(self,
                            measurement_value_fn, threshold_ref, threshold_percent_low,
                            threshold_percent_high):
        self.subscribed = True
        self.measurement_value_fn = measurement_value_fn
        self.threshold_ref = threshold_ref
        self.threshold_percent_low = threshold_percent_low
        self.threshold_percent_high = threshold_percent_high
        self.threshold_value_low = self.threshold_ref - (self.threshold_ref * (0.01 * self.threshold_percent_low))
        self.threshold_value_high = self.threshold_ref + (self.threshold_ref * (0.01 * self.threshold_percent_high))

    def open_event(self, start, device_id, value, is_low_threshold):
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
        event = ThresholdEvent(threshold_event.start,
                               threshold_event.end,
                               threshold_event.device_id,
                               threshold_event.threshold_type,
                               value)

        if event.threshold_type == "LOW":
            self.device_id_to_low_events[event.device_id] = event
        else:
            self.device_id_to_high_events[event.device_id] = event

    def close_event(self, threshold_event, end, value=None):
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
        pass
