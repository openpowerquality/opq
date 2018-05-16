import plugins.IticPlugin
from plugins.IticPlugin import IticRegion

import sys
import unittest


class IticPluginTests(unittest.TestCase):

    def test_itic_no_interruptions_at_rms_120(self):
        self.assertEqual(IticRegion.NO_INTERRUPTION, plugins.IticPlugin.itic_region(120, -1))
        self.assertEqual(IticRegion.NO_INTERRUPTION, plugins.IticPlugin.itic_region(120, 0))
        self.assertEqual(IticRegion.NO_INTERRUPTION, plugins.IticPlugin.itic_region(120, 1))
        self.assertEqual(IticRegion.NO_INTERRUPTION, plugins.IticPlugin.itic_region(120, 3))
        self.assertEqual(IticRegion.NO_INTERRUPTION, plugins.IticPlugin.itic_region(120, 20))
        self.assertEqual(IticRegion.NO_INTERRUPTION, plugins.IticPlugin.itic_region(120, 5000))
        self.assertEqual(IticRegion.NO_INTERRUPTION, plugins.IticPlugin.itic_region(120, 10000))
        self.assertEqual(IticRegion.NO_INTERRUPTION, plugins.IticPlugin.itic_region(120, 20000))
        self.assertEqual(IticRegion.NO_INTERRUPTION, plugins.IticPlugin.itic_region(120, sys.maxsize))

    def test_itic_no_interruptions(self):
        self.assertEqual(IticRegion.NO_INTERRUPTION,
                         plugins.IticPlugin.itic_region(1000, plugins.IticPlugin.c_to_ms(0.01)))
        self.assertEqual(IticRegion.NO_INTERRUPTION,
                         plugins.IticPlugin.itic_region(600, plugins.IticPlugin.c_to_ms(0.01)))
        self.assertEqual(IticRegion.NO_INTERRUPTION, plugins.IticPlugin.itic_region(240, .9))
        self.assertEqual(IticRegion.NO_INTERRUPTION, plugins.IticPlugin.itic_region(168, 2.9))
        self.assertEqual(IticRegion.NO_INTERRUPTION, plugins.IticPlugin.itic_region(144, 3))
        self.assertEqual(IticRegion.NO_INTERRUPTION, plugins.IticPlugin.itic_region(144, 4999))
        self.assertEqual(IticRegion.NO_INTERRUPTION, plugins.IticPlugin.itic_region(132, 4999))
        self.assertEqual(IticRegion.NO_INTERRUPTION, plugins.IticPlugin.itic_region(131.9, 5000))
        self.assertEqual(IticRegion.NO_INTERRUPTION, plugins.IticPlugin.itic_region(131.9, sys.maxsize))
        self.assertEqual(IticRegion.NO_INTERRUPTION, plugins.IticPlugin.itic_region(108.1, sys.maxsize))
        self.assertEqual(IticRegion.NO_INTERRUPTION, plugins.IticPlugin.itic_region(108.1, 10000))
        self.assertEqual(IticRegion.NO_INTERRUPTION, plugins.IticPlugin.itic_region(107.9, 9999))
        self.assertEqual(IticRegion.NO_INTERRUPTION, plugins.IticPlugin.itic_region(96, 4999))
        self.assertEqual(IticRegion.NO_INTERRUPTION, plugins.IticPlugin.itic_region(84, 20))
        self.assertEqual(IticRegion.NO_INTERRUPTION, plugins.IticPlugin.itic_region(48, 20))
        self.assertEqual(IticRegion.NO_INTERRUPTION, plugins.IticPlugin.itic_region(1, 20))
        self.assertEqual(IticRegion.NO_INTERRUPTION, plugins.IticPlugin.itic_region(0, 20))

    def test_itic_no_damage(self):
        self.assertEqual(IticRegion.NO_DAMAGE, plugins.IticPlugin.itic_region(0, 20.1))
        self.assertEqual(IticRegion.NO_DAMAGE, plugins.IticPlugin.itic_region(120 * 0.40, 20.1))
        self.assertEqual(IticRegion.NO_DAMAGE, plugins.IticPlugin.itic_region(120 * 0.40, sys.maxsize))
        self.assertEqual(IticRegion.NO_DAMAGE, plugins.IticPlugin.itic_region(120 * 0.69, 20.1))
        self.assertEqual(IticRegion.NO_DAMAGE, plugins.IticPlugin.itic_region(120 * 0.70, 20.1))
        self.assertEqual(IticRegion.NO_DAMAGE, plugins.IticPlugin.itic_region(120 * 0.70, 5000))
        self.assertEqual(IticRegion.NO_DAMAGE, plugins.IticPlugin.itic_region(120 * 0.70, 5001))
        self.assertEqual(IticRegion.NO_DAMAGE, plugins.IticPlugin.itic_region(120 * 0.70, sys.maxsize))
        self.assertEqual(IticRegion.NO_DAMAGE, plugins.IticPlugin.itic_region(120 * 0.80, 5001))
        self.assertEqual(IticRegion.NO_DAMAGE, plugins.IticPlugin.itic_region(120 * 0.80, 10000))
        self.assertEqual(IticRegion.NO_DAMAGE, plugins.IticPlugin.itic_region(120 * 0.80, sys.maxsize))
        self.assertEqual(IticRegion.NO_DAMAGE, plugins.IticPlugin.itic_region(120 * 0.90, 10000))
        self.assertEqual(IticRegion.NO_DAMAGE, plugins.IticPlugin.itic_region(120 * 0.90, sys.maxsize))

    def test_itic_prohibited(self):
        self.assertEqual(IticRegion.PROHIBITED,
                         plugins.IticPlugin.itic_region(120 * 5.00, plugins.IticPlugin.c_to_ms(0.02)))
        self.assertEqual(IticRegion.PROHIBITED,
                         plugins.IticPlugin.itic_region(120 * 5.01, plugins.IticPlugin.c_to_ms(0.02)))
        self.assertEqual(IticRegion.PROHIBITED, plugins.IticPlugin.itic_region(120 * 3.00, sys.maxsize))
        self.assertEqual(IticRegion.PROHIBITED, plugins.IticPlugin.itic_region(120 * 2.00, 1))
        self.assertEqual(IticRegion.PROHIBITED, plugins.IticPlugin.itic_region(120 * 1.40, 3))
        self.assertEqual(IticRegion.PROHIBITED, plugins.IticPlugin.itic_region(120 * 1.21, 3))
        self.assertEqual(IticRegion.PROHIBITED, plugins.IticPlugin.itic_region(120 * 1.20, 5000))
        self.assertEqual(IticRegion.PROHIBITED, plugins.IticPlugin.itic_region(120 * 1.20, 5001))
        self.assertEqual(IticRegion.PROHIBITED, plugins.IticPlugin.itic_region(120 * 1.10, 5000))
        self.assertEqual(IticRegion.PROHIBITED, plugins.IticPlugin.itic_region(120 * 1.10, 10000))
        self.assertEqual(IticRegion.PROHIBITED, plugins.IticPlugin.itic_region(120 * 1.10, 10001))
        self.assertEqual(IticRegion.PROHIBITED, plugins.IticPlugin.itic_region(120 * 1.10, sys.maxsize))
