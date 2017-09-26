#!/usr/bin/env python3

"""
This module is the entry point into the OPQMauka system.
"""

import json
import logging
import os
import signal
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


if __name__ == "__main__":
    _logger.info("Starting OpqMauka")
    if len(sys.argv) <= 1:
        _logger.error("Configuration file not supplied")
        usage()
        exit(0)

    config = load_config(sys.argv[1])

    plugin_manger = plugins.PluginManager(config)
    plugin_manger.register_plugin(plugins.MeasurementShimPlugin)
    plugin_manger.register_plugin(plugins.MeasurementPlugin)
    plugin_manger.register_plugin(plugins.FrequencyThresholdPlugin)
    plugin_manger.register_plugin(plugins.VoltageThresholdPlugin)
    plugin_manger.register_plugin(plugins.AcquisitionTriggerPlugin)
    plugin_manger.register_plugin(plugins.StatusPlugin)

    broker_process = plugins.start_mauka_pub_sub_broker(config)


    # start-stop-daemon sends a SIGTERM, we need to handle it to gracefully shutdown mauka
    def sigterm_handler(signum, frame):
        _logger.info("Received exit signal")
        import time
        import zmq
        zmq_context = zmq.Context()
        zmq_request_socket = zmq_context.socket(zmq.REQ)
        zmq_request_socket.connect(config["zmq.mauka.plugin.management.req.interface"])

        # 1) Stop all the plugins
        _logger.info("Stopping all plugins...")
        zmq_request_socket.send_string("stop-all-plugins")
        _logger.info(zmq_request_socket.recv_string())
        time.sleep(2)

        # 2) Stop the TCP server
        _logger.info("Stopping TCP server...")
        zmq_request_socket.send_string("stop-tcp-server")
        _logger.info(zmq_request_socket.recv_string())
        time.sleep(2)

        # 3) Kill broker process
        _logger.info("Stopping broker process...")
        broker_process.terminate()
        time.sleep(2)

        _logger.info("Goodbye")


    signal.signal(signal.SIGTERM, sigterm_handler)
    signal.signal(signal.SIGINT, sigterm_handler)

    try:
        plugin_manger.run_all_plugins()
        plugin_manger.start_tcp_server()
    except KeyboardInterrupt:
        sigterm_handler(None, None)
