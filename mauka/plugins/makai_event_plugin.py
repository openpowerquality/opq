"""
This module provides a plugin and utilities for interacting and transforming raw data produced from Makai events.
"""

import math
import multiprocessing
import threading
import typing

import numpy
from scipy import optimize
from scipy import signal

import analysis
import config
import constants
import mongo
import plugins.base_plugin
from plugins.routes import Routes
import plugins.thd_plugin
import protobuf.mauka_pb2
import protobuf.pb_util



def smooth_waveform(sample: numpy.ndarray, filter_order: int = 2, cutoff_frequency: float = 500.0,
                    downsample_factor: int = 4) -> numpy.ndarray:
    """
    Method to smooth waveform using a butterworth filter to lower sensitivity of frequency calculation.
    :param sample:
    :param filter_order:
    :param cutoff_frequency:
    :param downsample_factor: downsample factor for decimate function
    :return:
    """

    # smooth digital signal w/ butterworth filter
    # First, design the Butterworth filter
    # Cutoff frequencies in half-cycles / sample
    cutoff_frequency_nyquist = cutoff_frequency * 2 / constants.SAMPLE_RATE_HZ
    numerator, denominator = signal.butter(filter_order, cutoff_frequency_nyquist, output='ba')

    # Second, create Dicrete-time linear time invariant system instance
    dtltis = signal.dlti(numerator, denominator)
    # decimate signal to improve runtime
    return signal.decimate(sample, downsample_factor, ftype=dtltis)


def find_zero_xings(waveform: numpy.ndarray) -> numpy.ndarray:
    """
    Function which returns a boolean array indicating the positions of zero crossings in the the waveform
    :param waveform:
    :return: a boolean array indicating the positions of zero crossings in the the waveform
    """
    return numpy.diff(numpy.signbit(waveform))


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
    rms_voltages = []
    window_size = int(window_size)
    while len(waveform) >= window_size:
        samples = waveform[:window_size]
        waveform = waveform[window_size:]
        rms_voltages.append(vrms(samples))

    # pylint: disable=len-as-condition
    if len(waveform) > 0:
        rms_voltages.append(vrms(waveform))

    return numpy.array(rms_voltages)


def frequency(samples: numpy.ndarray, down_sample_factor: int) -> float:
    """
    Calculates the frequency of the supplied samples
    :param samples: Samples to calculate frequency over.
    :param down_sample_factor: the down sampling factor from the filtering, used to modify the sampling rate
    :return: The frequency value of the provided samples in Hz.
    """

    # Fit sinusoidal curve to data
    guess_amp = constants.NOMINAL_VRMS * numpy.sqrt(2)
    guess_freq = constants.CYCLES_PER_SECOND
    guess_phase = 0.0
    guess_mean = 0.0
    idx = numpy.arange(0,
                       len(samples) / (constants.SAMPLE_RATE_HZ / down_sample_factor),
                       1 / (constants.SAMPLE_RATE_HZ / down_sample_factor))
    idx = idx[:len(samples)]

    def optimize_func(args):
        """
        Optimized the function for finding and fitting the frequency.
        :param args: A list containing in this order: guess_amp, guess_freq, guess_phase, guess_mean.
        :return: Optimized function.
        """
        return args[0] * numpy.sin(args[1] * 2 * numpy.pi * idx + args[2]) + args[3] - samples

    _, est_freq, _, _ = optimize.leastsq(optimize_func,
                                         numpy.array([guess_amp, guess_freq, guess_phase, guess_mean]))[0]

    return round(est_freq, ndigits=2)


def frequency_waveform(waveform: numpy.ndarray, window_size: int, filter_order: int, cutoff_frequency: float,
                       down_sample_factor) -> numpy.ndarray:
    """
    Calculated frequency of a waveform using a given window size. In most cases, our window size should be the
    number of samples in a cycle.
    :param waveform: The waveform to find frequency values for.
    :param window_size: The size of the window used to compute frequency over the waveform.
    :param filter_order: order of band pass butterworth filter
    :param cutoff_frequency: cutoff frequency of low pass butterworth filter to smooth digital signal
    :param down_sample_factor: The down sample factor
    :return: An array of frequency values calculated for a given waveform.
    """

    # smooth digital signal w/ butterworth filter
    filtered_waveform = smooth_waveform(waveform, filter_order=filter_order, cutoff_frequency=cutoff_frequency,
                                        downsample_factor=down_sample_factor)

    # filtered frequency calc.
    frequencies = []
    while len(filtered_waveform) >= window_size:
        samples = filtered_waveform[:window_size]
        filtered_waveform = filtered_waveform[window_size:]
        frequencies.append(frequency(samples, down_sample_factor))

    # pylint: disable=len-as-condition
    if len(filtered_waveform) > 0:
        frequencies.append(frequency(filtered_waveform, down_sample_factor))

    return numpy.array(frequencies)


