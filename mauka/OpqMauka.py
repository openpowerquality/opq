#!/usr/bin/env python3

"""
This module is the entry point into the OPQMauka system.
"""

import json
import logging
import os
import multiprocessing
import sys
import typing

import plugins

_logger = logging.getLogger("app")
logging.basicConfig(
    format="[%(levelname)s][%(asctime)s][{} %(filename)s:%(lineno)s - %(funcName)s() ] %(message)s".format(
        os.getpid()))
_logger.setLevel(logging.DEBUG)


def usage():
    """Displays usage information"""
    _logger.info("Usage: ./OpqMauka.py [config file]")


def load_config(path: str) -> typing.Dict:
    """Loads a configuration file from the file system

    :param path: Path of configuration file
    :return: Configuration dictionary
    """
    _logger.info("Loading configuration from {}".format(path))
    try:
        with open(path, "r") as f:
            return json.load(f)
    except FileNotFoundError as e:
        _logger.error(e)
        usage()
        exit(0)


def start_mauka_pub_sub_broker(config: typing.Dict):
    def _run(config: typing.Dict):
        import logging
        import zmq

        _logger = logging.getLogger("app")
        logging.basicConfig(
            format="[%(levelname)s][%(asctime)s][{} %(filename)s:%(lineno)s - %(funcName)s() ] %(message)s".format(
                os.getpid()))

        zmq_pub_interface = config["zmq.mauka.broker.pub.interface"]
        zmq_sub_interface = config["zmq.mauka.broker.sub.interface"]
        zmq_context = zmq.Context()
        zmq_pub_socket = zmq_context.socket(zmq.PUB)
        zmq_sub_socket = zmq_context.socket(zmq.SUB)
        zmq_pub_socket.bind(zmq_pub_interface)
        zmq_sub_socket.bind(zmq_sub_interface)
        zmq_sub_socket.setsockopt(zmq.SUBSCRIBE, b"")
        _logger.info("Starting Mauka pub/sub broker")
        zmq.proxy(zmq_sub_socket, zmq_pub_socket)

    process = multiprocessing.Process(target=_run, args=(config,))
    process.start()
    return process


if __name__ == "__main__":
    _logger.info("Starting OpqMauka")
    if len(sys.argv) <= 1:
        _logger.error("Configuration file not supplied")
        usage()
        exit(0)

    config = load_config(sys.argv[1])

    pub_sub_server_process = start_mauka_pub_sub_broker(config)

    plugins_list = [
        [plugins.PrintPlugin, False],
        [plugins.MeasurementShimPlugin, True],
        [plugins.MeasurementPlugin, True],
        [plugins.FrequencyThresholdPlugin, True],
        [plugins.VoltageThresholdPlugin, True],
        [plugins.AcquisitionTriggerPlugin, True],
        [plugins.StatusPlugin, True]
    ]

    plugin_manager = plugins.PluginManager(plugins_list, config)
    plugin_manager.start_all_plugins()
