"""
This module contains a plugin that reports and records the status of other plugins in the system
"""

import multiprocessing
import typing

import plugins.base


class StatusPlugin(plugins.base.MaukaPlugin):
    """
    This module contains a plugin that reports and records the status of other plugins in the system
    """

    NAME = "StatusPlugin"

    def __init__(self, config: typing.Dict, exit_event: multiprocessing.Event):
        """ Initializes this plugin

        :param config: Configuration dictionary
        """
        super().__init__(config, ["heartbeat"], StatusPlugin.NAME, exit_event)

    def on_message(self, topic, message):
        """Subscribed messages occur async

        Messages are printed to stdout

        :param topic: The topic that this message is associated with
        :param message: The message
        """
        self.logger.info("{}:{}",format(topic, message))
