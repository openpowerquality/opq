"""
This module tests the Mauka pub/sub broker.
"""

import threading
import time
import unittest

import services.brokers

import zmq


class BrokerTests(unittest.TestCase):
    def setUp(self):
        self.config = {"zmq.mauka.broker.pub.interface": "tcp://*:9883",
                       "zmq.mauka.broker.sub.interface": "tcp://*:9882",
                       "zmq.mauka.plugin.pub.interface": "tcp://localhost:9882",
                       "zmq.mauka.plugin.sub.interface": "tcp://localhost:9883"}
        self.broker_process = services.brokers.start_mauka_pub_sub_broker(self.config)
        self.zmq_context = zmq.Context()
        self.sub_socket = self.zmq_context.socket(zmq.SUB)
        self.pub_socket = self.zmq_context.socket(zmq.PUB)
        self.sub_socket.connect(self.config["zmq.mauka.plugin.sub.interface"])
        self.pub_socket.connect(self.config["zmq.mauka.plugin.pub.interface"])

    def tearDown(self):
        if self.broker_process.is_alive():
            self.broker_process.terminate()

    def produce_future_message(self, topic: str, val: str, after_seconds: float, future_msg=None):
        def _produce_message():
            if future_msg is None:
                self.pub_socket.send_multipart((topic.encode(), val.encode()))
            else:
                self.pub_socket.send_multipart(future_msg)

        timer = threading.Timer(after_seconds, _produce_message)
        timer.start()

    def test_broker_starts(self):
        """Tests that the broker process starts and is running"""
        self.assertTrue(self.broker_process.is_alive())

    def test_broker_stops(self):
        """Tests that the broker process is terminated correctly"""
        self.broker_process.terminate()
        time.sleep(0.5)
        self.assertFalse(self.broker_process.is_alive())

    def test_broker_message(self):
        """Tests that the broker can forward a single message of any topic"""
        self.sub_socket.setsockopt(zmq.SUBSCRIBE, "".encode())

        self.produce_future_message("foo", "bar", .25)
        msg = self.sub_socket.recv_multipart()
        self.assertEqual(msg[0].decode(), "foo")
        self.assertEqual(msg[1].decode(), "bar")

    def test_broker_messages(self):
        """Tests that the broker can forward multiple messages from multiple topics"""
        self.sub_socket.setsockopt(zmq.SUBSCRIBE, "".encode())

        for f in range(5):
            self.produce_future_message("foo", str(f), .25)
            msg = self.sub_socket.recv_multipart()
            self.assertEqual(msg[0].decode(), "foo", str(f))

        for b in range(5):
            self.produce_future_message("bar", str(f), .25)
            msg = self.sub_socket.recv_multipart()
            self.assertEqual(msg[0].decode(), "bar", str(f))

    def test_broker_with_topic(self):
        """Tests that a topic subscription to the broker only receives messages matching the subscribers topic"""
        zmq_context = zmq.Context()
        pub_socket = zmq_context.socket(zmq.PUB)
        sub_socket = zmq_context.socket(zmq.SUB)
        pub_socket.connect(self.config["zmq.mauka.plugin.pub.interface"])
        sub_socket.connect(self.config["zmq.mauka.plugin.sub.interface"])
        sub_socket.setsockopt(zmq.SUBSCRIBE, "foo".encode())

        self.produce_future_message("foo", "bar", .25)
        msg = sub_socket.recv_multipart()
        self.assertEqual(msg[0].decode(), "foo")
        self.assertEqual(msg[1].decode(), "bar")

        self.sub_socket.setsockopt(zmq.RCVTIMEO, 1000)
        self.assertRaises(zmq.error.Again, lambda: self.sub_socket.recv_multipart())
