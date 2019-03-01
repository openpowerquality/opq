#!/usr/bin/env python3

"""
This module allows us to mock and inject any (topic, message) pair into the Mauka system.
"""

import sys
import time

import zmq

import config
import constants
import log


# pylint: disable=C0103
logger = log.get_logger(__name__)


def produce(broker: str, topic: str, message: str = None, message_bytes=None):
    """
    Produces a message to the provided broker.
    The message can either be a string or bytes, but not both.
    :param broker: The URL of the ZMQ message broker.
    :param topic: The topic of the message.
    :param message:  The message as a string.
    :param message_bytes: The message as bytes.
    """
    # logger.info("Producing %s:%s to %s", topic, message, broker)
    zmq_context = zmq.Context()
    # noinspection PyUnresolvedReferences
    # pylint: disable=E1101
    zmq_pub_socket = zmq_context.socket(zmq.PUB)
    zmq_pub_socket.connect(broker)
    time.sleep(0.1)  # We need to sleep while the handshake takes place
    if message is not None:
        zmq_pub_socket.send_multipart((topic.encode(), message.encode()))
    else:
        zmq_pub_socket.send_multipart((topic.encode(), message_bytes))


def main():
    """
    Entry point when called as a script.
    """

    if len(sys.argv) != 4:
        sys.exit("usage: ./mock_plugin.py config topic message")

    conf = config.from_env(constants.CONFIG_ENV)
    topic = sys.argv[2]
    message = sys.argv[3]
    broker = conf.get("zmq.mauka.plugin.pub.interface")
    produce(broker, topic, message)


if __name__ == "__main__":
    main()
