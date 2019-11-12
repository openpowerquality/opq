"""
This module contains constants relating to the OPQ project or methods for accessing constants.
"""

import math

SAMPLES_PER_CYCLE: float = 200.0
"""Number of samples per electrical cycle for OPQ box"""

SAMPLES_PER_MILLISECOND: float = 12.0

SAMPLE_RATE_HZ: float = 12000.0
"""Sample rate of OPQ box"""

CYCLES_PER_SECOND: float = 60.0
"""Cycles per second"""

CYCLES_PER_MILLISECOND: float = 0.06

MILLISECONDS_PER_SECOND: float = 1000.0

NOMINAL_VRMS: float = 120.0

CONFIG_ENV: str = "MAUKA_SETTINGS"

TWO_PI: float = 2.0 * math.pi
