import math

import numpy
import scipy
import scipy.fftpack

import analysis
import constants




def thd(waveform: numpy.ndarray) -> float:
    """
    Calculated THD by first taking the FFT and then taking the peaks of the harmonics (sans the fundamental).
    :param waveform:
    :return:
    """
    y = scipy.fftpack.fft(waveform)
    x = numpy.fft.fftfreq(y.size, 1 / constants.SAMPLE_RATE_HZ)

    new_x = []
    new_y = []
    for i in range(len(x)):
        if x[i] >= 0:
            new_x.append(x[i])
            new_y.append(y[i])

    new_x = numpy.array(new_x)
    new_y = numpy.abs(numpy.array(new_y))

    nth_harmonic = {
        1: new_y[analysis.closest_idx(new_x, 60.0)],
        2: new_y[analysis.closest_idx(new_x, 120.0)],
        3: new_y[analysis.closest_idx(new_x, 180.0)],
        4: new_y[analysis.closest_idx(new_x, 240.0)],
        5: new_y[analysis.closest_idx(new_x, 300.0)],
        6: new_y[analysis.closest_idx(new_x, 360.0)],
        7: new_y[analysis.closest_idx(new_x, 420.0)]
    }

    top = analysis.sq(nth_harmonic[2]) + analysis.sq(nth_harmonic[3]) + analysis.sq(nth_harmonic[4]) + analysis.sq(nth_harmonic[5])
    _thd = (math.sqrt(top) / nth_harmonic[1]) * 100.0
    return _thd