AcquireDataType = typing.Tuple[
    protobuf.mauka_pb2.MaukaMessage,
    protobuf.mauka_pb2.MaukaMessage,
    protobuf.mauka_pb2.MaukaMessage,
    protobuf.mauka_pb2.MaukaMessage]


def acquire_data(mongo_client: mongo.OpqMongoClient,
                 makai_event_plugin: 'MakaiEventPlugin',
                 event_id: int,
                 box_id: str,
                 name: str) -> AcquireDataType:
    """
    Given an event_id, acquire the raw data for each box associated with the given event. Perform feature
    extraction of the raw data and publish those features for downstream plugins.
    :param makai_event_plugin: An instance of the plugin.
    :param box_id: The box id.
    :param mongo_client: The mongo client to use to make this request.
    :param event_id: The event id to acquire data for.
    :param name: The name of the service requesting data.
    """
    box_event = mongo_client.box_events_collection.find_one({"event_id": event_id,
                                                             "box_id": box_id})
    waveform = mongo.get_waveform(mongo_client, box_event["data_fs_filename"])

    makai_event_plugin.debug("Loaded waveform for event_id=%s box_id=%s with len=%d" %
                             (event_id, box_id, len(waveform)))

    box_id = box_event["box_id"]
    makai_event_plugin.debug("box_id={} and type={}".format(box_id, type(box_id)))
    calibration_constant = mongo_client.get_box_calibration_constant(box_id)
    makai_event_plugin.debug("calibration_constant=%f" % calibration_constant)
    waveform_calibrated = waveform / calibration_constant

    makai_event_plugin.debug("Loaded calibrated waveform for event_id=%s box_id=%s with len=%d" %
                             (event_id, box_id, len(waveform_calibrated)))

    start_timestamp = box_event["event_start_timestamp_ms"]
    end_timestamp = box_event["event_end_timestamp_ms"]

    makai_event_plugin.debug("Extracted timestamps %d-%d" % (start_timestamp, end_timestamp))

    try:
        adc_samples = protobuf.pb_util.build_payload(name,
                                                     event_id,
                                                     box_id,
                                                     protobuf.mauka_pb2.ADC_SAMPLES,
                                                     waveform,
                                                     start_timestamp,
                                                     end_timestamp)
        makai_event_plugin.debug("Got ADC samples")
    except Exception as exception:
        makai_event_plugin.logger.error("Error getting ADC_SAMPLES %s", str(exception))
        adc_samples = protobuf.pb_util.build_payload(name,
                                                     event_id,
                                                     box_id,
                                                     protobuf.mauka_pb2.ADC_SAMPLES,
                                                     [],
                                                     start_timestamp,
                                                     end_timestamp)

    try:
        raw_voltage = protobuf.pb_util.build_payload(name,
                                                     event_id,
                                                     box_id,
                                                     protobuf.mauka_pb2.VOLTAGE_RAW,
                                                     waveform_calibrated,
                                                     start_timestamp,
                                                     end_timestamp)
        makai_event_plugin.debug("Got raw voltage")
    except Exception as exception:
        makai_event_plugin.logger.error("Error getting VOLTAGE_RAW: %s", str(exception))
        raw_voltage = protobuf.pb_util.build_payload(name,
                                                     event_id,
                                                     box_id,
                                                     protobuf.mauka_pb2.VOLTAGE_RAW,
                                                     [],
                                                     start_timestamp,
                                                     end_timestamp)

    try:
        rms_windowed_voltage = protobuf.pb_util.build_payload(name,
                                                              event_id,
                                                              box_id,
                                                              protobuf.mauka_pb2.VOLTAGE_RMS_WINDOWED,
                                                              vrms_waveform(waveform_calibrated,
                                                                            int(constants.SAMPLES_PER_CYCLE)),
                                                              start_timestamp,
                                                              end_timestamp)
        makai_event_plugin.debug("Got rms windowed voltage")
    except Exception as exception:
        makai_event_plugin.logger.error("Error getting VOLTAGE_RMS_WINDOWED: %s", str(exception))
        rms_windowed_voltage = protobuf.pb_util.build_payload(name,
                                                              event_id,
                                                              box_id,
                                                              protobuf.mauka_pb2.VOLTAGE_RMS_WINDOWED,
                                                              [],
                                                              start_timestamp,
                                                              end_timestamp)

    try:
        frequency_windowed = protobuf.pb_util.build_payload(name,
                                                            event_id,
                                                            box_id,
                                                            protobuf.mauka_pb2.FREQUENCY_WINDOWED,
                                                            analysis.frequency_per_cycle(waveform_calibrated),
                                                            start_timestamp,
                                                            end_timestamp)
        makai_event_plugin.debug("Got windowed frequency")
    except Exception as exception:
        frequency_windowed = protobuf.pb_util.build_payload(name,
                                                            event_id,
                                                            box_id,
                                                            protobuf.mauka_pb2.FREQUENCY_WINDOWED,
                                                            [],
                                                            start_timestamp,
                                                            end_timestamp)
        makai_event_plugin.logger.error("Error getting FREQUENCY_WINDOWED: %s", str(exception))

    return adc_samples, raw_voltage, rms_windowed_voltage, frequency_windowed


