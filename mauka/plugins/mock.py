#!/usr/bin/env python3

import json
import sys
import time
import typing

import zmq


def produce(broker: str, topic: str, message: str):
    print("Producing {}:{} to {}".format(topic, message, broker))
    zmq_context = zmq.Context()
    zmq_pub_socket = zmq_context.socket(zmq.PUB)
    zmq_pub_socket.connect(broker)
    time.sleep(0.1)
    zmq_pub_socket.send_multipart((topic.encode(), message.encode()))


if __name__ == "__main__":
    def load_config(path: str) -> typing.Dict:
        """Loads a configuration file from the file system

        :param path: Path of configuration file
        :return: Configuration dictionary
        """
        try:
            with open(path, "r") as f:
                return json.load(f)
        except FileNotFoundError as e:
            print("usage: ./mock.py config topic message")
            exit(0)


    if len(sys.argv) != 4:
        sys.exit("usage: ./mock.py config topic message")

    config = load_config(sys.argv[1])
    topic = sys.argv[2]
    message = sys.argv[3]
    broker = config["zmq.mauka.plugin.pub.interface"]
    produce(broker, topic, message)
