from plugins.makai_event_plugin import frequency_waveform
from plugins.makai_event_plugin import frequency
import config

import unittest
import numpy
import constants
import csv


def simulate_waveform(freq: float=constants.CYCLES_PER_SECOND, vrms: float = 120.0, noise: bool = False,
                      noise_variance: float = 1.0, num_samples: int = int(6 * constants.SAMPLES_PER_CYCLE),
                      sample_rate=constants.SAMPLE_RATE_HZ, rnd_seed=0) -> numpy.ndarray:

    rand = numpy.random.RandomState(seed=rnd_seed)

    if not noise:
        return numpy.sqrt(2) * vrms * numpy.sin([freq * 2 * numpy.pi * x / sample_rate for x in range(num_samples)])
    else:
        return numpy.sqrt(2) * vrms * numpy.sin([freq * 2 * numpy.pi * x / sample_rate for x in range(num_samples)]
                                                ) + numpy.sqrt(noise_variance) * rand.randn(1, num_samples)[0]


def read_waveform(filename: str):

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


class MakaiEventPluginTests(unittest.TestCase):

    def setUp(self):
        self.freq_ref = constants.CYCLES_PER_SECOND
        self.config = config.from_env(constants.CONFIG_ENV)
        self.window_size = int(self.config["plugins.MakaiEventPlugin.frequencyWindowCycles"]
                               * constants.SAMPLES_PER_CYCLE)
        self.downsample_factor = int(self.config["plugins.MakaiEventPlugin.frequencyDownSampleRate"])

    def test_frequency_no_variation(self):
        """
        Test 60Hz waveform
        :param
        """

        """MakaiEventPlugin frequency Method"""
        waveform_window = simulate_waveform()
        self.assertAlmostEqual(frequency(waveform_window, down_sample_factor=1),
                               constants.CYCLES_PER_SECOND, delta=0.2)

        """MakaiEventPlugin frequency_waveform Method"""
        # 1 cycles no noise
        waveform = simulate_waveform(num_samples=int(2*constants.SAMPLES_PER_CYCLE))
        windowed_frequencies = frequency_waveform(waveform, self.window_size,
                                                  filter_order=self.config["plugins.MakaiEventPlugin.filterOrder"],
                                                  cutoff_frequency=
                                                  self.config["plugins.MakaiEventPlugin.cutoffFrequency"],
                                                  down_sample_factor=self.downsample_factor)
        for freq in windowed_frequencies:
            message = "Frequency:{} Hz Expected:{} Hz".format(freq, constants.CYCLES_PER_SECOND)
            self.assertAlmostEqual(freq, constants.CYCLES_PER_SECOND, msg=message, delta=0.2)

        # 100 cycles no noise
        waveform = simulate_waveform(num_samples=int(100*constants.SAMPLES_PER_CYCLE))
        windowed_frequencies = frequency_waveform(waveform, self.window_size,
                                                  filter_order=self.config["plugins.MakaiEventPlugin.filterOrder"],
                                                  cutoff_frequency=
                                                  self.config["plugins.MakaiEventPlugin.cutoffFrequency"],
                                                  down_sample_factor=self.downsample_factor)
        for freq in windowed_frequencies:
            message = "Frequency:{} Hz Expected:{} Hz".format(freq, constants.CYCLES_PER_SECOND)
            self.assertAlmostEqual(freq, constants.CYCLES_PER_SECOND, msg=message, delta=0.2)

        # # 1 cycles noise, variance = 1.0
        waveform = simulate_waveform(noise=True)
        windowed_frequencies = frequency_waveform(waveform, self.window_size,
                                                  filter_order=self.config["plugins.MakaiEventPlugin.filterOrder"],
                                                  cutoff_frequency=
                                                  self.config["plugins.MakaiEventPlugin.cutoffFrequency"],
                                                  down_sample_factor=self.downsample_factor)
        for freq in windowed_frequencies:
            message = "Frequency:{} Hz Expected:{} Hz".format(freq, constants.CYCLES_PER_SECOND)
            self.assertAlmostEqual(freq, constants.CYCLES_PER_SECOND, msg=message, delta=0.2)

        # 1 cycles noise, variance = 10.0
        waveform = simulate_waveform(noise=True, noise_variance=10.0)
        windowed_frequencies = frequency_waveform(waveform, self.window_size,
                                                  filter_order=self.config["plugins.MakaiEventPlugin.filterOrder"],
                                                  cutoff_frequency=
                                                  self.config["plugins.MakaiEventPlugin.cutoffFrequency"],
                                                  down_sample_factor=self.downsample_factor)
        for freq in windowed_frequencies:
            message = "Frequency:{} Hz Expected:{} Hz".format(freq, constants.CYCLES_PER_SECOND)
            self.assertAlmostEqual(freq, constants.CYCLES_PER_SECOND, msg=message, delta=0.2)

        # 10 cycles noise, variance = 10.0
        waveform = simulate_waveform(noise=True, noise_variance=10.0, num_samples=int(10*constants.SAMPLES_PER_CYCLE))
        windowed_frequencies = frequency_waveform(waveform, self.window_size,
                                                  filter_order=self.config["plugins.MakaiEventPlugin.filterOrder"],
                                                  cutoff_frequency=
                                                  self.config["plugins.MakaiEventPlugin.cutoffFrequency"],
                                                  down_sample_factor=self.downsample_factor)
        for freq in windowed_frequencies:
            message = "Frequency:{} Hz Expected:{} Hz".format(freq, constants.CYCLES_PER_SECOND)
            self.assertAlmostEqual(freq, constants.CYCLES_PER_SECOND, msg=message, delta=0.2)

        # 100 cycles no noise, frequency = 59.0
        waveform = simulate_waveform(freq=59.0, noise=False, num_samples=int(100*constants.SAMPLES_PER_CYCLE))
        windowed_frequencies = frequency_waveform(waveform, self.window_size,
                                                  filter_order=self.config["plugins.MakaiEventPlugin.filterOrder"],
                                                  cutoff_frequency=
                                                  self.config["plugins.MakaiEventPlugin.cutoffFrequency"],
                                                  down_sample_factor=self.downsample_factor)
        for freq in windowed_frequencies:
            message = "Frequency:{} Hz Expected:{} Hz".format(freq, 59.0)
            self.assertAlmostEqual(freq, 59.0, msg=message, delta=0.2)