from plugins.transient_plugin import transient_sliding_window
from plugins.transient_plugin import transient_incident_classifier
from plugins.transient_plugin import multiple_zero_xing_classifier
from plugins.transient_plugin import arcing_classifier
from plugins.transient_plugin import impulsive_classifier
from plugins.transient_plugin import oscillatory_classifier
from plugins.transient_plugin import find_zero_xings
from plugins.transient_plugin import noise_canceler
from plugins.transient_plugin import periodic_notching_classifier
from plugins.transient_plugin import waveform_filter
from opq_mauka import load_config

import unittest
import numpy
import constants
from scipy import signal


def simulate_waveform(freq: float=constants.CYCLES_PER_SECOND, vrms: float = 120.0, noise: bool = False,
                      noise_variance: float = 1.0, num_samples: int = int(6 * constants.SAMPLES_PER_CYCLE),
                      sample_rate=constants.SAMPLE_RATE_HZ, rnd_seed=0) -> numpy.ndarray:

    rand = numpy.random.RandomState(seed=rnd_seed)

    if not noise:
        return numpy.sqrt(2) * vrms * numpy.sin([freq * 2 * numpy.pi * x / sample_rate for x in range(num_samples)])
    else:
        return numpy.sqrt(2) * vrms * numpy.sin([freq * 2 * numpy.pi * x / sample_rate for x in range(num_samples)]
                                                ) + numpy.sqrt(noise_variance) * rand.randn(1, num_samples)[0]

class TransientPluginTests(unittest.TestCase):

    def setUp(self):
        self.config = load_config("./config.json")
        self.noise_floor = float(self.config["plugins.TransientPlugin.noise.floor"])
        self.filter_order = int(self.config["plugins.MakaiEventPlugin.filterOrder"])
        self.cutoff_frequency = float(self.config["plugins.MakaiEventPlugin.cutoffFrequency"])

    def test_periodic_notching_transient(self):
        """
        test transient plugin functions on waveform with periodic notching
        :return: None
        """

        # 6 cycles no noise notching amp = 3 * (noise floor) with 1440 Hz frequency, i.e. 24 notches per cycle
        fundamental_waveform = simulate_waveform()
        t = numpy.linspace(0, 1, int(6 * constants.SAMPLES_PER_CYCLE))
        transient_waveform = 3 / 2 * self.noise_floor * signal.sawtooth(
            2 * numpy.pi * 1440 * t) + 3 / 2 * self.noise_floor

        # ensure that notching is negative power
        transient_waveform = - transient_waveform * numpy.sign(fundamental_waveform)

        raw_waveform = fundamental_waveform + transient_waveform

        waveforms = waveform_filter(raw_waveform, self.filter_order, self.cutoff_frequency)

        periodic_notching = periodic_notching_classifier(waveforms["filtered_waveform"],
                                                         waveforms["fundamental_waveform"], self.config)



