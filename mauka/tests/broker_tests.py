"""
This module tests the Mauka pub/sub broker.
"""

import threading
import time
import unittest

import zmq

import OpqMauka


def produce_future_message(producer_socket, topic: str, val: str, after_seconds: float):
    def _produce_message():
        producer_socket.send_multipart((topic.encode(), val.encode()))

    timer = threading.Timer(after_seconds, _produce_message)
    timer.start()


class BrokerTests(unittest.TestCase):
    def setUp(self):
        self.config = {"zmq.mauka.broker.pub.interface": "tcp://*:9883",
                       "zmq.mauka.broker.sub.interface": "tcp://*:9882",
                       "zmq.mauka.plugin.pub.interface": "tcp://localhost:9882",
                       "zmq.mauka.plugin.sub.interface": "tcp://localhost:9883"}
        self.broker_process = OpqMauka.start_mauka_pub_sub_broker(self.config)

    def tearDown(self):
        if self.broker_process.is_alive():
            self.broker_process.terminate()

    def test_broker_starts(self):
        self.assertTrue(self.broker_process.is_alive())

    def test_broker_stops(self):
        self.broker_process.terminate()
        time.sleep(0.5)
        self.assertFalse(self.broker_process.is_alive())

    def test_broker_message(self):
        zmq_context = zmq.Context()
        pub_socket = zmq_context.socket(zmq.PUB)
        sub_socket = zmq_context.socket(zmq.SUB)
        pub_socket.connect(self.config["zmq.mauka.plugin.pub.interface"])
        sub_socket.connect(self.config["zmq.mauka.plugin.sub.interface"])
        sub_socket.setsockopt(zmq.SUBSCRIBE, "".encode())

        produce_future_message(pub_socket, "foo", "bar", .25)
        msg = sub_socket.recv_multipart()
        self.assertEqual(msg[0].decode(), "foo")
        self.assertEqual(msg[1].decode(), "bar")

    def test_broker_messages(self):
        zmq_context = zmq.Context()
        pub_socket = zmq_context.socket(zmq.PUB)
        sub_socket = zmq_context.socket(zmq.SUB)
        pub_socket.connect(self.config["zmq.mauka.plugin.pub.interface"])
        sub_socket.connect(self.config["zmq.mauka.plugin.sub.interface"])
        sub_socket.setsockopt(zmq.SUBSCRIBE, "".encode())

        for f in range(10):
            produce_future_message(pub_socket, "foo", str(f), .25)
            msg = sub_socket.recv_multipart()
            self.assertEqual(msg[0].decode(), "foo", str(f))

        for b in range(10):
            produce_future_message(pub_socket, "bar", str(f), .25)
            msg = sub_socket.recv_multipart()
            self.assertEqual(msg[0].decode(), "bar", str(f))

    # def test_broker_with_topic(self):
    #     zmq_context = zmq.Context()
    #     pub_socket = zmq_context.socket(zmq.PUB)
    #     sub_socket = zmq_context.socket(zmq.SUB)
    #     pub_socket.connect(self.config["zmq.mauka.plugin.pub.interface"])
    #     sub_socket.connect(self.config["zmq.mauka.plugin.sub.interface"])
    #     sub_socket.setsockopt(zmq.SUBSCRIBE, "foo".encode())
    #
    #     produce_future_message(pub_socket, "foo", "bar", .25)
    #     msg = sub_socket.recv_multipart()
    #     self.assertEqual(msg[0].decode(), "foo")
    #     self.assertEqual(msg[1].decode(), "bar")
    #
    #     produce_future_message(pub_socket, "baz", "bar", .25)
    #     try:
    #         sub_socket.recv_multipart(flags=zmq.NOBLOCK)
    #         self.assertTrue(False)
    #     except zmq.error.Again:
    #         self.assertTrue(True)
    #         self.broker_process.terminate()
