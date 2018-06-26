from OpqMauka import load_config
from plugins.MakaiEventPlugin import frequency_waveform
from plugins.MakaiEventPlugin import frequency

import unittest
import numpy
import constants
import csv


def simulate_waveform(frequency: float = constants.CYCLES_PER_SECOND, vrms: float = 120.0, noise: bool = False,
                      noise_variance: float = 1.0, num_samples: int = int(constants.SAMPLES_PER_CYCLE),
                      sample_rate = constants.SAMPLE_RATE_HZ) -> numpy.ndarray:

    if not noise:
        return numpy.sqrt(2) * vrms * numpy.sin([frequency * 2 * numpy.pi * x / sample_rate
                                             for x in range(num_samples)])
    else:
        return numpy.sqrt(2) * vrms * numpy.sin([frequency * 2 * numpy.pi * x / sample_rate for x in range(num_samples)]
                                                ) + numpy.sqrt(noise_variance) * numpy.random.randn(num_samples)


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


class FrequencyVariationTests(unittest.TestCase):

    def setUp(self):
        self.AssertionErrors = []

    def tearDown(self):
        err_count = 0
        with open("test_out.txt", "w") as outFile:
            for err in self.AssertionErrors:
                outFile.write(err)
                outFile.write('\n')
                err_count = err_count + 1

        print("Num Errors: {}".format(err_count))

    def test_no_variation(self):
        """
        Test 60Hz waveform
        :param
        """

        """MakaiEventPlugin frequency Method"""
        waveform_window = simulate_waveform()
        try:
            self.assertAlmostEqual(frequency(waveform_window), constants.CYCLES_PER_SECOND, delta=0.1)
        except AssertionError as err:
            self.AssertionErrors.append(str(err))

        """MakaiEventPlugin frequency_waveform Method"""
        # 1 cycle no noise
        print("1 cycle no noise")
        waveform = simulate_waveform()
        windowed_frequencies = frequency_waveform(waveform)
        for freq in windowed_frequencies:
            message = "Frequency:{} Hz Expected:{} Hz".format(freq, constants.CYCLES_PER_SECOND)

            try:
                self.assertAlmostEqual(freq, constants.CYCLES_PER_SECOND, msg=message, delta = 0.2)
            except AssertionError as err:
                self.AssertionErrors.append(str(err))

        # 1 cycles noise, variance = 1.0
        print("1 cycle noise, variance = 1.0")
        waveform = simulate_waveform(noise=True)
        windowed_frequencies = frequency_waveform(waveform)
        for freq in windowed_frequencies:
            message = "Frequency:{} Hz Expected:{} Hz".format(freq, constants.CYCLES_PER_SECOND)

            try:
                self.assertAlmostEqual(freq, constants.CYCLES_PER_SECOND, msg=message, delta=0.2)
            except AssertionError as err:
                self.AssertionErrors.append(str(err))

        # 1 cycles noise, variance = 10.0
        print("1 cycle noise, variance = 10.0")
        waveform = simulate_waveform(noise=True, noise_variance=10.0)
        windowed_frequencies = frequency_waveform(waveform)
        for freq in windowed_frequencies:
            message = "Frequency:{} Hz Expected:{} Hz".format(freq, constants.CYCLES_PER_SECOND)

            try:
                self.assertAlmostEqual(freq, constants.CYCLES_PER_SECOND, msg=message, delta=0.2)
            except AssertionError as err:
                self.AssertionErrors.append(str(err))

        # 10 cycles noise, variance = 10.0
        print("10 cycles noise, variance = 10.0")
        waveform = simulate_waveform(noise=True, noise_variance=10.0, num_samples=int(10*constants.SAMPLES_PER_CYCLE))
        windowed_frequencies = frequency_waveform(waveform)
        for freq in windowed_frequencies:
            message = "Frequency:{} Hz Expected:{} Hz".format(freq, constants.CYCLES_PER_SECOND)

            try:
                self.assertAlmostEqual(freq, constants.CYCLES_PER_SECOND, msg=message, delta=0.2)
            except AssertionError as err:
                self.AssertionErrors.append(str(err))