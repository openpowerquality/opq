import datetime
import math
import typing

import gridfs
import numpy as np
import pymongo

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
    "OUTAGE": "Outage"
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

