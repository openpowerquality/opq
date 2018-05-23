import math
import multiprocessing
import pickle
import threading
import typing

import numpy

import constants
import mongo
import plugins.base


def vrms(samples: numpy.ndarray) -> float:
    """
    Calculates the Voltage root-mean-square of the supplied samples
    :param samples: Samples to calculate Vrms over.
    :return: The Vrms value of the provided samples.
    """
    summed_sqs = numpy.sum(numpy.square(samples))
    return math.sqrt(summed_sqs / len(samples))


def vrms_waveform(waveform: numpy.ndarray, window_size: int = constants.SAMPLES_PER_CYCLE) -> numpy.ndarray:
    """
    Calculated Vrms of a waveform using a given window size. In most cases, our window size should be the
    number of samples in a cycle.
    :param waveform: The waveform to find Vrms values for.
    :param window_size: The size of the window used to compute Vrms over the waveform.
    :return: An array of vrms values calculated for a given waveform.
    """
    v = []
    while len(waveform) >= window_size:
        samples = waveform[:window_size]
        waveform = waveform[window_size:]
        v.append(vrms(samples))

    if len(waveform) > 0:
        v.append(vrms(waveform))

    return numpy.array(v)


class MakaiEventPlugin(plugins.base.MaukaPlugin):
    NAME = "MakaiEventPlugin"

    def __init__(self, config: typing.Dict, exit_event: multiprocessing.Event):
        super().__init__(config, ["RequestDataEvent"], MakaiEventPlugin.NAME, exit_event)
        self.get_data_after_s = float(self.config["plugins.MakaiEventPlugin.getDataAfterS"])

    def acquire_data(self, event_id: int):
        box_events = self.mongo_client.box_events_collection.find({"event_id": event_id})
        self.debug("len(box_events): {}".format(box_events.count()))
        for box_event in box_events:
            waveform = mongo.get_waveform(self.mongo_client, box_event["data_fs_filename"])
            box_id = box_event["box_id"]
            calibration_constant = mongo.cached_calibration_constant(box_id)
            waveform_calibrated = waveform / calibration_constant
            waveform_vrms = vrms_waveform(waveform_calibrated)

            self.produce("Waveform", pickle.dumps((event_id, box_id, waveform)))
            self.debug("Sending waveform {}".format(len(waveform)))
            self.produce("CalibratedWaveform", pickle.dumps((event_id, box_id, waveform_calibrated)))
            self.debug("Sending calibrated waveform {}".format(len(waveform_calibrated)))
            self.produce("VrmsWaveform", pickle.dumps((event_id, box_id, waveform_vrms)))
            self.debug("Sending vrms waveform {}".format(len(waveform_vrms)))

    def on_message(self, topic, message):
        event_id = int(message)
        self.debug("Recv event_id {}".format(event_id))
        timer = threading.Timer(self.get_data_after_s, function=self.acquire_data, args=[event_id])
        timer.start()
