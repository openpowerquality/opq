#!/usr/bin/env python3

"""
This module is the entry point into the OPQ Mauka system.
"""

import json
import signal
import sys
import typing

import log
import plugins
import services.brokers
import services.plugin_manager

# pylint: disable=C0103
logger = log.get_logger(__name__)


def usage():
    """Displays usage information"""
    logger.info("Usage: ./opq_mauka.py [config file]")


def load_config(path: str) -> typing.Dict:
    """Loads a configuration file from the file system

    :param path: Path of configuration file
    :return: Configuration dictionary
    """
    logger.info("Loading configuration from %s", path)
    try:
        with open(path, "r") as config_file:
            return json.load(config_file)
    except FileNotFoundError as error:
        logger.error(error)
        usage()
        exit(0)


def main():
    """
    Entry point to OPQ Mauka.
    """
    logger.info("Starting OpqMauka")
    if len(sys.argv) <= 1:
        logger.error("Configuration file not supplied")
        usage()
        exit(0)

    config = load_config(sys.argv[1])

    plugin_manager = services.plugin_manager.PluginManager(config)
    plugin_manager.register_plugin(plugins.FrequencyThresholdPlugin)
    plugin_manager.register_plugin(plugins.VoltageThresholdPlugin)
    plugin_manager.register_plugin(plugins.AcquisitionTriggerPlugin)
    plugin_manager.register_plugin(plugins.MakaiEventPlugin)
    plugin_manager.register_plugin(plugins.StatusPlugin)
    plugin_manager.register_plugin(plugins.ThdPlugin)
    plugin_manager.register_plugin(plugins.IticPlugin)

    broker_process = services.brokers.start_mauka_pub_sub_broker(config)
    makai_bridge_process = services.brokers.start_makai_bridge(config)
    makai_bridge_event_process = services.brokers.start_makai_event_bridge(config)

    # start-stop-daemon sends a SIGTERM, we need to handle it to gracefully shutdown mauka
    def sigterm_handler(signum, frame):
        """
        Custom sigterm handler.
        :param signum: Number of the signal.
        :param frame: Frame of signal.
        """
        logger.info("Received exit signal %s %s", str(signum), str(frame))
        plugin_manager.clean_exit()

    signal.signal(signal.SIGTERM, sigterm_handler)
    signal.signal(signal.SIGINT, sigterm_handler)

    try:
        plugin_manager.run_all_plugins()
        plugin_manager.start_tcp_server()
        logger.info("Killing broker process")
        broker_process.terminate()
        logger.info("Killing makai bridge process")
        makai_bridge_process.terminate()
        logger.info("Killing makai event bridge process")
        makai_bridge_event_process.terminate()
        logger.info("Goodbye")
        sys.exit(0)
    except KeyboardInterrupt:
        sigterm_handler(None, None)


if __name__ == "__main__":
    main()
