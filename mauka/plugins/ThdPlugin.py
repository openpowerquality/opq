"""
This plugin calculates total harmonic distortion (THD) over waveforms.
"""
import math
import multiprocessing
import threading
import typing

import constants
import mongo.mongo
import plugins.base

import numpy
import scipy.fftpack


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

    def sq(self, num: float) -> float:
        """
        Squares a number
        :param num: Number to square
        :return: Squared number
        """
        return num * num

    def closest_idx(self, array: numpy.ndarray, val: float) -> int:
        """
        Finds the index in a sorted array whose value is closest to the value we are searching for "val".
        :param array: The array to search through.
        :param val: The value that we want to compare to each element.
        :return: The index of the closest value to val.
        """
        return numpy.argmin(numpy.abs(array - val))

    def thd(self, waveform: numpy.ndarray) -> float:
        """
        Calculated THD by first taking the FFT and then taking the peaks of the harmonics (sans the fundamental).
        :param waveform:
        :return:
        """
        y = scipy.fftpack.fft(waveform)
        x = numpy.fft.fftfreq(y.size, 1 / constants.SAMPLE_RATE_HZ)

        new_x = []
        new_y = []
        for i in range(len(x)):
            if x[i] >= 0:
                new_x.append(x[i])
                new_y.append(y[i])

        new_x = numpy.array(new_x)
        new_y = numpy.abs(numpy.array(new_y))

        nth_harmonic = {
            1: new_y[self.closest_idx(new_x, 60.0)],
            2: new_y[self.closest_idx(new_x, 120.0)],
            3: new_y[self.closest_idx(new_x, 180.0)],
            4: new_y[self.closest_idx(new_x, 240.0)],
            5: new_y[self.closest_idx(new_x, 300.0)],
            6: new_y[self.closest_idx(new_x, 360.0)],
            7: new_y[self.closest_idx(new_x, 420.0)]
        }

        top = self.sq(nth_harmonic[2]) + self.sq(nth_harmonic[3]) + self.sq(nth_harmonic[4]) + self.sq(nth_harmonic[5])
        _thd = (math.sqrt(top) / nth_harmonic[1]) * 100.0
        return _thd

    def perform_thd_calculation(self, event_id: int):
        """
        Extract waveforms associated with event_id, perform thd calculations, and store resulds back to data base.
        :param event_id: Event id that we are getting waveforms from.
        """
        event_data = mongo.mongo.load_event(event_id, self.mongo_client)
        for device_data in event_data["event_data"]:
            if "data" in device_data and "thd" not in device_data:
                try:
                    box_id = device_data["box_id"]
                    waveform = self.calibrate_waveform(device_data["data"], constants.get_calibration_constant(box_id))
                    thd = self.thd(waveform)
                    document_id = device_data["_id"]
                    self.logger.debug("Calculated THD for " + str(event_id) + ":" + str(box_id))
                    self.mongo_client.data_collection.update_one({'_id': self.object_id(document_id)},
                                                                 {"$set": {"thd": thd}})
                except Exception as e:
                    print(e.message)
                    continue

    def on_message(self, topic, message):
        """
        Fired when this plugin receives a message. This will wait a certain amount of time to make sure that data
        is in the database before starting thd calculations.
        :param topic: Topic of the message.
        :param message: Contents of the message.
        """
        event_id = int(message)
        print(topic, message)
        timer = threading.Timer(self.get_data_after_s, self.perform_thd_calculation, (event_id,))
        timer.start()