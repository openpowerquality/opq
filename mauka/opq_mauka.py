#!/usr/bin/env python3

"""
This module is the entry point into the OPQ Mauka system.
"""

import signal
import sys

import config
import constants
import log
import mongo
import plugins.annotation_plugin
import plugins.box_optimization_plugin
import plugins.frequency_variation_plugin
import plugins.laha_gc_plugin
import plugins.transient_plugin
import plugins.itic_plugin
import plugins.makai_event_plugin
import plugins.outage_plugin
import plugins.status_plugin
import plugins.thd_plugin
import plugins.ieee1159_voltage_plugin
import plugins.semi_f47_plugin
import plugins.system_stats_plugin
import plugins.threshold_optimization_plugin
import plugins.trigger_plugin
import services.brokers
import services.plugin_manager

# pylint: disable=C0103
logger = log.get_logger(__name__)


def usage():
    """Displays usage information"""
    logger.info("Usage: ./opq_mauka.py")


def bootstrap_db(conf: config.MaukaConfig):
    """
    Performs bootstrapping of the database.
    :param conf: Configuration.
    """
    mongo_client: mongo.OpqMongoClient = mongo.from_config(conf)

    # Check to make sure a laha config exists
    if mongo_client.get_laha_config() is None:
        logger.info("laha_config DNE, inserting default from config...")
        mongo_client.laha_config_collection.insert_one(conf.get("laha.config.default"))

    # Indexes
    mongo_client.measurements_collection.create_index("expire_at")
    mongo_client.trends_collection.create_index("expire_at")
    mongo_client.events_collection.create_index("expire_at")
    mongo_client.incidents_collection.create_index("expire_at")


def bootstrap(conf: config.MaukaConfig):
    """
    Performs any bootstrapping.
    :param conf: Configuration.
    """
    bootstrap_db(conf)


def main():
    """
    Entry point to OPQ Mauka.
    """
    logger.info("Starting OpqMauka")
    conf = config.from_env(constants.CONFIG_ENV)

    bootstrap(conf)

    plugin_manager = services.plugin_manager.PluginManager(conf)
    plugin_manager.register_plugin(plugins.annotation_plugin.AnnotationPlugin)
    plugin_manager.register_plugin(plugins.box_optimization_plugin.BoxOptimizationPlugin)
    plugin_manager.register_plugin(plugins.frequency_variation_plugin.FrequencyVariationPlugin)
    plugin_manager.register_plugin(plugins.ieee1159_voltage_plugin.Ieee1159VoltagePlugin)
    plugin_manager.register_plugin(plugins.itic_plugin.IticPlugin)
    plugin_manager.register_plugin(plugins.laha_gc_plugin.LahaGcPlugin)
    plugin_manager.register_plugin(plugins.makai_event_plugin.MakaiEventPlugin)
    plugin_manager.register_plugin(plugins.outage_plugin.OutagePlugin)
    plugin_manager.register_plugin(plugins.semi_f47_plugin.SemiF47Plugin)
    plugin_manager.register_plugin(plugins.status_plugin.StatusPlugin)
    plugin_manager.register_plugin(plugins.system_stats_plugin.SystemStatsPlugin)
    plugin_manager.register_plugin(plugins.thd_plugin.ThdPlugin)
    plugin_manager.register_plugin(plugins.threshold_optimization_plugin.ThresholdOptimizationPlugin)
    plugin_manager.register_plugin(plugins.transient_plugin.TransientPlugin)
    plugin_manager.register_plugin(plugins.trigger_plugin.TriggerPlugin)

    broker_process = None
    makai_bridge_event_process = None
    if conf.get("mauka.startPubSubBroker"):
        broker_process = services.brokers.start_mauka_pub_sub_broker(conf)

    if conf.get("mauka.startEventBroker"):
        makai_bridge_event_process = services.brokers.start_makai_event_bridge(conf)

    incident_id_process = services.brokers.start_incident_id_service(conf)

    # start-stop-daemon sends a SIGTERM, we need to handle it to gracefully shutdown mauka
    def sigterm_handler(signum, frame):
        """
        Custom sigterm handler.
        :param signum: Number of the signal.
        :param frame: Frame of signal.
        """
        logger.info("Received exit signal %s %s", str(signum), str(frame))
        if conf.get("mauka.startPlugins"):
            plugin_manager.clean_exit()

    signal.signal(signal.SIGTERM, sigterm_handler)
    signal.signal(signal.SIGINT, sigterm_handler)

    try:
        if conf.get("mauka.startPlugins"):
            plugin_manager.run_all_plugins()
            plugin_manager.start_tcp_server()

        if broker_process is not None:
            logger.info("Killing broker process")
            broker_process.terminate()

        if makai_bridge_event_process is not None:
            logger.info("Killing makai event bridge process")
            makai_bridge_event_process.terminate()

        if incident_id_process is not None:
            logger.info("Killing incident id process")
            incident_id_process.terminate()

        logger.info("Goodbye")
        sys.exit(0)
    except KeyboardInterrupt:
        sigterm_handler(None, None)


if __name__ == "__main__":
    main()
