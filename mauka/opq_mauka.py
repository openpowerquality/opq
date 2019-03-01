#!/usr/bin/env python3

"""
This module is the entry point into the OPQ Mauka system.
"""

import signal
import sys

import config
import constants
import log
import plugins.frequency_variation_plugin
import plugins.transient_plugin
import plugins.itic_plugin
import plugins.makai_event_plugin
import plugins.outage_plugin
import plugins.status_plugin
import plugins.thd_plugin
import plugins.ieee1159_voltage_plugin
import plugins.semi_f47_plugin
import services.brokers
import services.plugin_manager

# pylint: disable=C0103
logger = log.get_logger(__name__)


def usage():
    """Displays usage information"""
    logger.info("Usage: ./opq_mauka.py [config file]")


def main():
    """
    Entry point to OPQ Mauka.
    """
    logger.info("Starting OpqMauka")
    conf = config.from_env(constants.CONFIG_ENV)

    plugin_manager = services.plugin_manager.PluginManager(conf)
    plugin_manager.register_plugin(plugins.makai_event_plugin.MakaiEventPlugin)
    plugin_manager.register_plugin(plugins.status_plugin.StatusPlugin)
    plugin_manager.register_plugin(plugins.thd_plugin.ThdPlugin)
    plugin_manager.register_plugin(plugins.itic_plugin.IticPlugin)
    plugin_manager.register_plugin(plugins.frequency_variation_plugin.FrequencyVariationPlugin)
    plugin_manager.register_plugin(plugins.transient_plugin.TransientPlugin)
    plugin_manager.register_plugin(plugins.ieee1159_voltage_plugin.Ieee1159VoltagePlugin)
    plugin_manager.register_plugin(plugins.semi_f47_plugin.SemiF47Plugin)
    plugin_manager.register_plugin(plugins.outage_plugin.OutagePlugin)

    broker_process = services.brokers.start_mauka_pub_sub_broker(conf)
    makai_bridge_event_process = services.brokers.start_makai_event_bridge(conf)

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
        logger.info("Killing makai event bridge process")
        makai_bridge_event_process.terminate()
        logger.info("Goodbye")
        sys.exit(0)
    except KeyboardInterrupt:
        sigterm_handler(None, None)


if __name__ == "__main__":
    main()