class MakaiEventPlugin(plugins.base_plugin.MaukaPlugin):
    """
    This plugin retrieves data when Makai triggers events, performs feature extraction, and then publishes relevant
    features to Mauka downstream plugins.
    """
    NAME = "MakaiEventPlugin"

    def __init__(self, conf: config.MaukaConfig, exit_event: multiprocessing.Event):
        super().__init__(conf, [Routes.makai_event], MakaiEventPlugin.NAME, exit_event)
        self.get_data_after_s = float(self.config["plugins.MakaiEventPlugin.getDataAfterS"])
        self.filter_order = int(self.config.get("plugins.MakaiEventPlugin.filterOrder"))
        self.cutoff_frequency = float(self.config.get("plugins.MakaiEventPlugin.cutoffFrequency"))
        self.samples_per_window = int(constants.SAMPLES_PER_CYCLE) * int(self.config.get(
            "plugins.MakaiEventPlugin.frequencyWindowCycles"))
        self.down_sample_factor = int(self.config.get("plugins.MakaiEventPlugin.frequencyDownSampleRate"))

    def acquire_and_produce(self, event_id: int):
        """
        Acquire raw data for a given event_id, perform feature extraction, and produce to the rest of the Mauka
        processing pipeline.
        :param event_id: The event id to load raw data for.
        """
        self.debug("in acquire_and_produce")
        box_events = self.mongo_client.box_events_collection.find({"event_id": event_id})
        self.debug("Found %d box_events" % box_events.count())
        for box_event in box_events:
            box_id = box_event["box_id"]
            adc_samples, raw_voltage, rms_windowed_voltage, frequency_windowed = acquire_data(self.mongo_client,
                                                                                              self,
                                                                                              event_id,
                                                                                              box_id,
                                                                                              self.name)
            self.produce(Routes.adc_samples, adc_samples)
            self.produce(Routes.raw_voltage, raw_voltage)
            self.produce(Routes.rms_windowed_voltage, rms_windowed_voltage)
            self.produce(Routes.windowed_frequency, frequency_windowed)
            self.debug("Produced data for box_event=%s" % str(box_event))
        self.debug("Done with acquire_and_produce")

    def on_message(self, topic, mauka_message):
        if protobuf.pb_util.is_makai_event_message(mauka_message):
            self.debug("on_message: {}".format(mauka_message))
            timer = threading.Timer(self.get_data_after_s,
                                    function=self.acquire_and_produce,
                                    args=[mauka_message.makai_event.event_id])

            # Produce a message to the GC
            self.debug("Producing laha_gc update")
            self.produce(Routes.laha_gc,
                         protobuf.pb_util.build_gc_update(self.name, protobuf.mauka_pb2.EVENTS,
                                                          mauka_message.makai_event.event_id))
            self.debug("laha_gc update produced")
            timer.start()
        else:
            self.logger.error("Received incorrect mauka message [%s] for MakaiEventPlugin",
                              protobuf.pb_util.which_message_oneof(mauka_message))
