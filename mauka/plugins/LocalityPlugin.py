"""
This plugin calculates locality of PQ events.
"""
import math
import multiprocessing
import threading
import typing

import constants
import mongo.mongo
import plugins.base

import numpy
import scipy.fftpack


class LocalityPlugin(plugins.base.MaukaPlugin):
    """
    Mauka plugin that calculates locality.
    """
    NAME = "LocalityPlugin"

    def __init__(self, config: typing.Dict, exit_event: multiprocessing.Event):
        """
        Initializes this plugin
        :param config: Mauka configuration
        :param exit_event: Exit event that can disable this plugin from parent process
        """
        super().__init__(config, ["RequestDataEvent", "LocalityRequestEvent"], LocalityPlugin.NAME, exit_event)
        self.get_data_after_s = self.config["plugins.LocalityPlugin.getDataAfterS"]

    def perform_thd_calculation(self, event_id: int):
       pass

    def on_message(self, topic, message):
        """
        Fired when this plugin receives a message. This will wait a certain amount of time to make sure that data
        is in the database before starting thd calculations.
        :param topic: Topic of the message.
        :param message: Contents of the message.
        """
        event_id = int(message)
        timer = threading.Timer(self.get_data_after_s, self.perform_thd_calculation, (event_id,))
        timer.start()
