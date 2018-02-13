"""
This plugin calculates locality of PQ events.
"""
import math
import multiprocessing
import threading
import typing

import analysis
import constants
import mongo.mongo
import plugins.base

import numpy
import scipy.fftpack



def perform_locality_fft_transient_calculation(fs, box_events):
    def is_event(wave):
        metric = 0
        max = 0
        for i in range(0, int(len(wave) / 2000)):
            waveform = wave[(i) * 2000:(i + 1) * 2000]
            norm = numpy.linalg.norm(waveform)
            y = scipy.fftpack.fft(waveform)
            x = numpy.fft.fftfreq(y.size, 1 / constants.SAMPLE_RATE_HZ)

            for f in [60, 120, 180, 240, 300, 360]:
                close = analysis.closest_idx(x, f)
                y[close] = 0
                close = analysis.closest_idx(x, f * -1)
                y[close] = 0
            y = scipy.fftpack.ifft(y)
            this_metrik = numpy.sum(numpy.abs(y)) / norm
            if this_metrik > metric:
                metric = this_metrik
                max = i * 2000
        if metric > 1.2:
            return max
        return -1

    count = 0
    locations = []
    for box_event in box_events:
        event_name = box_event["data_fs_filename"]
        event_data = analysis.waveform_from_file(fs, event_name)
        loc = is_event(event_data)
        if loc > 0:
            count += 1
            locations.append({"id": box_event["box_id"], "loc": loc})
    if count > 1:
        print("{} {}".format(count, locations))
    else:
        pass

def perform_locality_simple_features_calculation(fs, box_events):
    pass


class LocalityPlugin(plugins.base.MaukaPlugin):
    """
    Mauka plugin that calculates locality.
    """
    NAME = "LocalityPlugin"

    def __init__(self, config: typing.Dict, exit_event: multiprocessing.Event):
        """
        Initializes this plugin
        :param config: Mauka configuration
        :param exit_event: Exit event that can disable this plugin from parent process
        """
        super().__init__(config, ["RequestDataEvent", "LocalityRequestEvent"], LocalityPlugin.NAME, exit_event)
        self.get_data_after_s = self.config["plugins.LocalityPlugin.getDataAfterS"]

    def perform_locality_calculations(self, event_id: int):
        box_events = self.mongo_client.box_events_collection.find({"event_id": event_id})
        if len(box_events) <= 0:
            return

        perform_locality_fft_transient_calculation(self.mongo_client.fs, box_events)

    def on_message(self, topic, message):
        """
        Fired when this plugin receives a message. This will wait a certain amount of time to make sure that data
        is in the database before starting thd calculations.
        :param topic: Topic of the message.
        :param message: Contents of the message.
        """
        event_id = int(message)
        timer = threading.Timer(self.get_data_after_s, self.perform_locality_calculations, (event_id,))
        timer.start()
