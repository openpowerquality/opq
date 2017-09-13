"""
This module contains a plugin that prints every message
"""

import typing

import plugins.base


def run_plugin(config: typing.Dict):
    """Runs this plugin using the given configuration

    :param config: Configuration dictionary
    """
    plugins.base.run_plugin(PrintPlugin, config)


class PrintPlugin(plugins.base.MaukaPlugin):
    """
    This class contains a plugin that prints every message
    """
    def __init__(self, config: typing.Dict):
        """ Initializes this plugin

        :param config: Configuration dictionary
        """
        super().__init__(config, [""], "PrintPlugin")

    def on_message(self, topic, message):
        """Subscribed messages occur async

        Messages are printed to stdout

        :param topic: The topic that this message is associated with
        :param message: The message
        """
        print("topic: {} message: {}...".format(topic, str(message)[:30]))
