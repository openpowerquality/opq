import datetime
import math
import typing
from typing import List, Optional

import gridfs
import numpy as np
import pymongo
import scipy.fftpack as fft
import scipy.optimize

import reports.constants as constants

SAMPLES_PER_CYCLE = 200.0
"""Number of samples per electrical cycle for OPQ box"""

SAMPLES_PER_MILLISECOND = 12.0

SAMPLE_RATE_HZ = 12000.0
"""Sample rate of OPQ box"""

CYCLES_PER_SECOND = 60.0
"""Cycles per second"""

CYCLES_PER_MILLISECOND = 0.06

MILLISECONDS_PER_SECOND = 1000.0

NOMINAL_VRMS = 120.0

box_to_location: typing.Dict[str, str] = {
    "1000": "POST 1",
    "1001": "Hamilton",
    "1002": "POST 2",
    "1003": "LAVA Lab",
    "1005": "Parking Structure Ph II",
    "1006": "Frog 1",
    "1007": "Frog 2",
    "1008": "Mile's Office",
    "1009": "Watanabe",
    "1010": "Holmes",
    "1021": "Marine Science Building",
    "1022": "Ag. Engineering",
    "1023": "Law Library",
    "1024": "IT Building",
    "1025": "Kennedy Theater"
}

boxes = [k for k in box_to_location]

incident_map: typing.Dict[str, str] = {
    "FREQUENCY_SWELL": "F Swell",
    "FREQUENCY_SAG": "F Sag",
    "FREQUENCY_INTERRUPTION": "F Int",
    "VOLTAGE_SAG": "V Sag",
    "OUTAGE": "Outage",
    "EXCESSIVE_THD": "THD"
}


def any_of_in(a: typing.List, b: typing.List) -> bool:
    a = set(a)
    b = set(b)
    return len(a.intersection(b)) > 0


def fmt_ts_by_hour(ts_s: int) -> str:
    dt = datetime.datetime.utcfromtimestamp(ts_s)
    return dt.strftime("%Y-%m-%d")


def to_s16bit(data: bytes) -> np.ndarray:
    """
    Converts raw bytes into an array of 16 bit integers.
    :param data:
    :return:
    """
    return np.frombuffer(data, np.int16)


def calibration_constant(box_id: str,
                         mongo_client: pymongo.MongoClient) -> float:
    return mongo_client.opq.opq_boxes.find_one({"box_id": box_id},
                                               projection={"_id": False,
                                                           "box_id": True,
                                                           "calibration_constant": True})["calibration_constant"]


def calib_waveform(file: str,
                   box_id: str,
                   mongo_client: pymongo.MongoClient) -> np.ndarray:
    fs = gridfs.GridFS(mongo_client.opq)
    waveform = fs.find_one({"filename": file}).read()
    waveform = to_s16bit(waveform).astype(np.int64)
    return waveform / calibration_constant(box_id, mongo_client)


def sample_to_ms(sample: int) -> float:
    return sample / 12.0

def vrms(samples: np.ndarray) -> float:
    """
    Calculates the Voltage root-mean-square of the supplied samples
    :param samples: Samples to calculate Vrms over.
    :return: The Vrms value of the provided samples.
    """
    summed_sqs = np.sum(np.square(samples))
    return math.sqrt(summed_sqs / len(samples))


def vrms_waveform(waveform: np.ndarray, window_size: int = 200) -> np.ndarray:
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

    return np.array(rms_voltages)

def percent_nominal(nominal: float, actual: float) -> float:
    return actual / nominal * 100.0


def perecent_nominal_from_zero(nominal: float, actual: float) -> float:
    return percent_nominal(nominal, actual) - 100.0


def cycles_to_s(cycles: float) -> float:
    return cycles / 60.0


def ms_to_s(ms: float) -> float:
    return ms / 1000.0


def ms_to_c(duration_ms: float) -> float:
    """
    Convert a duration in milliseconds to cycles.
    :param duration_ms: milliseconds
    :return: cycles
    """
    return duration_ms * CYCLES_PER_MILLISECOND


def s_to_c(s: float) -> float:
    return s * 1000.0 * 60.0

def ms_to_samples(ms: float) -> float:
    return ms * 12.0

def samples_to_cycles(samples: float) -> float:
    return samples / 200.0

def cycles_to_samples(cycles: float) -> float:
    return cycles * 200.0

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

    # if do_plot:
    #     _, ax = plt.subplots(1, 1, figsize=(16, 9))
    #     ax.scatter(x_values, y_values, color="blue", label="Data", linewidths=.1)
    #     ax.plot(x_values, fit_fn(x_values, amp_guess, freq_guess, phase_guess, offset_guess), color="green",
    #             label="Best Guess")
    #     ax.plot(x_values, fit_fn(x_values, *fit[0]), color="red", label="Best Fit")
    #     ax.legend()
    #     plt.show()

    return fit[0]


SAMPLES_PER_CYCLE = int(constants.SAMPLES_PER_CYCLE)
AMP_IDX = 0
FREQ_IDX = 1
PHASE_IDX = 2
OFFSET_IDX = 3


def frequency_per_cycle(data: np.ndarray,
                        do_plot: bool = False) -> List[float]:
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
                           offset_guess=prev_fit[OFFSET_IDX],
                           do_plot=do_plot)
            freq = fit[FREQ_IDX]
            prev_fit = fit
        else:
            fit = fit_data(window)
            freq = fit[FREQ_IDX]
            prev_fit = fit

        res.append(freq)

    return res
