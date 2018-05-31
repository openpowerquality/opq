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
import protobuf.util
import protobuf.mauka_pb2


def rolling_window(a, window):
    if len(a) <= window:
        return numpy.array([a])
    shape = a.shape[:-1] + (a.shape[-1] - window + 1, window)
    strides = a.strides + (a.strides[-1],)
    return numpy.lib.stride_tricks.as_strided(a, shape=shape, strides=strides)

def thd(waveform: numpy.ndarray, fundamental: int) -> float:
    y = numpy.abs(scipy.fftpack.fft(waveform))

    top = numpy.sqrt(numpy.sum(y[i]**2 for i in numpy.arange(2 * fundamental, len(y)//2, fundamental)))
    bottom = y[fundamental]
    return (top / bottom) * 100.0

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
        thds = [thd(window, 60) for window in windows]
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
                    #self.mongo_client.anomalies_collection.insert_one(anomaly)
                    self.debug(str(anomaly))
                    prev_beyond_threshold = False

    def on_message(self, topic, mauka_message_bytes):
        """
        Fired when this plugin receives a message. This will wait a certain amount of time to make sure that data
        is in the database before starting thd calculations.
        :param topic: Topic of the message.
        :param message: Contents of the message.
        """
        # event_id, box_id, waveform = pickle.loads(message)
        # self.debug("Calculating THD for event {} and box {} with waveform of len {}".format(event_id, box_id,
        #                                                                                     len(waveform)))
        mauka_message = protobuf.util.deserialize_mauka_message(mauka_message_bytes)
        self.debug("on_message {}".format(mauka_message))
        if protobuf.util.is_payload(mauka_message, protobuf.mauka_pb2.ADC_SAMPLES):
            self.sliding_thd(mauka_message.payload.event_id,
                             mauka_message.payload.box_id,
                             protobuf.util.repeated_as_ndarray(
                                 mauka_message.payload.data
                             ))
        else:
            self.logger.error("Received incorrect mauka message [{}] at ThdPlugin".format(
                protobuf.util.which_message_oneof(mauka_message)
            ))



