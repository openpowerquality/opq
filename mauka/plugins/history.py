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
    client = mongo.mongo.get_default_client(mongo_client)
    broker = config["zmq.mauka.plugin.pub.interface"]
    event_ids_sans_thd = client.data_collection.find({"thd": {"$exists": False}})
    for event_id in event_ids_sans_thd:
        plugins.mock.produce(broker, "ThdRequestEvent", str(event_id))
        time.sleep(1)


def update_events_itic():
    pass


if __name__ == "__main__":
    config = load_config(sys.argv[1])
    update_events_thd(config)
