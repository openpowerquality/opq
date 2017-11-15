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

    plugin_manager = plugins.PluginManager(config)
    plugin_manager.register_plugin(plugins.MeasurementPlugin)
    plugin_manager.register_plugin(plugins.FrequencyThresholdPlugin)
    plugin_manager.register_plugin(plugins.VoltageThresholdPlugin)
    plugin_manager.register_plugin(plugins.AcquisitionTriggerPlugin)
    plugin_manager.register_plugin(plugins.StatusPlugin)
    plugin_manager.register_plugin(plugins.ThdPlugin)
    plugin_manager.register_plugin(plugins.IticPlugin)

    broker_process = plugins.start_mauka_pub_sub_broker(config)
    makai_bridge_process = plugins.start_makai_bridge(config)

    # start-stop-daemon sends a SIGTERM, we need to handle it to gracefully shutdown mauka
    def sigterm_handler(signum, frame):
        _logger.info("Received exit signal")
        plugin_manager.clean_exit()
        #_logger.info("Stopping broker process...")
        #broker_process.terminate()
        #sys.exit(0)


    signal.signal(signal.SIGTERM, sigterm_handler)
    signal.signal(signal.SIGINT, sigterm_handler)

    try:

        plugin_manager.run_all_plugins()
        plugin_manager.start_tcp_server()
        _logger.info("Killing broker process")
        broker_process.terminate()
        _logger.info("Killing makai bridge process")
        makai_bridge_process.terminate()
        _logger.info("Goodbye")
        sys.exit(0)
    except KeyboardInterrupt:
        sigterm_handler(None, None)
