"""
This module contains the plugin for Future Phenomena.
"""
import collections
import datetime
import functools
from dataclasses import dataclass
import time
from typing import DefaultDict, Dict, List, Optional, Set, TypeVar
import threading

import config
import numpy as np
import scipy.signal
from log import maybe_debug
import mongo
import plugins.base_plugin
import protobuf.mauka_pb2
import protobuf.pb_util
import pymongo
import pymongo.database

from plugins.routes import Routes


def schedule_future_phenomena(interval_s: float,
                              opq_mongo_client: mongo.OpqMongoClient,
                              periodicity_plugin: 'FuturePlugin'):
    """

    """

    timer: threading.Timer = threading.Timer(interval_s,
                                             schedule_future_phenomena,
                                             (interval_s,
                                              opq_mongo_client,
                                              periodicity_plugin))
    timer.start()


class FuturePlugin(plugins.base_plugin.MaukaPlugin):
    """
    A Future Phenomena plugin.
    """
    NAME: str = "FuturePlugin"

    def __init__(self, conf: config.MaukaConfig, exit_event):
        super().__init__(conf, [], FuturePlugin.NAME, exit_event)
        schedule_future_phenomena(3600,
                                  self.mongo_client,
                                  self)

    def on_message(self, topic: str, mauka_message: protobuf.mauka_pb2.MaukaMessage):
        """

        :param topic:
        :param mauka_message:
        :return:
        """
        self.logger.warning("Received message: %s", str(mauka_message))
