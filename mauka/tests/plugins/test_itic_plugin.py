import unittest

import analysis
from plugins.itic_plugin import IticRegion, itic_region


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
        self.assertEqual(IticRegion.NO_DAMAGE, itic_region(0, 20_000_000))

    def test_itic_region_nominal(self):
        """
        Every RMS value with percent nominal between 90 and 110 percent should return no interruption irrelevant of
        duration.
        """
        self.assertEqual(IticRegion.NO_INTERRUPTION, itic_region(percent_nominal_to_rms(109.99), 0))
        self.assertEqual(IticRegion.NO_INTERRUPTION, itic_region(percent_nominal_to_rms(109.99), 3))
        self.assertEqual(IticRegion.NO_INTERRUPTION, itic_region(percent_nominal_to_rms(109.99), 500))
        self.assertEqual(IticRegion.NO_INTERRUPTION, itic_region(percent_nominal_to_rms(109.99), 10_000))
        self.assertEqual(IticRegion.NO_INTERRUPTION, itic_region(percent_nominal_to_rms(109.99), 1_000_000))

        self.assertEqual(IticRegion.NO_INTERRUPTION, itic_region(percent_nominal_to_rms(90.01), 0))
        self.assertEqual(IticRegion.NO_INTERRUPTION, itic_region(percent_nominal_to_rms(90.01), 3))
        self.assertEqual(IticRegion.NO_INTERRUPTION, itic_region(percent_nominal_to_rms(90.01), 500))
        self.assertEqual(IticRegion.NO_INTERRUPTION, itic_region(percent_nominal_to_rms(90.01), 10_000))
        self.assertEqual(IticRegion.NO_INTERRUPTION, itic_region(percent_nominal_to_rms(90.01), 1_000_000))

    def test_itic_region_prohibited(self):
        """
        All test results should return a prohibited ITIC region. First we'll test a few that are clearly prohibited
        and then we will probe around the edge of the prohibited region to test edge cases.
        """
        self.assertEqual(IticRegion.PROHIBITED, itic_region(percent_nominal_to_rms(300), 500))
        self.assertEqual(IticRegion.PROHIBITED, itic_region(percent_nominal_to_rms(600), 3))
        self.assertEqual(IticRegion.PROHIBITED, itic_region(percent_nominal_to_rms(140), 20))
        self.assertEqual(IticRegion.PROHIBITED, itic_region(percent_nominal_to_rms(500), 1))
        self.assertEqual(IticRegion.PROHIBITED, itic_region(percent_nominal_to_rms(200), 1.1))
        self.assertEqual(IticRegion.PROHIBITED, itic_region(percent_nominal_to_rms(140), 3.1))
        self.assertEqual(IticRegion.PROHIBITED, itic_region(percent_nominal_to_rms(121), 3.1))
        self.assertEqual(IticRegion.PROHIBITED, itic_region(percent_nominal_to_rms(121), 500))
        self.assertEqual(IticRegion.PROHIBITED, itic_region(percent_nominal_to_rms(120), 501))
        self.assertEqual(IticRegion.PROHIBITED, itic_region(percent_nominal_to_rms(110), 501))
        self.assertEqual(IticRegion.PROHIBITED, itic_region(percent_nominal_to_rms(111), 15_000))
        self.assertEqual(IticRegion.PROHIBITED, itic_region(percent_nominal_to_rms(110), 501))
        self.assertEqual(IticRegion.PROHIBITED, itic_region(percent_nominal_to_rms(112), 1_000_000))
        self.assertEqual(IticRegion.PROHIBITED, itic_region(percent_nominal_to_rms(10_000), analysis.c_to_ms(.02)))

    def test_itic_region_no_damage(self):
        """
        All test results should return a no damage ITIC region. First we'll test a few that are clearly no damange
        and then we will probe around the edge of the no damage region to test edge cases.
        """
        self.assertEqual(IticRegion.NO_DAMAGE, itic_region(percent_nominal_to_rms(40), 500))
        self.assertEqual(IticRegion.NO_DAMAGE, itic_region(percent_nominal_to_rms(40), 1_000_000))
        self.assertEqual(IticRegion.NO_DAMAGE, itic_region(percent_nominal_to_rms(70), 10000))
        self.assertEqual(IticRegion.NO_DAMAGE, itic_region(percent_nominal_to_rms(70), 501))
        self.assertEqual(IticRegion.NO_DAMAGE, itic_region(percent_nominal_to_rms(69), 20.1))
        self.assertEqual(IticRegion.NO_DAMAGE, itic_region(percent_nominal_to_rms(79), 500.1))
        self.assertEqual(IticRegion.NO_DAMAGE, itic_region(percent_nominal_to_rms(89.9), 10000.1))
        self.assertEqual(IticRegion.NO_DAMAGE, itic_region(percent_nominal_to_rms(89.9), 1000000))
        self.assertEqual(IticRegion.NO_DAMAGE, itic_region(percent_nominal_to_rms(40), 20.1))
        self.assertEqual(IticRegion.NO_DAMAGE, itic_region(percent_nominal_to_rms(0), 1000000))

    def test_itic_region_no_interruption(self):
        """
        All test results should return a no interruption ITIC region. First we'll test a few that are clearly
        no damage and then we will probe around the edge of the no damage region to test edge cases.
        """
        self.assertEqual(IticRegion.NO_INTERRUPTION, itic_region(percent_nominal_to_rms(100), 0))
        self.assertEqual(IticRegion.NO_INTERRUPTION, itic_region(percent_nominal_to_rms(100), 1))
        self.assertEqual(IticRegion.NO_INTERRUPTION, itic_region(percent_nominal_to_rms(100), 10000))
        self.assertEqual(IticRegion.NO_INTERRUPTION, itic_region(percent_nominal_to_rms(100), 1000000))
        self.assertEqual(IticRegion.NO_INTERRUPTION, itic_region(percent_nominal_to_rms(500), analysis.c_to_ms(0.01)))
        self.assertEqual(IticRegion.NO_INTERRUPTION, itic_region(percent_nominal_to_rms(1000), analysis.c_to_ms(0.01)))
        self.assertEqual(IticRegion.NO_INTERRUPTION, itic_region(0, analysis.c_to_ms(0.01)))
        self.assertEqual(IticRegion.NO_INTERRUPTION, itic_region(0, 20))
        self.assertEqual(IticRegion.NO_INTERRUPTION, itic_region(0, 20))
        self.assertEqual(IticRegion.NO_INTERRUPTION, itic_region(percent_nominal_to_rms(200), .9))
        self.assertEqual(IticRegion.NO_INTERRUPTION, itic_region(percent_nominal_to_rms(140), 2.9))
        self.assertEqual(IticRegion.NO_INTERRUPTION, itic_region(percent_nominal_to_rms(120), 2.9))
        self.assertEqual(IticRegion.NO_INTERRUPTION, itic_region(percent_nominal_to_rms(110), 0.5))
        self.assertEqual(IticRegion.NO_INTERRUPTION, itic_region(percent_nominal_to_rms(109), 10_000))
        self.assertEqual(IticRegion.NO_INTERRUPTION, itic_region(percent_nominal_to_rms(90), 9999))
        self.assertEqual(IticRegion.NO_INTERRUPTION, itic_region(percent_nominal_to_rms(80), 499))
        self.assertEqual(IticRegion.NO_INTERRUPTION, itic_region(percent_nominal_to_rms(70), 19))
        self.assertEqual(IticRegion.NO_INTERRUPTION, itic_region(percent_nominal_to_rms(40), 19))

    def test_on_line(self):
        self.assertEqual(IticRegion.NO_INTERRUPTION, itic_region(percent_nominal_to_rms(500), analysis.c_to_ms(0.01)))
        self.assertEqual(IticRegion.NO_INTERRUPTION, itic_region(percent_nominal_to_rms(1_000_000), analysis.c_to_ms(0.01)))
        self.assertEqual(IticRegion.NO_INTERRUPTION, itic_region(percent_nominal_to_rms(200), 1))
        self.assertEqual(IticRegion.NO_INTERRUPTION, itic_region(percent_nominal_to_rms(140), 3))
        self.assertEqual(IticRegion.NO_INTERRUPTION, itic_region(percent_nominal_to_rms(120), 3))
        self.assertEqual(IticRegion.NO_INTERRUPTION, itic_region(percent_nominal_to_rms(120), 500))
        self.assertEqual(IticRegion.NO_INTERRUPTION, itic_region(percent_nominal_to_rms(110), 500))

        # self.assertEqual(IticRegion.NO_INTERRUPTION, itic_region(percent_nominal_to_rms(110), 800))

        self.assertEqual(IticRegion.NO_INTERRUPTION, itic_region(percent_nominal_to_rms(0), 20))
        self.assertEqual(IticRegion.NO_INTERRUPTION, itic_region(percent_nominal_to_rms(40), 20))
        self.assertEqual(IticRegion.NO_INTERRUPTION, itic_region(percent_nominal_to_rms(70), 20))
        self.assertEqual(IticRegion.NO_INTERRUPTION, itic_region(percent_nominal_to_rms(70), 500))
        self.assertEqual(IticRegion.NO_INTERRUPTION, itic_region(percent_nominal_to_rms(80), 500))
        self.assertEqual(IticRegion.NO_INTERRUPTION, itic_region(percent_nominal_to_rms(80), 10_000))
        self.assertEqual(IticRegion.NO_INTERRUPTION, itic_region(percent_nominal_to_rms(90), 10_000))
        self.assertEqual(IticRegion.NO_INTERRUPTION, itic_region(percent_nominal_to_rms(90), 100_000))
        self.assertEqual(IticRegion.NO_INTERRUPTION, itic_region(percent_nominal_to_rms(90), 1_000_000))
