from plugins.FrequencyVariationPlugin import frequency_variation
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
        self.freq_ref = constants.CYCLES_PER_SECOND
        self.config = load_config("../../config.json")
        self.freq_var_low = float(self.config["plugins.FrequencyVariationPlugin.frequency.variation.threshold.low"])
        self.freq_var_high = float(self.config["plugins.FrequencyVariationPlugin.frequency.variation.threshold.high"])
        self.freq_interruption = float(self.config["plugins.FrequencyVariationPlugin.frequency.interruption"])
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
        Test clean waveform
        :param
        """

        """MakaiEventPlugin frequency Method"""
        waveform_window = simulate_waveform()
        try:
            self.assertAlmostEqual(frequency(waveform_window), constants.CYCLES_PER_SECOND, delta=0.1)
        except AssertionError as err:
            self.AssertionErrors.append(str(err))

        """MakaiEventPlugin frequency_waveform Method & FrequencyVariationPlugin frequency_variation Method"""
        # 1 cycle no noise
        print("1 cycle no noise")
        waveform = simulate_waveform()
        windowed_frequencies = frequency_waveform(waveform)
        for freq in windowed_frequencies:
            message = "Frequency:{} Hz Expected:{} Hz".format(freq, constants.CYCLES_PER_SECOND)
            incident_type, variation = frequency_variation(freq, self.freq_ref, self.freq_var_high,
                                                           self.freq_var_low, self.freq_interruption)
            try:
                self.assertAlmostEqual(freq, constants.CYCLES_PER_SECOND, msg = message, delta = 0.1)
            except AssertionError as err:
                self.AssertionErrors.append(str(err))

            if incident_type:
                message = "Frequency:{} Hz Classified as {}".format(freq, incident_type.value)
            else:
                message = "Frequency:{} Hz No Frequency Variation".format(freq)
            try:
                self.assertEqual(incident_type, False, msg = message)
            except AssertionError as err:
                self.AssertionErrors.append(str(err))

            message = "Frequency Variation:{} Hz Expected:{} Hz".format(variation, 0.0)
            try:
                self.assertAlmostEqual(variation, 0.0, delta=0.1, msg=message)
            except AssertionError as err:
                self.AssertionErrors.append(str(err))

        # 1 cycles noise, variance = 1.0
        print("1 cycle noise, variance = 1.0")
        waveform = simulate_waveform(noise=True)
        windowed_frequencies = frequency_waveform(waveform)
        for freq in windowed_frequencies:
            message = "Frequency:{} Hz Expected:{} Hz".format(freq, constants.CYCLES_PER_SECOND)
            incident_type, variation = frequency_variation(freq, self.freq_ref, self.freq_var_high,
                                                           self.freq_var_low, self.freq_interruption)
            try:
                self.assertAlmostEqual(freq, constants.CYCLES_PER_SECOND, msg=message, delta=0.1)
            except AssertionError as err:
                self.AssertionErrors.append(str(err))

            if incident_type:
                message = "Frequency:{} Hz Classified as {}".format(freq, incident_type.value)
            else:
                message = "Frequency:{} Hz No Frequency Variation".format(freq)
            try:
                self.assertEqual(incident_type, False, msg=message)
            except AssertionError as err:
                self.AssertionErrors.append(str(err))

            message = "Frequency Variation:{} Hz Expected:{} Hz".format(variation, 0.0)
            try:
                self.assertAlmostEqual(variation, 0.0, delta=0.1, msg=message)
            except AssertionError as err:
                self.AssertionErrors.append(str(err))

        # 1 cycle noise, variance = 10.0
        print("1 cycle noise, variance = 10.0")
        waveform = simulate_waveform(noise=True, noise_variance=10.0)
        windowed_frequencies = frequency_waveform(waveform)
        for freq in windowed_frequencies:
            message = "Frequency:{} Hz Expected:{} Hz".format(freq, constants.CYCLES_PER_SECOND)
            incident_type, variation = frequency_variation(freq, self.freq_ref, self.freq_var_high,
                                                           self.freq_var_low, self.freq_interruption)
            try:
                self.assertAlmostEqual(freq, constants.CYCLES_PER_SECOND, msg=message, delta=0.1)
            except AssertionError as err:
                self.AssertionErrors.append(str(err))

            if incident_type:
                message = "Frequency:{} Hz Classified as {}".format(freq, incident_type.value)
            else:
                message = "Frequency:{} Hz No Frequency Variation".format(freq)
            try:
                self.assertEqual(incident_type, False, msg=message)
            except AssertionError as err:
                self.AssertionErrors.append(str(err))

            message = "Frequency Variation:{} Hz Expected:{} Hz".format(variation, 0.0)
            try:
                self.assertAlmostEqual(variation, 0.0, delta=0.1, msg=message)
            except AssertionError as err:
                self.AssertionErrors.append(str(err))

        # 1 cycle noise, variance = 100.0
        print("1 cycle noise, variance = 100.0")
        waveform = simulate_waveform(noise=True, noise_variance=100.0)
        windowed_frequencies = frequency_waveform(waveform)
        for freq in windowed_frequencies:
            message = "Frequency:{} Hz Expected:{} Hz".format(freq, constants.CYCLES_PER_SECOND)
            incident_type, variation = frequency_variation(freq, self.freq_ref, self.freq_var_high,
                                                           self.freq_var_low, self.freq_interruption)
            try:
                self.assertAlmostEqual(freq, constants.CYCLES_PER_SECOND, msg=message, delta=0.1)
            except AssertionError as err:
                self.AssertionErrors.append(str(err))

            if incident_type:
                message = "Frequency:{} Hz Classified as {}".format(freq, incident_type.value)
            else:
                message = "Frequency:{} Hz No Frequency Variation".format(freq)
            try:
                self.assertEqual(incident_type, False, msg=message)
            except AssertionError as err:
                self.AssertionErrors.append(str(err))

            message = "Frequency Variation:{} Hz Expected:{} Hz".format(variation, 0.0)
            try:
                self.assertAlmostEqual(variation, 0.0, delta=0.1, msg = message)
            except AssertionError as err:
                self.AssertionErrors.append(str(err))

        # 1 cycle noise, variance = 1000.0
        print("1 cycle noise, variance = 1000.0")
        waveform = simulate_waveform(noise=True, noise_variance=1000.0)
        windowed_frequencies = frequency_waveform(waveform)
        for freq in windowed_frequencies:
            message = "Frequency:{} Hz Expected:{} Hz".format(freq, constants.CYCLES_PER_SECOND)
            incident_type, variation = frequency_variation(freq, self.freq_ref, self.freq_var_high,
                                                           self.freq_var_low, self.freq_interruption)
            try:
                self.assertAlmostEqual(freq, constants.CYCLES_PER_SECOND, msg=message, delta=0.1)
            except AssertionError as err:
                self.AssertionErrors.append(str(err))

            if incident_type:
                message = "Frequency:{} Hz Classified as {}".format(freq, incident_type.value)
            else:
                message = "Frequency:{} Hz No Frequency Variation".format(freq)
            try:
                self.assertEqual(incident_type, False, msg=message)
            except AssertionError as err:
                self.AssertionErrors.append(str(err))

            message = "Frequency Variation:{} Hz Expected:{} Hz".format(variation, 0.0)
            try:
                self.assertAlmostEqual(variation, 0.0, delta=0.1, msg=message)
            except AssertionError as err:
                self.AssertionErrors.append(str(err))

        # 10 cycles no noise
        print("10 cycles no noise")
        waveform = simulate_waveform(num_samples=int(10*constants.SAMPLES_PER_CYCLE))
        windowed_frequencies = frequency_waveform(waveform)
        for freq in windowed_frequencies:
            message = "Frequency:{} Hz Expected:{} Hz".format(freq, constants.CYCLES_PER_SECOND)
            incident_type, variation = frequency_variation(freq, self.freq_ref, self.freq_var_high,
                                                           self.freq_var_low, self.freq_interruption)
            try:
                self.assertAlmostEqual(freq, constants.CYCLES_PER_SECOND, msg=message, delta=0.1)
            except AssertionError as err:
                self.AssertionErrors.append(str(err))

            if incident_type:
                message = "Frequency:{} Hz Classified as {}".format(freq, incident_type.value)
            else:
                message = "Frequency:{} Hz No Frequency Variation".format(freq)
            try:
                self.assertEqual(incident_type, False, msg=message)
            except AssertionError as err:
                self.AssertionErrors.append(str(err))

            message = "Frequency Variation:{} Hz Expected:{} Hz".format(variation, 0.0)
            try:
                self.assertAlmostEqual(variation, 0.0, delta=0.1, msg=message)
            except AssertionError as err:
                self.AssertionErrors.append(str(err))

        # 10 cycles noise, variance = 1.0
        print("10 cycles noise, variance = 1.0")
        waveform = simulate_waveform(num_samples=int(10*constants.SAMPLES_PER_CYCLE), noise=True)
        windowed_frequencies = frequency_waveform(waveform)
        for freq in windowed_frequencies:
            message = "Frequency:{} Hz Expected:{} Hz".format(freq, constants.CYCLES_PER_SECOND)
            incident_type, variation = frequency_variation(freq, self.freq_ref, self.freq_var_high,
                                                           self.freq_var_low, self.freq_interruption)
            try:
                self.assertAlmostEqual(freq, constants.CYCLES_PER_SECOND, msg=message, delta=0.1)
            except AssertionError as err:
                self.AssertionErrors.append(str(err))

            if incident_type:
                message = "Frequency:{} Hz Classified as {}".format(freq, incident_type.value)
            else:
                message = "Frequency:{} Hz No Frequency Variation".format(freq)
            try:
                self.assertEqual(incident_type, False, msg=message)
            except AssertionError as err:
                self.AssertionErrors.append(str(err))

            message = "Frequency Variation:{} Hz Expected:{} Hz".format(variation, 0.0)
            try:
                self.assertAlmostEqual(variation, 0.0, delta=0.1, msg=message)
            except AssertionError as err:
                self.AssertionErrors.append(str(err))

        # 10 cycles noise, variance = 10.0
        print("10 cycles noise, variance = 10.0")
        waveform = simulate_waveform(num_samples=int(10*constants.SAMPLES_PER_CYCLE), noise=True, noise_variance=10.0)
        windowed_frequencies = frequency_waveform(waveform)
        for freq in windowed_frequencies:
            message = "Frequency:{} Hz Expected:{} Hz".format(freq, constants.CYCLES_PER_SECOND)
            incident_type, variation = frequency_variation(freq, self.freq_ref, self.freq_var_high,
                                                           self.freq_var_low, self.freq_interruption)
            try:
                self.assertAlmostEqual(freq, constants.CYCLES_PER_SECOND, msg=message, delta=0.1)
            except AssertionError as err:
                self.AssertionErrors.append(str(err))

            if incident_type:
                message = "Frequency:{} Hz Classified as {}".format(freq, incident_type.value)
            else:
                message = "Frequency:{} Hz No Frequency Variation".format(freq)
            try:
                self.assertEqual(incident_type, False, msg=message)
            except AssertionError as err:
                self.AssertionErrors.append(str(err))

            message = "Frequency Variation:{} Hz Expected:{} Hz".format(variation, 0.0)
            try:
                self.assertAlmostEqual(variation, 0.0, delta=0.1, msg=message)
            except AssertionError as err:
                self.AssertionErrors.append(str(err))

        # 10 cycles noise, variance = 100.0
        print("10 cycles noise, variance = 100.0")
        waveform = simulate_waveform(num_samples=int(10*constants.SAMPLES_PER_CYCLE), noise=True, noise_variance=100.0)
        windowed_frequencies = frequency_waveform(waveform)
        for freq in windowed_frequencies:
            message = "Frequency:{} Hz Expected:{} Hz".format(freq, constants.CYCLES_PER_SECOND)
            incident_type, variation = frequency_variation(freq, self.freq_ref, self.freq_var_high,
                                                           self.freq_var_low, self.freq_interruption)
            try:
                self.assertAlmostEqual(freq, constants.CYCLES_PER_SECOND, msg=message, delta=0.1)
            except AssertionError as err:
                self.AssertionErrors.append(str(err))

            if incident_type:
                message = "Frequency:{} Hz Classified as {}".format(freq, incident_type.value)
            else:
                message = "Frequency:{} Hz No Frequency Variation".format(freq)
            try:
                self.assertEqual(incident_type, False, msg=message)
            except AssertionError as err:
                self.AssertionErrors.append(str(err))

            message = "Frequency Variation:{} Hz Expected:{} Hz".format(variation, 0.0)
            try:
                self.assertAlmostEqual(variation, 0.0, delta=0.1, msg=message)
            except AssertionError as err:
                self.AssertionErrors.append(str(err))

        # 10 cycles noise, variance = 1000.0
        print("10 cycles noise, variance = 100.0")
        waveform = simulate_waveform(num_samples=int(10*constants.SAMPLES_PER_CYCLE), noise=True, noise_variance=1000.0)
        windowed_frequencies = frequency_waveform(waveform)
        for freq in windowed_frequencies:
            message = "Frequency:{} Hz Expected:{} Hz".format(freq, constants.CYCLES_PER_SECOND)
            incident_type, variation = frequency_variation(freq, self.freq_ref, self.freq_var_high,
                                                           self.freq_var_low, self.freq_interruption)
            try:
                self.assertAlmostEqual(freq, constants.CYCLES_PER_SECOND, msg=message, delta=0.1)
            except AssertionError as err:
                self.AssertionErrors.append(str(err))

            if incident_type:
                message = "Frequency:{} Hz Classified as {}".format(freq, incident_type.value)
            else:
                message = "Frequency:{} Hz No Frequency Variation".format(freq)
            try:
                self.assertEqual(incident_type, False, msg=message)
            except AssertionError as err:
                self.AssertionErrors.append(str(err))

            message = "Frequency Variation:{} Hz Expected:{} Hz".format(variation, 0.0)
            try:
                self.assertAlmostEqual(variation, 0.0, delta=0.1, msg=message)
            except AssertionError as err:
                self.AssertionErrors.append(str(err))

        # 100 cycles no noise
        print("100 cycles no noise")
        waveform = simulate_waveform(num_samples=int(100*constants.SAMPLES_PER_CYCLE))
        windowed_frequencies = frequency_waveform(waveform)
        for freq in windowed_frequencies:
            message = "Frequency:{} Hz Expected:{} Hz".format(freq, constants.CYCLES_PER_SECOND)
            incident_type, variation = frequency_variation(freq, self.freq_ref, self.freq_var_high,
                                                           self.freq_var_low, self.freq_interruption)
            try:
                self.assertAlmostEqual(freq, constants.CYCLES_PER_SECOND, msg=message, delta=0.1)
            except AssertionError as err:
                self.AssertionErrors.append(str(err))

            if incident_type:
                message = "Frequency:{} Hz Classified as {}".format(freq, incident_type.value)
            else:
                message = "Frequency:{} Hz No Frequency Variation".format(freq)
            try:
                self.assertEqual(incident_type, False, msg=message)
            except AssertionError as err:
                self.AssertionErrors.append(str(err))

            message = "Frequency Variation:{} Hz Expected:{} Hz".format(variation, 0.0)
            try:
                self.assertAlmostEqual(variation, 0.0, delta=0.1, msg=message)
            except AssertionError as err:
                self.AssertionErrors.append(str(err))

        # 100 cycles noise, variance = 1.0
        print("100 cycles noise, variance = 1.0")
        waveform = simulate_waveform(num_samples=int(100*constants.SAMPLES_PER_CYCLE), noise=True)
        windowed_frequencies = frequency_waveform(waveform)
        for freq in windowed_frequencies:
            message = "Frequency:{} Hz Expected:{} Hz".format(freq, constants.CYCLES_PER_SECOND)
            incident_type, variation = frequency_variation(freq, self.freq_ref, self.freq_var_high,
                                                           self.freq_var_low, self.freq_interruption)
            try:
                self.assertAlmostEqual(freq, constants.CYCLES_PER_SECOND, msg=message, delta=0.1)
            except AssertionError as err:
                self.AssertionErrors.append(str(err))

            if incident_type:
                message = "Frequency:{} Hz Classified as {}".format(freq, incident_type.value)
            else:
                message = "Frequency:{} Hz No Frequency Variation".format(freq)
            try:
                self.assertEqual(incident_type, False, msg=message)
            except AssertionError as err:
                self.AssertionErrors.append(str(err))

            message = "Frequency Variation:{} Hz Expected:{} Hz".format(variation, 0.0)
            try:
                self.assertAlmostEqual(variation, 0.0, delta=0.1, msg=message)
            except AssertionError as err:
                self.AssertionErrors.append(str(err))

        # 100 cycles noise, variance = 10.0
        print("100 cycles noise, variance = 10.0")
        waveform = simulate_waveform(num_samples=int(100 * constants.SAMPLES_PER_CYCLE), noise=True,
                                     noise_variance=10.0)
        windowed_frequencies = frequency_waveform(waveform)
        for freq in windowed_frequencies:
            message = "Frequency:{} Hz Expected:{} Hz".format(freq, constants.CYCLES_PER_SECOND)
            incident_type, variation = frequency_variation(freq, self.freq_ref, self.freq_var_high,
                                                           self.freq_var_low, self.freq_interruption)
            try:
                self.assertAlmostEqual(freq, constants.CYCLES_PER_SECOND, msg=message, delta=0.1)
            except AssertionError as err:
                self.AssertionErrors.append(str(err))

            if incident_type:
                message = "Frequency:{} Hz Classified as {}".format(freq, incident_type.value)
            else:
                message = "Frequency:{} Hz No Frequency Variation".format(freq)
            try:
                self.assertEqual(incident_type, False, msg=message)
            except AssertionError as err:
                self.AssertionErrors.append(str(err))

            message = "Frequency Variation:{} Hz Expected:{} Hz".format(variation, 0.0)
            try:
                self.assertAlmostEqual(variation, 0.0, delta=0.1, msg=message)
            except AssertionError as err:
                self.AssertionErrors.append(str(err))

        # 100 cycles noise, variance = 100.0
        print("100 cycles noise, variance = 100.0")
        waveform = simulate_waveform(num_samples=int(100 * constants.SAMPLES_PER_CYCLE), noise=True,
                                     noise_variance=100.0)
        windowed_frequencies = frequency_waveform(waveform)
        for freq in windowed_frequencies:
            message = "Frequency:{} Hz Expected:{} Hz".format(freq, constants.CYCLES_PER_SECOND)
            incident_type, variation = frequency_variation(freq, self.freq_ref, self.freq_var_high,
                                                           self.freq_var_low, self.freq_interruption)
            try:
                self.assertAlmostEqual(freq, constants.CYCLES_PER_SECOND, msg=message, delta=0.1)
            except AssertionError as err:
                self.AssertionErrors.append(str(err))

            if incident_type:
                message = "Frequency:{} Hz Classified as {}".format(freq, incident_type.value)
            else:
                message = "Frequency:{} Hz No Frequency Variation".format(freq)
            try:
                self.assertEqual(incident_type, False, msg=message)
            except AssertionError as err:
                self.AssertionErrors.append(str(err))

            message = "Frequency Variation:{} Hz Expected:{} Hz".format(variation, 0.0)
            try:
                self.assertAlmostEqual(variation, 0.0, delta=0.1, msg=message)
            except AssertionError as err:
                self.AssertionErrors.append(str(err))

        # 100 cycles noise, variance = 1000.0
        print("100 cycles noise, variance = 100.0")
        waveform = simulate_waveform(num_samples=int(100 * constants.SAMPLES_PER_CYCLE), noise=True,
                                     noise_variance=1000.0)
        windowed_frequencies = frequency_waveform(waveform)
        for freq in windowed_frequencies:
            message = "Frequency:{} Hz Expected:{} Hz".format(freq, constants.CYCLES_PER_SECOND)
            incident_type, variation = frequency_variation(freq, self.freq_ref, self.freq_var_high,
                                                           self.freq_var_low, self.freq_interruption)
            try:
                self.assertAlmostEqual(freq, constants.CYCLES_PER_SECOND, msg=message, delta=0.1)
            except AssertionError as err:
                self.AssertionErrors.append(str(err))

            if incident_type:
                message = "Frequency:{} Hz Classified as {}".format(freq, incident_type.value)
            else:
                message = "Frequency:{} Hz No Frequency Variation".format(freq)
            try:
                self.assertEqual(incident_type, False, msg=message)
            except AssertionError as err:
                self.AssertionErrors.append(str(err))

            message = "Frequency Variation:{} Hz Expected:{} Hz".format(variation, 0.0)
            try:
                self.assertAlmostEqual(variation, 0.0, delta=0.1, msg=message)
            except AssertionError as err:
                self.AssertionErrors.append(str(err))

        # 1000 cycles no noise
        print("1000 cycles no noise")
        waveform = simulate_waveform(num_samples=int(1000 * constants.SAMPLES_PER_CYCLE))
        windowed_frequencies = frequency_waveform(waveform)
        for freq in windowed_frequencies:
            message = "Frequency:{} Hz Expected:{} Hz".format(freq, constants.CYCLES_PER_SECOND)
            incident_type, variation = frequency_variation(freq, self.freq_ref, self.freq_var_high,
                                                           self.freq_var_low, self.freq_interruption)
            try:
                self.assertAlmostEqual(freq, constants.CYCLES_PER_SECOND, msg=message, delta=0.1)
            except AssertionError as err:
                self.AssertionErrors.append(str(err))

            if incident_type:
                message = "Frequency:{} Hz Classified as {}".format(freq, incident_type.value)
            else:
                message = "Frequency:{} Hz No Frequency Variation".format(freq)
            try:
                self.assertEqual(incident_type, False, msg=message)
            except AssertionError as err:
                self.AssertionErrors.append(str(err))

            message = "Frequency Variation:{} Hz Expected:{} Hz".format(variation, 0.0)
            try:
                self.assertAlmostEqual(variation, 0.0, delta=0.1, msg=message)
            except AssertionError as err:
                self.AssertionErrors.append(str(err))

        # 1000 cycles noise, variance = 1.0
        print("1000 cycles noise, variance = 1.0")
        waveform = simulate_waveform(num_samples=int(1000 * constants.SAMPLES_PER_CYCLE), noise=True)
        windowed_frequencies = frequency_waveform(waveform)
        for freq in windowed_frequencies:
            message = "Frequency:{} Hz Expected:{} Hz".format(freq, constants.CYCLES_PER_SECOND)
            incident_type, variation = frequency_variation(freq, self.freq_ref, self.freq_var_high,
                                                           self.freq_var_low, self.freq_interruption)
            try:
                self.assertAlmostEqual(freq, constants.CYCLES_PER_SECOND, msg=message, delta=0.1)
            except AssertionError as err:
                self.AssertionErrors.append(str(err))

            if incident_type:
                message = "Frequency:{} Hz Classified as {}".format(freq, incident_type.value)
            else:
                message = "Frequency:{} Hz No Frequency Variation".format(freq)
            try:
                self.assertEqual(incident_type, False, msg=message)
            except AssertionError as err:
                self.AssertionErrors.append(str(err))

            message = "Frequency Variation:{} Hz Expected:{} Hz".format(variation, 0.0)
            try:
                self.assertAlmostEqual(variation, 0.0, delta=0.1, msg=message)
            except AssertionError as err:
                self.AssertionErrors.append(str(err))

        # 1000 cycles noise, variance = 10.0
        print("1000 cycles noise, variance = 10.0")
        waveform = simulate_waveform(num_samples=int(1000 * constants.SAMPLES_PER_CYCLE), noise=True,
                                     noise_variance=10.0)
        windowed_frequencies = frequency_waveform(waveform)
        for freq in windowed_frequencies:
            message = "Frequency:{} Hz Expected:{} Hz".format(freq, constants.CYCLES_PER_SECOND)
            incident_type, variation = frequency_variation(freq, self.freq_ref, self.freq_var_high,
                                                           self.freq_var_low, self.freq_interruption)
            try:
                self.assertAlmostEqual(freq, constants.CYCLES_PER_SECOND, msg=message, delta=0.1)
            except AssertionError as err:
                self.AssertionErrors.append(str(err))

            if incident_type:
                message = "Frequency:{} Hz Classified as {}".format(freq, incident_type.value)
            else:
                message = "Frequency:{} Hz No Frequency Variation".format(freq)
            try:
                self.assertEqual(incident_type, False, msg=message)
            except AssertionError as err:
                self.AssertionErrors.append(str(err))

            message = "Frequency Variation:{} Hz Expected:{} Hz".format(variation, 0.0)
            try:
                self.assertAlmostEqual(variation, 0.0, delta=0.1, msg=message)
            except AssertionError as err:
                self.AssertionErrors.append(str(err))

        # 1000 cycles noise, variance = 100.0
        print("1000 cycles noise, variance = 100.0")
        waveform = simulate_waveform(num_samples=int(1000 * constants.SAMPLES_PER_CYCLE), noise=True,
                                     noise_variance=100.0)
        windowed_frequencies = frequency_waveform(waveform)
        for freq in windowed_frequencies:
            message = "Frequency:{} Hz Expected:{} Hz".format(freq, constants.CYCLES_PER_SECOND)
            incident_type, variation = frequency_variation(freq, self.freq_ref, self.freq_var_high,
                                                           self.freq_var_low, self.freq_interruption)
            try:
                self.assertAlmostEqual(freq, constants.CYCLES_PER_SECOND, msg=message, delta=0.1)
            except AssertionError as err:
                self.AssertionErrors.append(str(err))

            if incident_type:
                message = "Frequency:{} Hz Classified as {}".format(freq, incident_type.value)
            else:
                message = "Frequency:{} Hz No Frequency Variation".format(freq)
            try:
                self.assertEqual(incident_type, False, msg=message)
            except AssertionError as err:
                self.AssertionErrors.append(str(err))

            message = "Frequency Variation:{} Hz Expected:{} Hz".format(variation, 0.0)
            try:
                self.assertAlmostEqual(variation, 0.0, delta=0.1, msg=message)
            except AssertionError as err:
                self.AssertionErrors.append(str(err))

        # 1000 cycles noise, variance = 1000.0
        print("1000 cycles noise, variance = 100.0")
        waveform = simulate_waveform(num_samples=int(1000 * constants.SAMPLES_PER_CYCLE), noise=True,
                                     noise_variance=1000.0)
        windowed_frequencies = frequency_waveform(waveform)
        for freq in windowed_frequencies:
            message = "Frequency:{} Hz Expected:{} Hz".format(freq, constants.CYCLES_PER_SECOND)
            incident_type, variation = frequency_variation(freq, self.freq_ref, self.freq_var_high,
                                                           self.freq_var_low, self.freq_interruption)
            try:
                self.assertAlmostEqual(freq, constants.CYCLES_PER_SECOND, msg=message, delta=0.1)
            except AssertionError as err:
                self.AssertionErrors.append(str(err))

            if incident_type:
                message = "Frequency:{} Hz Classified as {}".format(freq, incident_type.value)
            else:
                message = "Frequency:{} Hz No Frequency Variation".format(freq)
            try:
                self.assertEqual(incident_type, False, msg=message)
            except AssertionError as err:
                self.AssertionErrors.append(str(err))

            message = "Frequency Variation:{} Hz Expected:{} Hz".format(variation, 0.0)
            try:
                self.assertAlmostEqual(variation, 0.0, delta=0.1, msg=message)
            except AssertionError as err:
                self.AssertionErrors.append(str(err))


    # def test_frequency_swell(self):
    #     """
    #     Test frequency_swell
    #     :param
    #     """
    #
    #     """MakaiEventPlugin frequency Method"""
    #     #60.1Hz threshold for frequency swell, no noise
    #     waveform_window = simulate_waveform(frequency=60.1)
    #     self.assertAlmostEqual(frequency(waveform_window), 60.1, delta=0.1)
    #
    #     #60.25Hz frequency swell, no noise
    #     waveform_window = simulate_waveform(frequency=60.1)
    #     self.assertAlmostEqual(frequency(waveform_window), 60.1, delta=0.1)
    #
    # def test_frequency_interruption(self):
    #
    #
    # def test_frequency_dip(self):

def run():
    unittest.main()