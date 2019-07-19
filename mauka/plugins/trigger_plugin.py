"""
This module contains a plugin that provides capabilities for triggering boxes through Makai.
"""

import multiprocessing
import typing

import config
import plugins.base_plugin
import protobuf.pb_util as pb_util


def trigger_boxes(start_timestamp_ms: int,
                  stop_timestamp_ms: int,
                  box_ids: typing.List[str],
                  incident_id: int) -> str:
    pass


class TriggerPlugin(plugins.base_plugin.MaukaPlugin):
    """
    This class contains a plugin that prints every message
    """

    NAME = "TriggerPlugin"

    def __init__(self, conf: config.MaukaConfig, exit_event: multiprocessing.Event):
        """ Initializes this plugin

        :param conf: Configuration dictionary
        """
        super().__init__(conf, ["TriggerRequest"], TriggerPlugin.NAME, exit_event)

    def on_message(self, topic, mauka_message):
        """Subscribed messages occur async

        Messages are printed to stdout

        :param topic: The topic that this message is associated with
        :param mauka_message: The message
        """
        if pb_util.is_trigger_request(mauka_message):
            trigger_boxes(mauka_message.trigger_request.start_timestamp_ms,
                          mauka_message.trigger_request.end_timestamp_ms,
                          mauka_message.trigger_request.box_ids,
                          mauka_message.trigger_request.incident_id)
        else:
            self.logger.error("Received incorrect type of MaukaMessage :%s" % str(mauka_message))


if __name__ == "__main__":
    cmds = pb_util.build_makai_trigger_commands(0, 1, ["1", "2", "3"], "et", "uuid")
