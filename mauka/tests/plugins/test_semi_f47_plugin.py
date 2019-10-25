import unittest

from analysis import ms_to_c
from plugins.semi_f47_plugin import point_in_poly, SEMI_F47_VIOLATION_POLYGON


class SemiF47PluginTests(unittest.TestCase):
    def test_lt_one_cycle(self):
        self.assertFalse(point_in_poly(0, 0))
        self.assertFalse(point_in_poly(1, 0))
        self.assertFalse(point_in_poly(1, 10_000))

    def test_no_violation(self):
        self.assertFalse(point_in_poly(1.1, 50.1))
        self.assertFalse(point_in_poly(ms_to_c(100), 50.1))
        self.assertFalse(point_in_poly(ms_to_c(100), 1_000_000))
        self.assertFalse(point_in_poly(ms_to_c(300), 70.1))
        self.assertFalse(point_in_poly(ms_to_c(300), 1_000_000))
        self.assertFalse(point_in_poly(ms_to_c(500), 80.1))
        self.assertFalse(point_in_poly(ms_to_c(10_000), 1_000_000))

    def test_violation(self):
        self.assertTrue(point_in_poly(2, 49.9))
        self.assertTrue(point_in_poly(ms_to_c(100), 49.9))
        self.assertTrue(point_in_poly(ms_to_c(200), 49.9))
        self.assertTrue(point_in_poly(ms_to_c(201), 69.9))
        self.assertTrue(point_in_poly(ms_to_c(500), 69.9))
        self.assertTrue(point_in_poly(ms_to_c(501), 79.9))
        self.assertTrue(point_in_poly(ms_to_c(10000), 79.9))
        self.assertTrue(point_in_poly(ms_to_c(10001), 89.9))
        self.assertTrue(point_in_poly(ms_to_c(1_000_000), 89.9))

    def test_line(self):
        for xy in SEMI_F47_VIOLATION_POLYGON:
            x = xy[0]
            y = xy[1]
            self.assertTrue(point_in_poly(x, y))
