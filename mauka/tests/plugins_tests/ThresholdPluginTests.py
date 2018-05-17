import multiprocessing
import unittest

import plugins.ThresholdPlugin
import plugins.VoltageThresholdPlugin

config = {
    "zmq.triggering.interface": "tcp://localhost:9881",
    "zmq.mauka.broker.pub.interface": "tcp://*:9883",
    "zmq.mauka.broker.sub.interface": "tcp://*:9882",
    "zmq.mauka.plugin.pub.interface": "tcp://localhost:9882",
    "zmq.mauka.plugin.sub.interface": "tcp://localhost:9883",
    "zmq.makai.req.interface": "tcp://localhost:9884",

    "zmq.mauka.plugin.management.rep.interface": "tcp://*:12000",
    "zmq.mauka.plugin.management.req.interface": "tcp://localhost:12000",

    "mongo.host": "emilia.ics.hawaii.edu",
    "mongo.port": 27017,
    "mongo.db": "opq",

    "plugins.AcquisitionTriggerPlugin.msBefore": 1000,
    "plugins.AcquisitionTriggerPlugin.msAfter": 1000,
    "plugins.AcquisitionTriggerPlugin.sDeadZoneAfterTrigger": 60,

    "plugins.base.heartbeatIntervalS": 600.0,

    "plugins.MeasurementPlugin.sample_every": 3.0,

    "plugins.ThresholdPlugin.voltage.ref": 120.0,
    "plugins.ThresholdPlugin.voltage.threshold.percent.low": 5.0,
    "plugins.ThresholdPlugin.voltage.threshold.percent.high": 5.0,

    "plugins.ThresholdPlugin.frequency.ref": 60.0,
    "plugins.ThresholdPlugin.frequency.threshold.percent.low": 0.5,
    "plugins.ThresholdPlugin.frequency.threshold.percent.high": 0.5
}


class ThresholdPluginTests(unittest.TestCase):
    def setUp(self):
        self.exit_event = multiprocessing.Event()
        self.threshold_plugin = plugins.ThresholdPlugin.ThresholdPlugin(config, "ThresholdPlugin", self.exit_event)
        self.device_id = 10

    def tearDown(self):
        pass

    def test_subscribe_threshold(self):
        self.threshold_plugin.subscribe_threshold(lambda m: m.rms, 120.0, 5.0, 5.0)
        self.assertEqual(self.threshold_plugin.threshold_value_low, 114.0)
        self.assertEqual(self.threshold_plugin.threshold_value_high, 126.0)

    def test_open_event_low(self):
        self.assertTrue(len(self.threshold_plugin.device_id_to_low_events) == 0)
        self.assertTrue(len(self.threshold_plugin.device_id_to_high_events) == 0)
        self.threshold_plugin.open_event(1, self.device_id, 100.0, True)
        self.assertTrue(len(self.threshold_plugin.device_id_to_low_events) == 1)
        self.assertTrue(len(self.threshold_plugin.device_id_to_high_events) == 0)
        event = self.threshold_plugin.device_id_to_low_events[self.device_id]
        self.assertEqual(event.start, 1)
        self.assertEqual(event.end, 0)
        self.assertEqual(event.threshold_type, "LOW")
        self.assertEqual(event.max_value, 100.0)

    def test_open_event_high(self):
        self.assertTrue(len(self.threshold_plugin.device_id_to_low_events) == 0)
        self.assertTrue(len(self.threshold_plugin.device_id_to_high_events) == 0)
        self.threshold_plugin.open_event(1, self.device_id, 140.0, False)
        self.assertTrue(len(self.threshold_plugin.device_id_to_low_events) == 0)
        self.assertTrue(len(self.threshold_plugin.device_id_to_high_events) == 1)
        event = self.threshold_plugin.device_id_to_high_events[self.device_id]
        self.assertEqual(event.start, 1)
        self.assertEqual(event.end, 0)
        self.assertEqual(event.threshold_type, "HIGH")
        self.assertEqual(event.max_value, 140.0)

    def test_update_event_low(self):
        self.threshold_plugin.open_event(1, self.device_id, 100.0, True)
        event = self.threshold_plugin.device_id_to_low_events[self.device_id]
        self.threshold_plugin.update_event(event, 101.0)
        event = self.threshold_plugin.device_id_to_low_events[self.device_id]
        self.assertEqual(event.max_value, 101.0)

    def test_update_event_high(self):
        self.threshold_plugin.open_event(1, self.device_id, 140.0, False)
        event = self.threshold_plugin.device_id_to_high_events[self.device_id]
        self.threshold_plugin.update_event(event, 141.0)
        event = self.threshold_plugin.device_id_to_high_events[self.device_id]
        self.assertEqual(event.max_value, 141.0)

    def test_close_event_low(self):
        self.threshold_plugin.open_event(1, self.device_id, 100.0, True)
        self.assertTrue(self.device_id in self.threshold_plugin.device_id_to_low_events)
        event = self.threshold_plugin.device_id_to_low_events[self.device_id]
        self.threshold_plugin.close_event(event, 1)
        self.assertFalse(self.device_id in self.threshold_plugin.device_id_to_low_events)

    def test_close_event_high(self):
        self.threshold_plugin.on_event = lambda e: print(e)
        self.threshold_plugin.open_event(1, self.device_id, 140.0, False)
        self.assertTrue(self.device_id in self.threshold_plugin.device_id_to_high_events)
        event = self.threshold_plugin.device_id_to_high_events[self.device_id]
        self.threshold_plugin.close_event(event, 1)
        self.assertFalse(self.device_id in self.threshold_plugin.device_id_to_high_events)
