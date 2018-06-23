import plugins.FrequencyVariationPlugin
from plugins.FrequencyVariationPlugin import FrequencyVariationPlugin

import sys
import unittest
import numpy
import constants
import csv

def simulate_waveform(frequency: float = 60.0, vrms: float = 120.0, noise: bool = False,
                      num_samples: int = int(constants.SAMPLES_PER_CYCLE),
                      sample_rate = constants.SAMPLE_RATE_HZ) -> numpy.ndarray:
    if not noise:
        return numpy.sqrt(2) * vrms * numpy.sin([frequency * 2 * numpy.pi * x / sample_rate
                                             for x in range(num_samples)])
    else:
        return numpy.sqrt(2) * vrms * numpy.sin([frequency * 2 * numpy.pi * x / sample_rate
                                                 for x in range(num_samples)]) + numpy.random.randn(num_samples)

def read_waveform(filename: str) -> numpy.ndarray:
    try:
        waveform = []
        with open(filename, 'rt') as csv_file:
            reader = csv.reader(csv_file)
            for row in reader:
                waveform.append(float(row[0]))
        return numpy.array(waveform)
    except FileNotFoundError as err:
        print(err)
        return None

class FrequencyVariationPluginTests(unittest.TestCase):

    def test_no_variation(self):


    def test_frequency_swell(self):


    def test_frequency_interruption(self):


    def test_frequency_dip(self):