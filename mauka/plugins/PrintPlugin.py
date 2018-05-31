"""
This module contains a plugin that prints every message
"""

import multiprocessing
import typing

import plugins.base
import protobuf.util


class PrintPlugin(plugins.base.MaukaPlugin):
    """
    This class contains a plugin that prints every message
    """

    NAME = "PrintPlugin"

    def __init__(self, config: typing.Dict, exit_event: multiprocessing.Event):
        """ Initializes this plugin

        :param config: Configuration dictionary
        """
        super().__init__(config, [""], PrintPlugin.NAME, exit_event)

    def on_message(self, topic, mauka_message_bytes):
        """Subscribed messages occur async

        Messages are printed to stdout

        :param topic: The topic that this message is associated with
        :param message: The message
        """
        mauka_message = protobuf.util.deserialize_mauka_message(mauka_message_bytes)
        self.logger.info("topic: {} message: {}...".format(topic, mauka_message))
