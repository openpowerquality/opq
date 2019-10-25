"""
This module provides analysis/util functions that may be called from multiple locations.
"""

import logging
import typing

import numpy as np
import ruptures as rpt

import constants


def c_to_ms(cycles: float) -> float:
    """
    Convert cycles to milliseconds
    :param cycles: cycles
    :return: milliseconds
    """
    return cycles / constants.CYCLES_PER_MILLISECOND


def ms_to_c(duration_ms: float) -> float:
    """
    Convert a duration in milliseconds to cycles.
    :param duration_ms: milliseconds
    :return: cycles
    """
    return duration_ms * constants.CYCLES_PER_MILLISECOND


def ms_to_samples(duration_ms: float) -> float:
    """
    Convert a duration in milliseconds to cycles.
    :param duration_ms: milliseconds
    :return: Number of samples over that duration
    """
    return duration_ms * constants.SAMPLES_PER_MILLISECOND


def samples_to_ms(samples: float) -> float:
    """
    Convert a given number of samples to milliseconds.
    :param samples: Number of samples.
    :return: Milliseconds computed from number of samples.
    """
    return samples / constants.SAMPLES_PER_MILLISECOND


def percent_nominal_to_rms(percent_nominal: float) -> float:
    """
    Converts percent nominal Voltage into an RMS value.
    :param percent_nominal: The percent nominal voltage.
    :return: Voltage RMS
    """
    return (percent_nominal * 120.0) / 100


def rms_to_percent_nominal(rms_voltage: float) -> float:
    """
    Converts RMS voltage to percent nominal voltage.
    :param rms_voltage: The RMS voltage.
    :return: Percent nominal voltage.
    """
    return (rms_voltage / 120.0) * 100.0


def segment(array: np.ndarray, delta: float) -> typing.List[np.ndarray]:
    """
    Segments an array by splitting the array into stable segments and throwing away "changing" segments.
    :param array: An array.
    :param delta: The segmentation threshold.
    :return: A list of segmented arrays where each segment is a stable segment.
    """
    if array is None or delta is None:
        return []

    # pylint: disable=len-as-condition
    if len(array) == 0:
        return []

    if len(array) == 1:
        return [array]

    if len(array) == 2:
        if np.abs(array[0] - array[1]) < delta:
            return [array]

        return []

    abs_diffs = np.abs(np.diff(array))
    stable = (abs_diffs < delta)

    stable_segments = []
    for i, is_stable in enumerate(stable):
        if is_stable:
            if not stable_segments:
                stable_segments.append([i, i + 1])
            else:
                last = stable_segments[len(stable_segments) - 1]
                if last[1] == i:  # merge
                    last[1] = i + 1
                else:  # append
                    stable_segments.append([i, i + 1])

    return list(map(np.array, stable_segments))


# pylint: disable=W0703
# pylint: disable=C0103
def segment_array(data: np.ndarray) -> typing.List[np.ndarray]:
    """
    Split up data into segments.
    :param data:
    :return:
    """

    if data is None or len(data) == 0:
        return []

    if len(data) == 1:
        return [np.array([1])]

    try:
        algo = rpt.Pelt().fit(data)
        segment_idxs = algo.predict(pen=1)

        segments: typing.List[np.ndarray] = []
        start = 0
        for idx in segment_idxs:
            segments.append(data[start:idx])
            start = idx

        return segments
    except Exception as e:
        logging.error(str(e))
        return []
