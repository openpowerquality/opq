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

def get_x(size):
    return numpy.fft.fftfreq(size, 1 / constants.SAMPLE_RATE_HZ)

def memoize(fn):
    state = {}

    def memo(v):
        if v not in state:
            state[v] = fn(v)
        return state[v]

    return memo


memoized_get_x = memoize(get_x)

def thd(waveform: numpy.ndarray) -> float:
    """
    Calculated THD by first taking the FFT and then taking the peaks of the harmonics (sans the fundamental).
    :param waveform:
    :return:
    """
    y = numpy.abs(scipy.fftpack.fft(waveform))
    # x = numpy.fft.fftfreq(y.size, 1 / constants.SAMPLE_RATE_HZ)
    x = memoized_get_x(y.size)
    # print(x)
    #
    # new_x = []
    # new_y = []
    # for i in range(len(x)):
    #     # print(x[i])
    #     if x[i] >= 0:
    #         new_x.append(x[i])
    #         new_y.append(y[i])
    #
    # new_x = numpy.array(new_x)
    # new_y = numpy.abs(y)
    # print(y.size, new_y.size)
    # print(closest_idx(x, 60.0))
    # print(closest_idx(x, 120.0))
    # print(closest_idx(x, 180.0))
    # print(closest_idx(x, 240.0))
    # print(closest_idx(x, 300.0))
    # print(closest_idx(x, 360.0))
    # print(closest_idx(x, 420.0))

    nth_harmonic = {
        1: y[closest_idx(x, 60.0)],
        2: y[closest_idx(x, 120.0)],
        3: y[closest_idx(x, 180.0)],
        4: y[closest_idx(x, 240.0)],
        5: y[closest_idx(x, 300.0)],
        6: y[closest_idx(x, 360.0)],
        7: y[closest_idx(x, 420.0)]
    }

    # nth_harmonic = {
    #     1: y[12],
    #     2: y[24],
    #     3: y[36],
    #     4: y[48],
    #     5: y[60],
    #     6: y[72],
    #     7: y[84]
    # }

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
        self.debug("sliding thd A")
        window_size = int(constants.SAMPLE_RATE_HZ * (self.sliding_window_ms / 1000.0))
        windows = rolling_window(waveform, window_size)
        self.debug("sliding thd B")
        thds = numpy.apply_along_axis(thd, 1, windows)
        self.debug("sliding thd C")
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
                    anomaly = mongo.make_anomaly_document(event_id,  # Event id
                                                          box_id,  # box id
                                                          mongo.BoxEventType.THD.value,  # Event name
                                                          "unknown",  # Location
                                                          0,  # Start ts ms
                                                          0,  # End ts ms
                                                          0,  # Duration ms
                                                          prev_idx,  # Start idx
                                                          i,  # End idx
                                                          {"min": numpy.min(thds[prev_idx:i]),  # Other fields
                                                           "max": numpy.max(thds[prev_idx:i]),
                                                           "avg": numpy.average(thds[prev_idx:i])})
                    self.mongo_client.anomalies_collection.insert_one(anomaly)
                    prev_beyond_threshold = False
        self.debug("sliding thd D")

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


###### Testing
def sliding_thd(event_id: int, box_id: str, waveform: numpy.ndarray):
    print("a")
    window_size = int(constants.SAMPLE_RATE_HZ * (200 / 1000.0))
    windows = rolling_window(waveform, window_size)
    print("b")
    # thds = numpy.apply_along_axis(thd, 1, windows)
    thds = [thd(w) for w in windows]
    # vthd = numpy.vectorize(thd)
    # thds = vthd(windows)
    print("c")
    prev_beyond_threshold = False
    prev_idx = -1
    for i in range(len(thds)):
        if thds[i] > 5.0:
            # We only care if this is the start of a new anomaly
            if not prev_beyond_threshold:
                prev_idx = i
                prev_beyond_threshold = True
        else:
            # We only care if this is the end of an anomaly
            if prev_beyond_threshold:
                anomaly = mongo.make_anomaly_document(event_id,  # Event id
                                                      box_id,  # box id
                                                      mongo.BoxEventType.THD.value,  # Event name
                                                      "unknown",  # Location
                                                      0,  # Start ts ms
                                                      0,  # End ts ms
                                                      0,  # Duration ms
                                                      prev_idx,  # Start idx
                                                      i,  # End idx
                                                      {"min": numpy.min(thds[prev_idx:i]),  # Other fields
                                                       "max": numpy.max(thds[prev_idx:i]),
                                                       "avg": numpy.average(thds[prev_idx:i])})
                print(anomaly)
                # self.mongo_client.anomalies_collection.insert_one(anomaly)
                prev_beyond_threshold = False

    return thds


import math


class WaveformGenerator:
    def __init__(self):
        self.amplitude: float = 120.0 * math.sqrt(2)
        self.frequency: float = 60.0
        self.phase: float = 0.0
        self.sample_rate_hz: float = 12000.0
        self.samples_per_cycle: int = 200
        self.generator: typing.Generator[typing.Tuple[int, float]] = self.waveform_gen()

    def waveform_gen(self, start: int = 0):
        i = start
        while True:
            v = self.amplitude * math.sin(self.frequency * (2 * math.pi) * i / self.sample_rate_hz)
            yield (i, v)

            i += 1
            if i == self.samples_per_cycle:
                i = 0

    def next(self) -> typing.Tuple[int, float]:
        return next(self.generator)

    def realize(self, nitems: int):
        return [self.next() for i in range(nitems)]


def extract_waveform(tuple2: typing.Tuple[int, float]) -> float:
    return tuple2[1]


import time

if __name__ == "__main__":
    gen = WaveformGenerator()
    # 10 sec of waveform
    print("warmup")
    # waveform = numpy.array(list(map(extract_waveform, gen.realize(12000 * 60 * 10))))
    waveform = numpy.array(list(map(extract_waveform, gen.realize(12000 * 5))))
    print("start")
    start = time.time()
    v = sliding_thd(0, "0", waveform)[:100]
    end = time.time()
    print("end", end - start)
    print(v)
