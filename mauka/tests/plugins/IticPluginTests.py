import unittest

import analysis
from plugins.IticPlugin import IticRegion, itic_region


def percent_nominal_to_rms(percent_nominal: float) -> float:
    return (percent_nominal * 120.0) / 100


class IticPluginTests(unittest.TestCase):

    def test_itic_region_very_short_duration(self):
        """
        Any duration less than 0.01 cycles are short enough that they should
        always return no interruption irrelevant of the voltage.
        """
        short_duration = analysis.c_to_ms(0.009)
        self.assertEqual(IticRegion.NO_INTERRUPTION, itic_region(percent_nominal_to_rms(120), short_duration))
        self.assertEqual(IticRegion.NO_INTERRUPTION, itic_region(percent_nominal_to_rms(400), short_duration))
        self.assertEqual(IticRegion.NO_INTERRUPTION, itic_region(percent_nominal_to_rms(4000), short_duration))
        self.assertEqual(IticRegion.NO_INTERRUPTION, itic_region(percent_nominal_to_rms(0), short_duration))

    def test_itic_region_0_rms(self):
        """
        The ITIC curve defines two separate regions at 0 (or less) depending on duration.
        """
        self.assertEqual(IticRegion.NO_INTERRUPTION, itic_region(0, 0))
        self.assertEqual(IticRegion.NO_INTERRUPTION, itic_region(0, 10))
        self.assertEqual(IticRegion.NO_INTERRUPTION, itic_region(0, 20))
        self.assertEqual(IticRegion.NO_DAMAGE, itic_region(0, 21))
        self.assertEqual(IticRegion.NO_DAMAGE, itic_region(0, 20000000))

    def test_itic_region_nominal(self):
        """
        Every RMS value with percent nominal between 90 and 110 percent should return no interruption irrelevant of
        duration.
        """
        self.assertEqual(IticRegion.NO_INTERRUPTION, itic_region(percent_nominal_to_rms(109.99), 0))
        self.assertEqual(IticRegion.NO_INTERRUPTION, itic_region(percent_nominal_to_rms(109.99), 3))
        self.assertEqual(IticRegion.NO_INTERRUPTION, itic_region(percent_nominal_to_rms(109.99), 500))
        self.assertEqual(IticRegion.NO_INTERRUPTION, itic_region(percent_nominal_to_rms(109.99), 10000))
        self.assertEqual(IticRegion.NO_INTERRUPTION, itic_region(percent_nominal_to_rms(109.99), 1000000))

        self.assertEqual(IticRegion.NO_INTERRUPTION, itic_region(percent_nominal_to_rms(90.01), 0))
        self.assertEqual(IticRegion.NO_INTERRUPTION, itic_region(percent_nominal_to_rms(90.01), 3))
        self.assertEqual(IticRegion.NO_INTERRUPTION, itic_region(percent_nominal_to_rms(90.01), 500))
        self.assertEqual(IticRegion.NO_INTERRUPTION, itic_region(percent_nominal_to_rms(90.01), 10000))
        self.assertEqual(IticRegion.NO_INTERRUPTION, itic_region(percent_nominal_to_rms(90.01), 1000000))

    def test_itic_region_prohibited(self):
        """
        All test results should return a prohibited ITIC region. First we'll test a few that are clearly prohibited
        and then we will probe around the edge of the prohibited region to test edge cases.
        """
        self.assertEqual(IticRegion.PROHIBITED, itic_region(percent_nominal_to_rms(300), 500))
        self.assertEqual(IticRegion.PROHIBITED, itic_region(percent_nominal_to_rms(600), 3))
        self.assertEqual(IticRegion.PROHIBITED, itic_region(percent_nominal_to_rms(140), 20))
        self.assertEqual(IticRegion.PROHIBITED, itic_region(percent_nominal_to_rms(500), analysis.c_to_ms(.02)))
        self.assertEqual(IticRegion.PROHIBITED, itic_region(percent_nominal_to_rms(200), 1))
        self.assertEqual(IticRegion.PROHIBITED, itic_region(percent_nominal_to_rms(140), 3))
        self.assertEqual(IticRegion.PROHIBITED, itic_region(percent_nominal_to_rms(121), 3))
        self.assertEqual(IticRegion.PROHIBITED, itic_region(percent_nominal_to_rms(120), 500))
        self.assertEqual(IticRegion.PROHIBITED, itic_region(percent_nominal_to_rms(110), 501))
        self.assertEqual(IticRegion.PROHIBITED, itic_region(percent_nominal_to_rms(110), 501))
        self.assertEqual(IticRegion.PROHIBITED, itic_region(percent_nominal_to_rms(110), 1000000))
        self.assertEqual(IticRegion.PROHIBITED, itic_region(percent_nominal_to_rms(10000), analysis.c_to_ms(.02)))

    def test_itic_region_no_damange(self):
        """
        All test results should return a prohibited ITIC region. First we'll test a few that are clearly prohibited
        and then we will probe around the edge of the prohibited region to test edge cases.
        """
        self.assertEqual(IticRegion.NO_DAMAGE, itic_region(percent_nominal_to_rms(40), 500))
        self.assertEqual(IticRegion.NO_DAMAGE, itic_region(percent_nominal_to_rms(40), 1000000))
        self.assertEqual(IticRegion.NO_DAMAGE, itic_region(percent_nominal_to_rms(70), 10000))
        self.assertEqual(IticRegion.NO_DAMAGE, itic_region(percent_nominal_to_rms(70), 500))
        self.assertEqual(IticRegion.NO_DAMAGE, itic_region(percent_nominal_to_rms(70), 20.1))
        self.assertEqual(IticRegion.NO_DAMAGE, itic_region(percent_nominal_to_rms(80), 500.1))
        self.assertEqual(IticRegion.NO_DAMAGE, itic_region(percent_nominal_to_rms(90), 10000.1))
        self.assertEqual(IticRegion.NO_DAMAGE, itic_region(percent_nominal_to_rms(90), 1000000))
        self.assertEqual(IticRegion.NO_DAMAGE, itic_region(percent_nominal_to_rms(40), 20.1))
        self.assertEqual(IticRegion.NO_DAMAGE, itic_region(percent_nominal_to_rms(0), 1000000))

    def test_itic_region_no_interruption(self):
        pass









