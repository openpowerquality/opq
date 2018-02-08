"""
This module contains functions for performing analysis on raw power waveforms.
"""
import math

import gridfs
import numpy

import constants


def sq(num: float) -> float:
    """
    Squares a number
    :param num: Number to square
    :return: Squared number
    """
    return num * num


def to_s16bit(data: bytes) -> numpy.ndarray:
    """
    Converts a list of bytes into an array of signed 16-bit values.
    :param data: The byte array.
    :return: An array of signed 16-bit values.
    """
    return numpy.frombuffer(data, numpy.int16)


def waveform_from_file(fs: gridfs.GridFS, filename: str) -> numpy.ndarray:
    """
    Loads a raw waveform from gridfs.
    :param fs: The gridfs client.
    :param filename: The filename of the file to load.
    :return: An array of signed 16-bit integers that represent the raw waveform.
    """
    buf = fs.get_last_version(filename).read()
    s16bit_buf = to_s16bit(buf)
    return s16bit_buf


def closest_idx(array: numpy.ndarray, val: float) -> int:
    """
    Given a sorted array, find the index of the value closest to val.
    :param array: The array to search through.
    :param val: The value to search for.
    :return: The index into the array of the closest value to val.
    """
    return numpy.argmin(numpy.abs(array - val))


def calibrate_waveform(waveform: numpy.ndarray, calibration_constant: float = 1.0) -> numpy.ndarray:
    """
    Returns a calibrated waveform given a non-calibrated waveform and a constant.
    :param waveform: The uncalibrated waveform
    :param calibration_constant: The calibration constant for a specific box
    :return: The calibrated waveform
    """
    return waveform / calibration_constant


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


def c_to_ms(c: float) -> float:
    """
    Convert cycles to milliseconds
    :param c: cycles
    :return: milliseconds
    """
    return (c * (1 / 60)) * 1000.0


def waveform_duration_s(waveform: numpy.ndarray, sample_rate_hz=constants.SAMPLE_RATE_HZ):
    """
    Returns the length of a given waveform in fractional seconds.
    :param waveform: The waveform to find the time duration of.
    :param sample_rate_hz: The sample rate of the given waveform.
    :return: The total number of fractional seconds that the waveform makes up.
    """
    return float(len(waveform)) / float(sample_rate_hz)
