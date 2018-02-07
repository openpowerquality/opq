"""
This plugin calculates the ITIC region of a voltage, duration pair.
"""
import typing
import multiprocessing
import threading

import numpy

import analysis.itic
import constants
import mongo.mongo
import plugins.base


class IticPlugin(plugins.base.MaukaPlugin):
    """
    Mauka plugin that calculates ITIC for any event that includes a raw waveform
    """
    NAME = "IticPlugin"

    def __init__(self, config: typing.Dict, exit_event: multiprocessing.Event):
        """
        Initializes this plugin
        :param config: Configuration dictionary
        :param exit_event: Exit event
        """
        super().__init__(config, ["RequestDataEvent", "IticRequestEvent"], IticPlugin.NAME, exit_event)
        self.get_data_after_s = self.config["plugins.IticPlugin.getDataAfterS"]

    def itic(self, waveform: numpy.ndarray) -> str:
        """
        Returns the ITIC region as a string given a waveform.
        :param waveform: The waveform to measure.
        :return: ITIC region name for specified waveform
        """
        vrms_vals = self.vrms_waveform(waveform)
        duration_ms = (len(waveform) / constants.SAMPLE_RATE_HZ) * 1000
        vrms_min = numpy.min(vrms_vals)
        vrms_max = numpy.max(vrms_vals)

        if numpy.abs(vrms_min - 120.0) > numpy.abs(vrms_max - 120.0):
            return analysis.itic.itic_region(vrms_min, duration_ms).name
        else:
            return analysis.itic.itic_region(vrms_max, duration_ms).name

    def perform_itic_calculations(self, event_id: int):
        """
        Called on a timer in a separate thread to allow raw data to be acquired first by makai.
        When raw waveforms are found, ITIC calculations are performed and the result is stored back to box_events
        collection.
        :param event_id: Event id to calculate itic over.
        """
        try:
            box_events = self.mongo_client.box_events_collection.find({"event_id": event_id})
            for box_event in box_events:
                _id = self.object_id(box_event["_id"])
                box_id = box_event["box_id"]
                waveform = mongo.mongo.get_waveform(self.mongo_client, box_event["data_fs_filename"])
                calibrated_waveform = self.calibrate_waveform(waveform, constants.cached_calibration_constant(box_id))
                itic_region_str = self.itic(calibrated_waveform)

                self.mongo_client.box_events_collection.update_one({"_id": _id},
                                                                   {"$set": {"itic": itic_region_str}})

                self.logger.debug("Calculated ITIC for " + str(event_id) + ":" + str(box_id) + ":" + itic_region_str)
        except Exception as e:
            self.logger.error("Error performing itic calculation: " + str(e))
            pass

    def on_message(self, topic, message):
        """
        Called async when a topic this plugin subscribes to produces a message
        :param topic: The topic that is producing the message
        :param message: The message that was produced
        """
        event_id = int(message)
        timer = threading.Timer(self.get_data_after_s, self.perform_itic_calculations, (event_id,))
        timer.start()
