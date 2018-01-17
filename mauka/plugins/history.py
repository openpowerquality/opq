"""
This module contains utilities for running new plugins over historical data.
This is mainly achieved my injecting messages into a live system that cause plugins to run over specific historic data.
"""

import mongo.mongo
import plugins.mock

import json
import logging
import os
import sys
import time
import typing

_logger = logging.getLogger("app")
logging.basicConfig(
        format="[%(levelname)s][%(asctime)s][{} %(filename)s:%(lineno)s - %(funcName)s() ] %(message)s".format(
                os.getpid()))
_logger.setLevel(logging.DEBUG)


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
        exit(0)


def update_events_thd(config: typing.Dict, mongo_client: mongo.mongo.OpqMongoClient = None):
    """
    Update THD values for all events with data that do not have a THD calculation.
    :param config: Mauka configuration.
    :param mongo_client: Instance of a mongo client
    """
    client = mongo.mongo.get_default_client(mongo_client)
    broker = config["zmq.mauka.plugin.pub.interface"]
    box_events = client.box_events_collection.find({"thd": {"$exists": False}},
                                                         ["event_id"])

    unique_event_ids = set(list(map(lambda box_event: box_event["event_id"], box_events)))
    for event_id in unique_event_ids:
        plugins.mock.produce(broker, "ThdRequestEvent", str(event_id))
        time.sleep(.25)



def update_events_itic(config: typing.Dict, mongo_client: mongo.mongo.OpqMongoClient = None):
    client = mongo.mongo.get_default_client(mongo_client)
    broker = config["zmq.mauka.plugin.pub.interface"]
    box_events = client.box_events_collection.find({"itic": {"$exists": False}},
                                                   ["event_id"])

    unique_event_ids = set(list(map(lambda box_event: box_event["event_id"], box_events)))
    for event_id in unique_event_ids:
        plugins.mock.produce(broker, "IticRequestEvent", str(event_id))
        time.sleep(.25)



if __name__ == "__main__":
    """
    Entry point when ran as a script.
    """
    config = load_config(sys.argv[1])
    mongo_client = mongo.mongo.get_default_client()
    update_events_thd(config, mongo_client)
    update_events_itic(config, mongo_client)
