import datetime
import mongo.mongo
import plugins.base
import plugins.ThresholdPlugin


def run_plugin(config):
    plugins.base.run_plugin(VoltageThresholdPlugin, config)


def extract_voltage(measurement):
    return measurement.rms


class VoltageThresholdPlugin(plugins.ThresholdPlugin.ThresholdPlugin):
    def __init__(self, config):
        super().__init__(config, "VoltageThresholdPlugin")
        self.voltage_ref = self.config_get("plugins.ThresholdPlugin.voltage.ref")
        self.voltage_percent_low = self.config_get("plugins.ThresholdPlugin.voltage.threshold.percent.low")
        self.voltage_percent_high = self.config_get("plugins.ThresholdPlugin.voltage.threshold.percent.high")
        self.subscribe_threshold(extract_voltage, self.voltage_ref, self.voltage_percent_low, self.voltage_percent_high)

    def on_event(self, threshold_event):
        type = threshold_event.threshold_type

        if type =="LOW":
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
