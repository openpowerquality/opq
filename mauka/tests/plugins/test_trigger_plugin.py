"""
This module contains tests for Mauka's TriggerPlugin.
"""

import protobuf.opqbox3_pb2 as opqbox3_pb2

from plugins.trigger_plugin import cycles_to_data

import unittest


class TriggerPluginTests(unittest.TestCase):
    def test_cycles_to_data(self):
        cycles = []
        for i in range(0, 100, 10):
            cycle = opqbox3_pb2.Cycle()
            cycle.datapoints.extend(list(range(i, i + 10)))
            cycles.append(cycle)

        self.assertEqual(cycles_to_data(cycles), list(range(0, 100)))
