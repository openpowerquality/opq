"""
This module tests the makai bridge.

Trigger messages enter mauka from makai in the makai protobuf format, are converted to the mauka protobuf format, and
then are injected into mauka with the topic "measurement".

We can test the makai bridge by mocking the makai trigger messages by producing them to the appropriate port. We can
then subscribe to the "measurement" topic to ensure the expected message arrived.
"""

import config
import tests.test_utils
import protobuf.opq_pb2
import protobuf.util

import zmq

import threading
import unittest

class MakaiBridgeTests(unittest.TestCase):
    def setUp(self):
        print("setup")
        self.config = config.from_file("/home/anthony/Development/opq/mauka/config.json").config_dict
        self.mauka_service = tests.test_utils.MaukaService(self.config, [])
        self.mauka_service.start_mauka_service()
        print("post-setup")

    def tearDown(self):
        self.mauka_service.stop_mauka_service()

    def test_makai_bridge(self):
        """Mock messages from makai to inject measurements into Mauka"""
        zmq_context = zmq.Context()

        # The mock makai trigger publisher
        makai_trigger_pub = zmq_context.socket(zmq.PUB)
        makai_trigger_pub.bind("tcp://*:9881")

        # Mauka subscription
        mauka_sub = zmq_context.socket(zmq.SUB)
        mauka_sub.connect("tcp://localhost:9883")
        mauka_sub.setsockopt_string(zmq.SUBSCRIBE, "measurement")

        # Mock trigger message
        makai_trigger_msg = protobuf.opq_pb2.TriggerMessage()
        makai_trigger_msg.time = 1528754706000
        makai_trigger_msg.id = 808
        makai_trigger_msg.frequency = 60.0
        makai_trigger_msg.rms = 120.0
        makai_trigger_msg.thd = 0.1

        # We need to schedule the trigger to send the message after we've started listening for it
        def _send_makai_trigger():
            makai_trigger_pub.send_multipart(("".encode(), makai_trigger_msg.SerializeToString()))
        t = threading.Timer(1, _send_makai_trigger)
        t.start()

        (topic, payload) = mauka_sub.recv_multipart()
        self.assertEqual(topic.decode(), "measurement")
        print(protobuf.util.deserialize_mauka_message(payload))



