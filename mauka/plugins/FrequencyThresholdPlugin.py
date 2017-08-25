import datetime
import mongo.mongo
import plugins.base
import plugins.ThresholdPlugin


def run_plugin(config):
    plugins.base.run_plugin(FrequencyThresholdPlugin, config)


def extract_frequency(measurement):
    return measurement.frequency


class FrequencyThresholdPlugin(plugins.ThresholdPlugin.ThresholdPlugin):
    def __init__(self, config):
        super().__init__(config, "FrequencyThresholdPlugin")
        self.frequency_ref = self.config_get("plugins.ThresholdPlugin.frequency.ref")
        self.frequency_percent_low = self.config_get("plugins.ThresholdPlugin.frequency.threshold.percent.low")
        self.frequency_percent_high = self.config_get("plugins.ThresholdPlugin.frequency.threshold.percent.high")
        self.subscribe_threshold(extract_frequency, self.frequency_ref, self.frequency_percent_low, self.frequency_percent_high)

    def on_event(self, threshold_event):
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