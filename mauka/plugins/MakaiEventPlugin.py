import math
import multiprocessing
import threading
import typing

import numpy

import constants
import mongo
import plugins.base
import protobuf.mauka_pb2
import protobuf.util
from scipy import optimize


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
    window_size = int(window_size)
    while len(waveform) >= window_size:
        samples = waveform[:window_size]
        waveform = waveform[window_size:]
        v.append(vrms(samples))

    if len(waveform) > 0:
        v.append(vrms(waveform))

    return numpy.array(v)


def frequency(samples: numpy.ndarray) -> float:
    """
    Calculates the frequency of the supplied samples
    :param samples: Samples to calculate frequency over.
    :return: The frequency value of the provided samples in Hz.
    """

    """Fit sinusoidal curve to data"""
    guess_amp = 120.0
    guess_freq = constants.CYCLES_PER_SECOND
    guess_phase = 0.0
    guess_mean = 0.0
    t = numpy.arange(0, len(samples) / constants.SAMPLE_RATE_HZ, 1 / constants.SAMPLE_RATE_HZ)

    optimize_func = lambda x: x[0] * numpy.sin(x[1] * 2 * numpy.pi * t + x[2]) + x[3] - samples
    est_amp, est_freq, est_phase, est_mean = optimize.leastsq(optimize_func,
                                                              numpy.array(
                                                                  [guess_amp, guess_freq, guess_phase, guess_mean])
                                                              )[0]
    return numpy.round(est_freq, decimals=2)

    """Zero Crossing Method:"""
    # zero_crossing_indices = numpy.diff(samples > 0)
    # num_zero_crossings = sum(zero_crossing_indices)
    # zero_crossing_time_intervals = numpy.diff(numpy.array(range(len(zero_crossing_indices)))[zero_crossing_indices])
    # if num_zero_crossings >= 2:
    #     return ((num_zero_crossings - 1) * constants.SAMPLE_RATE_HZ) / (2 * sum(zero_crossing_time_intervals))
    # else:
    #     return 0.0

    """DFT of Sampled Waveform Using Numpy's FFT Implementation"""
    # f = interpolate.interp1d(range(len(samples)), samples)
    # dft = numpy.abs(numpy.fft.rfft(f(numpy.arange(0, 199, 0.001)))) #amplitude spectrum of dft
    # freq = numpy.fft.rfftfreq((len(dft) - 1) * 2, d = 0.001 / (constants.SAMPLE_RATE_HZ))
    # return freq[dft.argmax()]


def frequency_waveform(waveform: numpy.ndarray, window_size: int = constants.SAMPLES_PER_CYCLE) -> numpy.ndarray:
    """
    Calculated frequency of a waveform using a given window size. In most cases, our window size should be the
    number of samples in a cycle.
    :param waveform: The waveform to find frequency values for.
    :param window_size: The size of the window used to compute frequency over the waveform.
    :return: An array of frequency values calculated for a given waveform.
    """

    f = []
    window_size = int(window_size)
    while len(waveform) >= window_size:
        samples = waveform[:window_size]
        waveform = waveform[window_size:]
        f.append(frequency(samples))

    if len(waveform) > 0:
        f.append(frequency(waveform))

    return numpy.array(f)


class MakaiEventPlugin(plugins.base.MaukaPlugin):
    NAME = "MakaiEventPlugin"

    def __init__(self, config: typing.Dict, exit_event: multiprocessing.Event):
        super().__init__(config, ["MakaiEvent"], MakaiEventPlugin.NAME, exit_event)
        self.get_data_after_s = float(self.config["plugins.MakaiEventPlugin.getDataAfterS"])

    def acquire_data(self, event_id: int):
        box_events = self.mongo_client.box_events_collection.find({"event_id": event_id})
        for box_event in box_events:
            waveform = mongo.get_waveform(self.mongo_client, box_event["data_fs_filename"])
            box_id = box_event["box_id"]
            calibration_constant = mongo.cached_calibration_constant(box_id)
            waveform_calibrated = waveform / calibration_constant
            waveform_vrms = vrms_waveform(waveform_calibrated, int(constants.SAMPLES_PER_CYCLE))
            waveform_frequency = frequency_waveform(waveform_calibrated, int(constants.SAMPLES_PER_CYCLE))

            start_timestamp = box_event["event_start_timestamp_ms"]
            end_timestamp = box_event["event_end_timestamp_ms"]

            adc_samples = protobuf.util.build_payload(self.name,
                                                      event_id,
                                                      box_id,
                                                      protobuf.mauka_pb2.ADC_SAMPLES,
                                                      waveform,
                                                      start_timestamp,
                                                      end_timestamp)

            raw_voltage = protobuf.util.build_payload(self.name,
                                                      event_id,
                                                      box_id,
                                                      protobuf.mauka_pb2.VOLTAGE_RAW,
                                                      waveform_calibrated,
                                                      start_timestamp,
                                                      end_timestamp)

            rms_windowed_voltage = protobuf.util.build_payload(self.name,
                                                               event_id,
                                                               box_id,
                                                               protobuf.mauka_pb2.VOLTAGE_RMS_WINDOWED,
                                                               waveform_vrms,
                                                               start_timestamp,
                                                               end_timestamp)

            frequency_windowed = protobuf.util.build_payload(self.name,
                                                             event_id,
                                                             box_id,
                                                             protobuf.mauka_pb2.FREQUENCY_WINDOWED,
                                                             waveform_frequency,
                                                             start_timestamp,
                                                             end_timestamp)

            self.produce("AdcSamples", adc_samples)
            self.produce("RawVoltage", raw_voltage)
            self.produce("RmsWindowedVoltage", rms_windowed_voltage)
            self.produce("WindowedFrequency", frequency_windowed)

    def on_message(self, topic, mauka_message):
        if protobuf.util.is_makai_event_message(mauka_message):
            self.debug("on_message: {}".format(mauka_message))
            timer = threading.Timer(self.get_data_after_s,
                                    function=self.acquire_data,
                                    args=[mauka_message.makai_event.event_id])
            timer.start()
        else:
            self.logger.error("Received incorrect mauka message [{}] for MakaiEventPlugin".format(
                protobuf.util.which_message_oneof(mauka_message)
            ))
