"""
This module contains tests for Mauka's TriggerPlugin.
"""

import protobuf.opqbox3_pb2 as opqbox3_pb2

from plugins.trigger_plugin import cycles_to_data
import plugins.trigger_plugin as trigger_plugin

import unittest


class TriggerPluginTests(unittest.TestCase):
    def test_cycles_to_data(self):
        cycles = []
        for i in range(0, 100, 10):
            cycle = opqbox3_pb2.Cycle()
            cycle.datapoints.extend(list(range(i, i + 10)))
            cycles.append(cycle)

        self.assertEqual(cycles_to_data(cycles), list(range(0, 100)))

    def test_extract_timestamps_single(self):
        cycle = opqbox3_pb2.Cycle()
        cycle.timestamp_ms = 1
        self.assertEqual(trigger_plugin.extract_timestamps([cycle]), (1, 1))

    def test_extract_timestamps_double(self):
        cycles = []
        for i in range(2):
            cycle = opqbox3_pb2.Cycle()
            cycle.timestamp_ms = i
            cycles.append(cycle)

        self.assertEqual(trigger_plugin.extract_timestamps(cycles), (0, 1))

    def test_extract_timestamps_multi(self):
        cycles = []
        for i in range(3):
            cycle = opqbox3_pb2.Cycle()
            cycle.timestamp_ms = i
            cycles.append(cycle)

        self.assertEqual(trigger_plugin.extract_timestamps(cycles), (0, 2))

    def test_trigger_record_single_record(self):
        trigger_records = trigger_plugin.TriggerRecords()
        event_token = "event_token"
        event_id = 1
        incident_id = 0
        box_ids = {"1", "2", "3"}
        trigger_records.insert_record(event_token, event_id, incident_id, box_ids)

        self.assertEqual(trigger_records.event_id(event_token), event_id)
        self.assertEqual(trigger_records.box_ids_for_token(event_token), box_ids)
        trigger_records.remove_box_id(event_token, "1")
        self.assertEqual(trigger_records.box_ids_for_token(event_token), {"2", "3"})
        trigger_records.remove_box_id(event_token, "2")
        self.assertEqual(trigger_records.box_ids_for_token(event_token), {"3"})
        trigger_records.remove_box_id(event_token, "4")
        self.assertEqual(trigger_records.box_ids_for_token(event_token), {"3"})
        trigger_records.remove_box_id(event_token, "3")
        self.assertEqual(trigger_records.box_ids_for_token(event_token), set())
        trigger_records.remove_record(event_token)
        self.assertEqual(trigger_records.event_id(event_token), None)
