"""
This module provides analysis/util functions that may be called from multiple locations.
"""

import logging
from typing import List, Optional

import matplotlib.pyplot as plt
import numpy as np
import ruptures as rpt
import scipy.fftpack as fft
import scipy.optimize

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


def segment(array: np.ndarray, delta: float) -> List[np.ndarray]:
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
def segment_array(data: np.ndarray) -> List[np.ndarray]:
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

        segments: List[np.ndarray] = []
        start = 0
        for idx in segment_idxs:
            segments.append(data[start:idx])
            start = idx

        return segments
    except Exception as e:
        logging.error(str(e))
        return []


def fit_fn(x: np.ndarray, amplitude: float, frequency: float, phase: float, offset: float):
    """
    A function used to fit sine waves to power data.
    :param x: The x-values.
    :param amplitude: The amplitude.
    :param frequency: The frequency.
    :param phase: The phase.
    :param offset: The offset.
    """
    return np.sin(x * frequency * constants.TWO_PI / constants.SAMPLE_RATE_HZ + phase) * amplitude + offset


def fft_freq(samples: np.ndarray) -> float:
    """
    Calculate the frequency of the provided samples using FFT.
    :param samples: Samples to calculate frequency over.
    :return: The fundamental frequency.
    """
    f = fft.fft(samples)
    freqs = fft.fftfreq(len(samples))
    largest_idx = np.argmax(np.abs(f))
    return abs(freqs[largest_idx] * constants.SAMPLE_RATE_HZ)


# noinspection PyArgumentList
def fit_data(y_values: np.ndarray,
             amp_guess: Optional[float] = None,
             freq_guess: Optional[float] = None,
             phase_guess: Optional[float] = None,
             offset_guess: Optional[float] = None,
             do_plot: bool = False) -> np.ndarray:
    """
    Fits a sine function to the given data. Either computes the best guess params or uses what are provided in.
    :param y_values: The samples.
    :param amp_guess: The optional amplitude guess.
    :param freq_guess: The optional frequency guess.
    :param phase_guess: The optional phase guess.
    :param offset_guess: The optional offset guess.
    :param do_plot: When set, the fit will be plotted.
    :return: A numpy array containing the fitted amplitude, fitted frequency, fitted phase, and fitted offset.
    """
    x_values = np.arange(0, len(y_values))

    if not freq_guess:
        freq_guess = fft_freq(y_values)

    if not amp_guess:
        amp_guess = (abs(y_values.min()) + y_values.max()) / 2.0  # 120.0 * math.sqrt(2)

    if not phase_guess:
        phase_guess = 0.0

    if not offset_guess:
        offset_guess = y_values.mean()

    fit = scipy.optimize.curve_fit(fit_fn, x_values, y_values, [
        amp_guess, freq_guess, phase_guess, offset_guess
    ])

    if do_plot:
        _, ax = plt.subplots(1, 1, figsize=(16, 9))
        ax.scatter(x_values, y_values, color="blue", label="Data", linewidths=.1)
        ax.plot(x_values, fit_fn(x_values, amp_guess, freq_guess, phase_guess, offset_guess), color="green",
                label="Best Guess")
        ax.plot(x_values, fit_fn(x_values, *fit[0]), color="red", label="Best Fit")
        ax.legend()
        plt.show()

    return fit[0]


SAMPLES_PER_CYCLE = int(constants.SAMPLES_PER_CYCLE)
AMP_IDX = 0
FREQ_IDX = 1
PHASE_IDX = 2
OFFSET_IDX = 3


def frequency_per_cycle(data: np.ndarray) -> List[float]:
    """
    Calculates the fundamental frequency per cycle.
    :param data: Data to calculate frequency over.
    :return: A list of frequency calculations.
    """
    data_len = len(data)

    if data_len < SAMPLES_PER_CYCLE:
        return []

    res = []
    num_windows = data_len // SAMPLES_PER_CYCLE

    prev_fit: np.ndarray = np.array([])
    for i in range(num_windows):
        start_idx = i * SAMPLES_PER_CYCLE
        end_idx = start_idx + SAMPLES_PER_CYCLE
        window = data[start_idx:end_idx]

        if len(prev_fit) > 0:
            fit = fit_data(window,
                           amp_guess=prev_fit[AMP_IDX],
                           freq_guess=prev_fit[FREQ_IDX],
                           phase_guess=prev_fit[PHASE_IDX],
                           offset_guess=prev_fit[OFFSET_IDX])
            freq = fit[FREQ_IDX]
            prev_fit = fit
        else:
            fit = fit_data(window)
            freq = fit[FREQ_IDX]
            prev_fit = fit

        res.append(freq)

    return res
