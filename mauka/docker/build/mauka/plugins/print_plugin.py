"""
This module contains a plugin that prints every message
"""

import multiprocessing

import config
import plugins.base_plugin


class PrintPlugin(plugins.base_plugin.MaukaPlugin):
    """
    This class contains a plugin that prints every message
    """

    NAME = "PrintPlugin"

    def __init__(self, conf: config.MaukaConfig, exit_event: multiprocessing.Event):
        """ Initializes this plugin

        :param conf: Configuration dictionary
        """
        super().__init__(conf, [""], PrintPlugin.NAME, exit_event)

    def on_message(self, topic, mauka_message):
        """Subscribed messages occur async

        Messages are printed to stdout

        :param topic: The topic that this message is associated with
        :param mauka_message: The message
        """
        self.logger.info("topic: %s message: %s", str(topic), str(mauka_message))
