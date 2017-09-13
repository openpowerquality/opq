"""
This module contains a plugin that reports and records the status of other plugins in the system
"""

import typing

import plugins.base


def run_plugin(config: typing.Dict):
    """Runs this plugin using the given configuration

    :param config: Configuration dictionary
    """
    plugins.base.run_plugin(StatusPlugin, config)


class StatusPlugin(plugins.base.MaukaPlugin):
    """
    This module contains a plugin that reports and records the status of other plugins in the system
    """
    def __init__(self, config: typing.Dict):
        """ Initializes this plugin

        :param config: Configuration dictionary
        """
        super().__init__(config, ["heartbeat"], "StatusPlugin")

    def on_message(self, topic, message):
        """Subscribed messages occur async

        Messages are printed to stdout

        :param topic: The topic that this message is associated with
        :param message: The message
        """
        print("status", topic, message)
