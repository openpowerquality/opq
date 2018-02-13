"""
This plugin calculates total harmonic distortion (THD) over waveforms.
"""
import multiprocessing
import threading
import typing

import analysis.thd
import constants
import mongo.mongo
import plugins.base


class ThdPlugin(plugins.base.MaukaPlugin):
    """
    Mauka plugin that calculates THD over raw waveforms.
    """
    NAME = "ThdPlugin"

    def __init__(self, config: typing.Dict, exit_event: multiprocessing.Event):
        """
        Initializes this plugin
        :param config: Mauka configuration
        :param exit_event: Exit event that can disable this plugin from parent process
        """
        super().__init__(config, ["RequestDataEvent", "ThdRequestEvent"], ThdPlugin.NAME, exit_event)
        self.get_data_after_s = self.config["plugins.ThdPlugin.getDataAfterS"]


    def perform_thd_calculation(self, event_id: int):
        """
        Extract waveforms associated with event_id, perform thd calculations, and store results back to mongodb.
        :param event_id: Event to calculate THD for.
        """
        try:
            box_events = self.mongo_client.box_events_collection.find({"event_id": event_id})
            for box_event in box_events:
                _id = self.object_id(box_event["_id"])
                box_id = box_event["box_id"]
                waveform = mongo.mongo.get_waveform(self.mongo_client, box_event["data_fs_filename"])
                calibrated_waveform = self.calibrate_waveform(waveform, constants.cached_calibration_constant(box_id))
                thd = analysis.thd.thd(calibrated_waveform)

                self.mongo_client.box_events_collection.update_one({"_id": _id},
                                                        {"$set": {"thd": thd}})

                self.logger.debug("Calculated THD for " + str(event_id) + ":" + str(box_id) + ":" + str(thd))
        except Exception as e:
            self.logger.error("Error performing THD calculation: " + str(e))
            pass

    def on_message(self, topic, message):
        """
        Fired when this plugin receives a message. This will wait a certain amount of time to make sure that data
        is in the database before starting thd calculations.
        :param topic: Topic of the message.
        :param message: Contents of the message.
        """
        event_id = int(message)
        timer = threading.Timer(self.get_data_after_s, self.perform_thd_calculation, (event_id,))
        timer.start()
