#!/usr/bin/env python3

import plugins

import json
import logging
import os
import sys

_logger = logging.getLogger("app")
logging.basicConfig(
    format="[%(levelname)s][%(asctime)s][{} %(filename)s:%(lineno)s - %(funcName)s() ] %(message)s".format(
        os.getpid()))
_logger.setLevel(logging.DEBUG)


def usage():
    _logger.info("Usage: ./OpqMauka.py [config file]")


def load_config(path):
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

    plugins_list = [
        #plugins.PrintPlugin,
        plugins.MeasurementShimPlugin,
        plugins.MeasurementPlugin,
        plugins.FrequencyThresholdPlugin,
        plugins.VoltageThresholdPlugin,
        plugins.AcquisitionTriggerPlugin,
        plugins.StatusPlugin
    ]

    processes = []

    for plugin in plugins_list:
        try:
            plugin.run_plugin(config)
        except KeyError as e:
            _logger.error("Could not load plugin due to configuration error: {}".format(e))
