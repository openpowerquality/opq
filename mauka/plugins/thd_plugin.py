"""
This plugin calculates total harmonic distortion (THD) over waveforms.
"""
import multiprocessing
import typing

import numpy
import scipy.fftpack

import config
import constants
import mongo
import plugins.base_plugin
import protobuf.mauka_pb2
import protobuf.util


def rolling_window(array: numpy.ndarray, window_size: int) -> typing.List[numpy.ndarray]:
    """
    Given an array and window, restructure the data so that it is in a rolling window of size "window" and step = 1.
    :param array: The array to roll a window over
    :param window_size: The window size
    :return: A 2D array where each row is a window into the provided data.
    """
    array_len = len(array)
    if array_len < window_size:
        return [array]

    num_windows = array_len / window_size
    return numpy.array_split(array, num_windows)


def thd(waveform: numpy.ndarray, fundamental: int) -> float:
    """
    Calculates the total harmonic distortion (THD) of the provided waveform with the provided fundamental of the
    waveform.
    :param waveform: The waveform to find the THD of.
    :param fundamental: The fundamental frequency (in Hz) of the provided waveform.
    :return: The calculated THD of the provided waveform.
    """
    fundamental = int(fundamental)
    abs_dft = numpy.abs(scipy.fftpack.fft(waveform))
    top = numpy.sqrt(numpy.sum(abs_dft[i] ** 2 for i in numpy.arange(2 * fundamental, len(abs_dft) // 2, fundamental)))
    bottom = abs_dft[fundamental]
    return (top / bottom) * 100.0


def sliding_thd(mongo_client, threshold_percent, sliding_window_ms, event_id: int, box_id: str,
                box_event_start_timestamp: int, waveform: numpy.ndarray,
                thd_plugin: 'ThdPlugin') -> typing.List[int]:
    """
    Calculates sliding THD over a waveform.
    High THD values are then stored as incidents to the database.
    :param event_id: Event that this waveform came form.
    :param box_id: Box that this waveform came from.
    :param box_event_start_timestamp: Start timestamp of the provided waveform
    :param waveform: The waveform to calculate THD over.
    """
    thd_plugin.debug("in sliding_thd")
    window_size = int(constants.SAMPLES_PER_CYCLE)
    thd_plugin.debug("window_size=%d" % window_size)
    windows = rolling_window(waveform, window_size)
    thd_plugin.debug(str(windows))
    thds = [thd(window, constants.CYCLES_PER_SECOND) for window in windows]
    thd_plugin.debug("calculated thds")
    prev_beyond_threshold = False
    prev_idx = -1
    max_thd = -1
    incident_ids = []
    for i, thd_i in enumerate(thds):
        if thd_i > max_thd:
            max_thd = thd_i

        if thd_i > threshold_percent:
            # We only care if this is the start of a new anomaly
            if not prev_beyond_threshold:
                prev_idx = i
                prev_beyond_threshold = True
        else:
            # We only care if this is the end of an anomaly
            if prev_beyond_threshold:
                prev_beyond_threshold = False

                # Every thd value is a sample over a 200 ms window
                incident_start_timestamp = int(box_event_start_timestamp + (prev_idx * sliding_window_ms))
                incident_end_timestamp = int(box_event_start_timestamp + (i * sliding_window_ms) + sliding_window_ms)

                incident_id = mongo.store_incident(event_id,
                                                   box_id,
                                                   incident_start_timestamp,
                                                   incident_end_timestamp,
                                                   mongo.IncidentMeasurementType.THD,
                                                   max_thd,
                                                   [mongo.IncidentClassification.EXCESSIVE_THD],
                                                   [],
                                                   {},
                                                   mongo_client)

                incident_ids.append(incident_id)
    thd_plugin.debug("exiting sliding_thd")
    return incident_ids


class ThdPlugin(plugins.base_plugin.MaukaPlugin):
    """
    Mauka plugin that calculates THD over raw waveforms.
    """
    NAME = "ThdPlugin"

    def __init__(self, conf: config.MaukaConfig, exit_event: multiprocessing.Event):
        """
        Initializes this plugin
        :param conf: Mauka configuration
        :param exit_event: Exit event that can disable this plugin from parent process
        """
        super().__init__(conf, ["AdcSamples", "ThdRequestEvent"], ThdPlugin.NAME, exit_event)
        self.threshold_percent = float(self.config.get("plugins.ThdPlugin.threshold.percent"))
        self.sliding_window_ms = float(self.config.get("plugins.ThdPlugin.window.size.ms"))

    def on_message(self, topic, mauka_message):
        """
        Fired when this plugin receives a message. This will wait a certain amount of time to make sure that data
        is in the database before starting thd calculations.
        :param topic: Topic of the message.
        :param mauka_message: Contents of the message.
        """
        if protobuf.util.is_payload(mauka_message, protobuf.mauka_pb2.ADC_SAMPLES):
            self.debug("on_message {}:{} len:{}".format(mauka_message.payload.event_id,
                                                        mauka_message.payload.box_id,
                                                        len(mauka_message.payload.data)))
            self.debug("Running sliding_thd on %d samples"
                       % len(protobuf.util.repeated_as_ndarray(mauka_message.payload.data)))
            incident_ids = sliding_thd(self.mongo_client,
                                       self.threshold_percent,
                                       self.sliding_window_ms,
                                       mauka_message.payload.event_id,
                                       mauka_message.payload.box_id,
                                       mauka_message.payload.start_timestamp_ms,
                                       protobuf.util.repeated_as_ndarray(mauka_message.payload.data),
                                       self)
            self.debug("Done running sliding_thd")

            for incident_id in incident_ids:
                # Produce a message to the GC
                self.produce("laha_gc", protobuf.util.build_gc_update(self.name,
                                                                      protobuf.mauka_pb2.INCIDENTS,
                                                                      incident_id))
        else:
            self.logger.error("Received incorrect mauka message [%s] at ThdPlugin",
                              protobuf.util.which_message_oneof(mauka_message))


def rerun(mauka_message: protobuf.mauka_pb2.MaukaMessage,
          logger,
          mongo_client: mongo.OpqMongoClient = None):
    """
    Rerun the THD plugin over a Makai box event.
    :param mauka_message: The event message to rerun THD analysis over.
    :param logger: The application logger
    :param mongo_client: An optional instance of a mongo client.
    :return:
    """
    client = mongo.get_default_client(mongo_client)

    if protobuf.util.is_payload(mauka_message, protobuf.mauka_pb2.ADC_SAMPLES):
        sliding_thd(client,
                    5.0,
                    200,
                    mauka_message.payload.event_id,
                    mauka_message.payload.box_id,
                    mauka_message.payload.start_timestamp_ms,
                    protobuf.util.repeated_as_ndarray(mauka_message.payload.data))
    else:
        logger.error("Received incorrect mauka message [%s] at ThdPlugin rerun",
                     protobuf.util.which_message_oneof(mauka_message))
