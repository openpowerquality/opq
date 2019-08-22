"""
This module contains a plugin that provides capabilities for triggering boxes through Makai.
"""

import concurrent.futures as futures
import multiprocessing
import threading
import time
import typing
import uuid

import zmq

import config
import plugins.base_plugin
import protobuf.pb_util as pb_util


def timestamp_ms() -> int:
    """
    :return: The current timestamp as milliseconds since the epoch.
    """
    return int(round(time.time() * 1000.0))


class MakaiDataSubscriber:
    """
    This class handles receiving triggered data back from Makai. This class is ran in a separate thread.
    """

    # pylint: disable=E1101
    def __init__(self, zmq_data_interface: str):
        self.zmq_context = zmq.Context()
        # noinspection PyUnresolvedReferences
        self.zmq_socket = self.zmq_context.socket(zmq.SUB)
        self.zmq_socket.connect(zmq_data_interface)
        # noinspection PyUnresolvedReferences
        self.zmq_socket.setsockopt(zmq.SUBSCRIBE, "".encode())

    def run(self):
        """
        Run loop which continuously attempts to receive triggered data from Makai.
        """
        while True:
            data = self.zmq_socket.recv_multipart()
            identity = data[0]
            response = pb_util.deserialize_makai_response(data[1])
            data = list(map(pb_util.deserialize_makai_cycle, data[2:]))
            print(identity, response, data)

    def start_thread(self):
        """
        Starts the data recv thread.
        """
        thread = threading.Thread(target=self.run)
        thread.start()


def trigger_boxes(zmq_trigger_interface: str,
                  start_timestamp_ms: int,
                  end_timestamp_ms: int,
                  box_ids: typing.List[str],
                  incident_id: int,
                  source: str) -> str:
    """
    This function triggers boxes through Makai.
    :param zmq_trigger_interface: Makai interface.
    :param start_timestamp_ms: Start of the requested data time window.
    :param end_timestamp_ms: End of the requested data time window.
    :param box_ids: A list of box ids to trigger.
    :param incident_id: The associated incident id.
    :param source: The source of the trigger (generally a plugin).
    :return: The event token.
    """
    event_token = str(uuid.uuid4())
    trigger_commands = pb_util.build_makai_trigger_commands(start_timestamp_ms,
                                                            end_timestamp_ms,
                                                            box_ids,
                                                            event_token,
                                                            source)
    zmq_context = zmq.Context()
    # pylint: disable=E1101
    # noinspection PyUnresolvedReferences
    zmq_socket = zmq_context.socket(zmq.PUSH)
    zmq_socket.connect(zmq_trigger_interface)

    for trigger_command in trigger_commands:
        try:
            zmq_socket.send(pb_util.serialize_message(trigger_command))
        except Exception as exception:  # pylint: disable=W0703
            print(exception)

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
        self.zmq_trigger_interface: str = conf.get("zmq.trigger.interface")
        self.zmq_data_interface: str = conf.get("zmq.data.interface")
        self.executor: futures.ThreadPoolExecutor = futures.ThreadPoolExecutor()

    def on_message(self, topic, mauka_message):
        """Subscribed messages occur async

        Messages are printed to stdout

        :param topic: The topic that this message is associated with
        :param mauka_message: The message
        """
        if pb_util.is_trigger_request(mauka_message):
            pass
        else:
            self.logger.error("Received incorrect type of MaukaMessage :%s", str(mauka_message))
