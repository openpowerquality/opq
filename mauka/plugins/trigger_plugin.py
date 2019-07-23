"""
This module contains a plugin that provides capabilities for triggering boxes through Makai.
"""

import concurrent.futures as futures
import multiprocessing
import typing
import uuid

import zmq

import config
import plugins.base_plugin
import protobuf.pb_util as pb_util


def on_data_recv(future: futures.Future):
    try:
        exception = future.exception()
        if exception is not None:
            print("Error receiving data in trigger plugin: %s" % str(exception))
            return

        result = future.result()
        print(result)

    except futures.TimeoutError as e:
        print("trigger plugin futures timeout error: %s" % str(e))
    except futures.CancelledError as e:
        print("trigger plugin futures canceled error: %s" % str(e))


def trigger_boxes(zmq_trigger_interface: str,
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

    zmq_context = zmq.Context()
    zmq_socket = zmq_context.socket(zmq.PUSH)
    zmq_socket.connect(zmq_trigger_interface)

    for trigger_command in trigger_commands:
        zmq_socket.send(pb_util.serialize_message(trigger_command))

    # Receive results from acquisition broker

    return event_token


def trigger_boxes_async(executor: futures.ThreadPoolExecutor,
                        zmq_trigger_interface: str,
                        start_timestamp_ms: int,
                        end_timestamp_ms: int,
                        box_ids: typing.List[str],
                        incident_id: int,
                        source: str,
                        on_data_recv: typing.Callable[[str], None]):
    future: futures.Future = executor.submit(trigger_boxes,
                                             zmq_trigger_interface,
                                             start_timestamp_ms,
                                             end_timestamp_ms,
                                             box_ids,
                                             incident_id,
                                             source)

    future.add_done_callback(on_data_recv)


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
        self.zmq_trigger_interface: str = conf.get("zmq.trigger.interface")
        self.executor: futures.ThreadPoolExecutor = futures.ThreadPoolExecutor()

    def on_message(self, topic, mauka_message):
        """Subscribed messages occur async

        Messages are printed to stdout

        :param topic: The topic that this message is associated with
        :param mauka_message: The message
        """
        if pb_util.is_trigger_request(mauka_message):
            trigger_boxes_async(self.zmq_trigger_interface,
                                mauka_message.trigger_request.start_timestamp_ms,
                                mauka_message.trigger_request.end_timestamp_ms,
                                mauka_message.trigger_request.box_ids,
                                mauka_message.trigger_request.incident_id,
                                mauka_message.source)
        else:
            self.logger.error("Received incorrect type of MaukaMessage :%s" % str(mauka_message))

    if __name__ == "__main__":
        cmds = pb_util.build_makai_trigger_commands(0, 1, ["1", "2", "3"], "et", "uuid")
        for cmd in cmds:
            print(cmd)
