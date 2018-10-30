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

def periodic_notching_transient_wave_filter(voltage, noise_floor):
    if abs(voltage) < noise_floor:
        return 0
    else:
        if voltage < 0:
            return voltage + noise_floor
        else:
            return voltage - noise_floor


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
        self.configs = {
            "noise_floor": float(self.config["plugins.TransientPlugin.noise.floor"]),
            "filter_cutoff_frequency": float(self.config["plugins.MakaiEventPlugin.cutoffFrequency"]),
            "filter_order": float(self.config["plugins.MakaiEventPlugin.filterOrder"]),
            "oscillatory_min_cycles": int(self.config["plugins.TransientPlugin.oscillatory.min.cycles"]),
            "oscillatory_low_freq_max": float(self.config["plugins.TransientPlugin.oscillatory.low.freq.max.hz"]),
            "oscillatory_med_freq_max": float(self.config["plugins.TransientPlugin.oscillatory.med.freq.max.hz"]),
            "oscillatory_high_freq_max": float(self.config["plugins.TransientPlugin.oscillatory.high.freq.max.hz"]),
            "arc_zero_xing_threshold": int(self.config["plugins.TransientPlugin.arcing.zero.crossing.threshold"]),
            "pf_cap_switch_low_ratio": float(self.config["plugins.TransientPlugin.PF.cap.switching.low.ratio"]),
            "pf_cap_switch_high_ratio": float(self.config["plugins.TransientPlugin.PF.cap.switching.high.ratio"]),
            "pf_cap_switch_low_freq": float(self.config["plugins.TransientPlugin.PF.cap.switching.low.freq.hz"]),
            "pf_cap_switch_high_freq": float(self.config["plugins.TransientPlugin.PF.cap.switching.high.freq.hz"]),
            "max_lull_ms": float(self.config["plugins.TransientPlugin.max.lull.ms"]),
            "max_std_periodic_notching": float(
                self.config["plugins.TransientPlugin.max.periodic.notching.std.dev"]),
            "auto_corr_thresh_periodicity": float(
                self.config["plugins.TransientPlugin.auto.corr.thresh.periodicity"])
        }

    def test_periodic_notching_transient(self):
        """
        test transient plugin functions on waveform with periodic notching
        :return: None
        """

        # 6 cycles notching amp = 3 * (noise floor) with frequency 1440Hz i.e.e 24 notches per cycle for 1 cycle
        fundamental_waveform = simulate_waveform()
        t = numpy.linspace(0, 1 / 10, int(6 * constants.SAMPLES_PER_CYCLE))
        transient_waveform = 8 / 2 * self.noise_floor * signal.sawtooth(
            2 * numpy.pi * 1440 * t) + 8 / 2 * self.noise_floor

        # ensure that notching is negative power
        transient_waveform = - transient_waveform * numpy.sign(fundamental_waveform)

        # ensure gaps in notching
        transient_waveform = numpy.vectorize(periodic_notching_transient_wave_filter)(transient_waveform,
                                                                                      32)

        raw_waveform_transient_window = fundamental_waveform[600:800] + transient_waveform[600:800]

        raw_waveform = numpy.concatenate((fundamental_waveform[:600], raw_waveform_transient_window,
                                         fundamental_waveform[800:]))

        # first ensure that if transient and fundamental wave were recovered perfectly
        # then we could classify periodic notching
        periodic_notching = periodic_notching_classifier(fundamental_waveform - raw_waveform,
                                                         fundamental_waveform, self.configs)

        self.assertTrue(periodic_notching[0])

        waveforms = waveform_filter(raw_waveform, self.filter_order, self.cutoff_frequency)

        periodic_notching = periodic_notching_classifier(waveforms["filtered_waveform"],
                                                         waveforms["fundamental_waveform"], self.configs)

        self.assertTrue(periodic_notching[0])


