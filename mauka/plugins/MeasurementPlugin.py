"""
This module contains the measurement plugin which stores triggering message measurements
"""

import multiprocessing
import protobuf.util
import typing

import mongo
import plugins.base


class MeasurementPlugin(plugins.base.MaukaPlugin):
    """
    This class contains the measurement plugin which stores triggering message measurements
    """

    NAME = "MeasurementPlugin"

    def __init__(self, config: typing.Dict, exit_event: multiprocessing.Event):
        """ Initializes this plugin

        :param config: Configuration dictionary
        """
        super().__init__(config, ["measurement"], MeasurementPlugin.NAME, exit_event)

        self.sample_every = int(self.config_get("plugins.MeasurementPlugin.sample_every"))
        """Of all the triggering messages, how often should we sample values from the stream"""

        self.measurements_collection = self.mongo_client.db[mongo.Collection.MEASUREMENTS]
        """Mongo OPQ measurements collection"""

        self.device_id_to_sample_cnt = {}
        """For each device, store how many samples its received"""

        self.device_id_to_total_cnts = {}

        self.init_measurements_collection()

    def init_measurements_collection(self):
        """
        Make sure proper indexes are setup for measurements
        """
        self.measurements_collection.create_index("device_id")
        self.measurements_collection.create_index("timestamp_ms")

    def get_status(self):
        return str(self.device_id_to_total_cnts)

    def on_message(self, topic, message):
        """Subscribed messages occur async

        Messages are stored in mongo based on the sampling rate

        :param topic: The topic that this message is associated with
        :param message: The message
        """
        measurement = protobuf.util.decode_trigger_message(message)
        device_id = measurement.id

        if device_id not in self.device_id_to_sample_cnt:
            self.device_id_to_sample_cnt[device_id] = 0

        if device_id not in self.device_id_to_total_cnts:
            self.device_id_to_total_cnts[device_id] = 0

        if self.device_id_to_sample_cnt[device_id] == (self.sample_every - 1):
            self.device_id_to_sample_cnt[device_id] = 0
            measurement_dict = {
                "box_id": str(device_id),
                "timestamp_ms": measurement.time,
                "frequency": measurement.frequency,
                "voltage": measurement.rms
            }

            if measurement.HasField("thd"):
                measurement_dict["thd"] = measurement.thd

            self.measurements_collection.insert_one(measurement_dict)

        self.device_id_to_sample_cnt[device_id] += 1
        self.device_id_to_total_cnts[device_id] += 1
