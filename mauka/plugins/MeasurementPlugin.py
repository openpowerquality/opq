import mongo.mongo
import plugins.base


def run_plugin(config):
    plugins.base.run_plugin(MeasurementPlugin, config)


class MeasurementPlugin(plugins.base.MaukaPlugin):
    def __init__(self, config):
        super().__init__(config, ["measurement"], "MeasurementPlugin")
        self.sample_every = self.config_get("plugins.MeasurementPlugin.sample_every")
        self.measurements_collection = self.mongo_client.db[mongo.mongo.Collection.MEASUREMENTS]
        self.device_id_to_sample_cnt = {}

        self.init_measurements_collection()

    def init_measurements_collection(self):
        self.measurements_collection.create_index("device_id")
        self.measurements_collection.create_index("timestamp_ms")

    def on_message(self, topic, message):
        measurement = plugins.base.protobuf_decode_measurement(message)
        device_id = measurement.id

        if device_id not in self.device_id_to_sample_cnt:
            self.device_id_to_sample_cnt[device_id] = 0;

        if self.device_id_to_sample_cnt[device_id] == (self.sample_every - 1):
            # print("{} {} {}".format(device_id, measurement.rms, measurement.frequency))
            self.device_id_to_sample_cnt[device_id] = 0
            measurement = {
                "device_id": device_id,
                "timestamp_ms": measurement.time,
                "frequency": measurement.frequency,
                "voltage": measurement.rms
            }
            # print(measurement)
            self.measurements_collection.insert_one(measurement)

        self.device_id_to_sample_cnt[device_id] += 1
