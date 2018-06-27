"""
This module provides analysis/util functions that may be called from multiple locations.
"""

import typing

import numpy

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


def segment(a: numpy.ndarray, delta: float) -> typing.List[numpy.ndarray]:
    """
    Segments an array by splitting the array into stable segments and throwing away "changing" segments.
    :param a: An array.
    :param delta: The segmentation threshold.
    :return: A list of segmented arrays where each segment is a stable segment.
    """
    if a is None or delta is None:
        return []

    if len(a) == 0:
        return []

    if len(a) == 1:
        return [a]

    if len(a) == 2:
        if numpy.abs(a[0] - a[1]) < delta:
            return [a]
        else:
            return []

    abs_diffs = numpy.abs(numpy.diff(a))
    stable = (abs_diffs < delta)

    stable_segments = []
    for i, v in enumerate(stable):
        if v:
            if len(stable_segments) == 0:
                stable_segments.append([i, i + 1])
            else:
                last = stable_segments[len(stable_segments) - 1]
                if last[1] == i:  # merge
                    last[1] = i + 1
                else:  # append
                    stable_segments.append([i, i + 1])

    return list(map(numpy.array, stable_segments))
