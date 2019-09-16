"""
This module provides methods for modifying thresholds dynamically.
"""

import multiprocessing
import time
import typing

import zmq

import config
import plugins.base_plugin
import protobuf.pb_util as pb_util

PLUGIN_NAME = "BoxOptimizationPlugin"
SUBSCRIBED_TOPICS = ["BoxOptimizationRequest"]

def timestamp_ms() -> int:
    """
    :return: The current timestamp as milliseconds since the epoch.
    """
    return int(round(time.time() * 1000.0))


def maybe_debug(msg: str, box_optimization_plugin: typing.Optional['BoxOptimizationPlugin'] = None):
    if box_optimization_plugin is not None:
        box_optimization_plugin.debug(msg)
    else:
        print(msg)


class BoxOptimizationRecords:
    def __init__(self, box_optimization_plugin: typing.Optional['BoxOptimizationPlugin'] = None):
        self.records: typing.Dict[str, int] = dict()
        self.lock = multiprocessing.RLock()
        self.box_optimization_plugin = box_optimization_plugin

    def prune(self):
        now = timestamp_ms()
        with self.lock:
            for record, timestamp in self.records.items():
                if now - timestamp > 1_000 * 60 * 10:  # 10 minutes
                    maybe_debug("Removing orphan box optimization record %s" % record, self.box_optimization_plugin)
                    del self.records[record]

    def add_record(self, record_id: str):
        with self.lock:
            self.records[record_id] = timestamp_ms()

    def check_record(self, record_id: str):
        with self.lock:
            if record_id not in self.records:
                maybe_debug("Removing orphan box optimization record %s" % record_id, self.box_optimization_plugin)

def modify_measurement_window_cycles(makai_send_socket: zmq.Socket,
                                     box_ids: typing.List[str],
                                     measurement_window_cycles: int,
                                     box_optimization_plugin: typing.Optional['BoxOptimizationPlugin'] = None):
    maybe_debug("Modifying measurement_window_cycles=%d for %s" % (measurement_window_cycles, str(box_ids)),
                box_optimization_plugin)

    box_commands = pb_util.build_makai_rate_change_commands(box_ids, measurement_window_cycles)

    for (box_command, identity) in box_commands:
        serialized_box_command = pb_util.serialize_message(box_command)
        makai_send_socket.send(serialized_box_command)


class BoxOptimizationPlugin(plugins.base_plugin.MaukaPlugin):
    """
    This class provides a plugin for dynamically optimizing Boxes.
    """

    NAME = PLUGIN_NAME

    # noinspection PyUnresolvedReferences
    # pylint: disable=E1101
    def __init__(self, conf: config.MaukaConfig, exit_event: multiprocessing.Event):
        """ Initializes this plugin

        :param conf: Configuration dictionary
        """
        super().__init__(conf, SUBSCRIBED_TOPICS, BoxOptimizationPlugin.NAME, exit_event)
        zmq_context = zmq.Context()
        self.makai_send_interface: str = conf.get("zmq.trigger.interface")
        self.makai_recv_interface: str = conf.get("zmq.data.interface")
        self.makai_send_socket = zmq_context.socket(zmq.PUSH)
        self.makai_send_socket.connect(self.makai_send_interface)

    def on_message(self, topic: str, mauka_message: pb_util.mauka_pb2.MaukaMessage):
        """
        Called when this plugin receives a message.
        :param topic: The topic that this message is associated with
        :param mauka_message: The message
        """
        if pb_util.is_box_optimization_request(mauka_message):
            self.debug("Recv box optimization request %s" % str(mauka_message))
            box_optimization_request = mauka_message.box_optimization_request
            modify_measurement_window_cycles(self.makai_send_socket,
                                             box_optimization_request.box_ids,
                                             box_optimization_request.measurement_window_cycles,
                                             self)
        else:
            self.logger.error("Received incorrect type of MaukaMessage :%s", str(mauka_message))


if __name__ == "__main__":
    import logging

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    logger.info("Starting test")

    trigger_interface = "tcp://127.0.0.1:9884"
    data_interface = "tcp://127.0.0.1:9899"
    event_id_interface = "tcp://127.0.0.1:10001"

    zmq_context = zmq.Context()

    zmq_trigger_socket = zmq_context.socket(zmq.PUSH)
    zmq_trigger_socket.connect(trigger_interface)

    cmd_socket = zmq_context.socket(zmq.SUB)
    cmd_socket.setsockopt(zmq.SUBSCRIBE, "maukainfo_".encode())
    cmd_socket.connect(data_interface)

    cmd, ident = pb_util.build_makai_get_info_cmd("1006")
    zmq_trigger_socket.send(pb_util.serialize_message(cmd))

    while True:
        resp = cmd_socket.recv_multipart()
        identity = resp[0]
        payload = resp[1]
        print(resp)
        print(identity)
        print(payload)
        response = pb_util.opqbox3_pb2.Response()
        response.ParseFromString(payload)
        print(response)


