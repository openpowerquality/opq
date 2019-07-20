"""
This module contains a plugin that provides capabilities for triggering boxes through Makai.
"""

import multiprocessing
import typing
import uuid
import zmq

import config
import plugins.base_plugin
import protobuf.pb_util as pb_util
import protobuf.opqbox3_pb2 as opqbox3_pb2


def trigger_boxes_future(conf: config.MaukaConfig, trigger_commands: typing.List[opqbox3_pb2]):
    # Send commands to Makai acq broker
    zmq_context = zmq.Context()
    zmq_socket = zmq_context.socket(zmq.PUSH)
    zmq_socket = conf.

    # Receive results from acquisition broker

    # Return results
    pass


def trigger_boxes(conf: config.MaukaConfig,
                  start_timestamp_ms: int,
                  end_timestamp_ms: int,
                  box_ids: typing.List[str],
                  incident_id: int,
                  source: str) -> str:
    event_token = str(uuid.uuid4())
    trigger_commands = pb_util.build_makai_trigger_commands(start_timestamp_ms,
                                                            end_timestamp_ms,
                                                            box_ids,
                                                            event_token,
                                                            source)

    return event_token


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
    for cmd in cmds:
        print(cmd)
