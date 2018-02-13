"""
This module contains constants relating to the OPQ project or methods for accessing constants.
"""

import typing

from mongo.mongo import get_box_calibration_constants

SAMPLES_PER_CYCLE = 200
"""Number of samples per electrical cycle for OPQ box"""

SAMPLE_RATE_HZ = 12000.0
"""Sample rate of OPQ box"""


def get_calibration_constant(box_id: int) -> float:
    """
    Return the calibration constant for a specified box id.
    :param box_id: The box id to query
    :return: The calibration constant or 1.0 if the constant can't be found
    """
    calibration_constants = get_box_calibration_constants()
    if box_id in calibration_constants:
        return calibration_constants[box_id]
    else:
        return 1.0


def memoize(fn: typing.Callable) -> typing.Callable:
    cache = {}

    def helper(v):
        if v in cache:
            return cache[v]
        else:
            cache[v] = fn(v)
            return cache[v]

    return helper


cached_calibration_constant = memoize(get_calibration_constant)
