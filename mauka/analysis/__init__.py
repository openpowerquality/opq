"""
This module contains functions for performing analysis on raw power waveforms.
"""

import gridfs
import numpy


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
