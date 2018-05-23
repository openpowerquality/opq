"""
This plugin calculates total harmonic distortion (THD) over waveforms.
"""
import math
import multiprocessing
import pickle
import typing

import numpy
import scipy.fftpack

import constants
import mongo
import plugins.base


def rolling_window(a, window):
    shape = a.shape[:-1] + (a.shape[-1] - window + 1, window)
    strides = a.strides + (a.strides[-1],)
    return numpy.lib.stride_tricks.as_strided(a, shape=shape, strides=strides)


def sq(num: float) -> float:
    """
    Squares a number
    :param num: Number to square
    :return: Squared number
    """
    return num * num


def closest_idx(array: numpy.ndarray, val: float) -> int:
    """
    Finds the index in a sorted array whose value is closest to the value we are searching for "val".
    :param array: The array to search through.
    :param val: The value that we want to compare to each element.
    :return: The index of the closest value to val.
    """
    return numpy.argmin(numpy.abs(array - val))


def thd(waveform: numpy.ndarray) -> float:
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
        1: new_y[closest_idx(new_x, 60.0)],
        2: new_y[closest_idx(new_x, 120.0)],
        3: new_y[closest_idx(new_x, 180.0)],
        4: new_y[closest_idx(new_x, 240.0)],
        5: new_y[closest_idx(new_x, 300.0)],
        6: new_y[closest_idx(new_x, 360.0)],
        7: new_y[closest_idx(new_x, 420.0)]
    }

    top = sq(nth_harmonic[2]) + sq(nth_harmonic[3]) + sq(nth_harmonic[4]) + sq(nth_harmonic[5])
    _thd = (math.sqrt(top) / nth_harmonic[1]) * 100.0
    return _thd


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
        super().__init__(config, ["Waveform", "ThdRequestEvent"], ThdPlugin.NAME, exit_event)
        self.threshold_percent = float(self.config_get("plugins.ThdPlugin.threshold.percent"))
        self.sliding_window_ms = float(self.config_get("plugins.ThdPlugin.window.size.ms"))

    def sliding_thd(self, event_id: int, box_id: str, waveform: numpy.ndarray):
        window_size = int(constants.SAMPLE_RATE_HZ * (self.sliding_window_ms / 1000.0))
        windows = rolling_window(waveform, window_size)
        thds = numpy.apply_along_axis(thd, 1, windows)

        prev_beyond_threshold = False
        prev_idx = -1
        for i in range(len(thds)):
            if thds[i] > self.threshold_percent:
                # We only care if this is the start of a new anomaly
                if not prev_beyond_threshold:
                    prev_idx = i
                    prev_beyond_threshold = True
            else:
                # We only care if this is the end of an anomaly
                if prev_beyond_threshold:
                    self.debug("Found anomaly.")
                    anomaly = mongo.make_anomaly_document(event_id,                                 # Event id
                                                          box_id,                                   # box id
                                                          mongo.BoxEventType.THD.value,              # Event name
                                                          "unknown",                                # Location
                                                          0,                                        # Start ts ms
                                                          0,                                        # End ts ms
                                                          0,                                        # Duration ms
                                                          prev_idx,                                 # Start idx
                                                          i,                                        # End idx
                                                          {"min": numpy.min(thds[prev_idx:i]),      # Other fields
                                                           "max": numpy.max(thds[prev_idx:i]),
                                                           "avg": numpy.average(thds[prev_idx:i])})
                    self.mongo_client.anomalies_collection.insert_one(anomaly)
                    prev_beyond_threshold = False

    def on_message(self, topic, message):
        """
        Fired when this plugin receives a message. This will wait a certain amount of time to make sure that data
        is in the database before starting thd calculations.
        :param topic: Topic of the message.
        :param message: Contents of the message.
        """
        event_id, box_id, waveform = pickle.loads(message)
        self.debug("Calculating THD for event {} and box {} with waveform of len {}".format(event_id, box_id,
                                                                                                       len(waveform)))
        self.sliding_thd(event_id, box_id, waveform)

