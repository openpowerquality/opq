import json
import unittest

import plugins.base
import plugins.mock
import plugins.ThresholdPlugin
import tests.test_utils

import zmq

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


class VoltageThresholdPluginTests(unittest.TestCase):
    def setUp(self):
        self.voltage_threshold_plugin_process = plugins.base.run_plugin(plugins.VoltageThresholdPlugin, config)

    def tearDown(self):
        self.voltage_threshold_plugin_process.terminate()

    def test_voltage_dip(self):
        threshold_event = plugins.ThresholdPlugin.ThresholdEvent(start=tests.test_utils.current_milli_time(),
                                                                 end=tests.test_utils.current_milli_time(),
                                                                 device_id=10,
                                                                 threshold_type="LOW",
                                                                 max_value=100.0)


    def test_voltage_swell(self):
        pass

    def test_unknown_threshold_type(self):
        pass

    def test_extract_voltage(self):
        pass
