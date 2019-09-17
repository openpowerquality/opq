"""
This module provides methods for modifying thresholds dynamically.
"""

import logging
import multiprocessing
import threading
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


class BoxOptimizationPluginLogger:
    def __init__(self,
                 loggable: typing.Optional[typing.Union['BoxOptimizationPlugin', logging.Logger]] = None):
        self.log_interface = None
        self.plugin_interface = None

        if loggable is not None:
            if isinstance(loggable, BoxOptimizationPlugin):
                self.plugin_interface = loggable

            if isinstance(loggable, logging.Logger):
                self.log_interface = loggable

    def _default(self, msg: str):
        print(msg)

    def debug(self, msg: str):
        if self.plugin_interface is not None:
            self.plugin_interface.debug(msg)
        elif self.log_interface is not None:
            self.log_interface.debug(msg)
        else:
            self._default(msg)

    def info(self, msg: str):
        if self.log_interface is not None:
            self.log_interface.info(msg)
        else:
            self._default(msg)

    def warn(self, msg: str):
        if self.log_interface is not None:
            self.log_interface.warning(msg)
        else:
            self._default(msg)

    def error(self, msg: str):
        if self.log_interface is not None:
            self.log_interface.error(msg)
        else:
            self._default(msg)


class BoxOptimizationRecords:
    def __init__(self, logger: BoxOptimizationPluginLogger):
        self.records: typing.Dict[str, int] = dict()
        self.lock = multiprocessing.RLock()
        self.logger = logger

    def __prune(self):
        now = timestamp_ms()
        self.logger.debug("Pruning records.")
        for record, timestamp in self.records.items():
            if now - timestamp > 1_000 * 60 * 10:  # 10 minutes
                self.logger.error("Removing orphaned record %s" % record)
                del self.records[record]

    def add_record(self, record_id: str):
        self.logger.debug("Adding record %s" % record_id)
        with self.lock:
            self.records[record_id] = timestamp_ms()
            self.__prune()

    def check_record(self, record_id: str):
        with self.lock:
            if record_id not in self.records:
                self.logger.error("Box optimization record with id %s not found" % record_id)
            else:
                self.logger.debug("Removing record %s after response" % record_id)
                del self.records[record_id]
            self.__prune()


class MakaiOptimizationResultSubscriber(threading.Thread):
    """
    This class handles receiving triggered data back from Makai. This class is ran in a separate thread.
    """

    # noinspection PyUnresolvedReferences
    def __init__(self,
                 makai_recv_interface: str,
                 box_optimization_records: BoxOptimizationRecords,
                 logger: BoxOptimizationPluginLogger):

        super().__init__()

        # ZMQ
        self.zmq_context = zmq.Context()
        self.zmq_socket = self.zmq_context.socket(zmq.SUB)
        self.zmq_socket.setsockopt(zmq.SUBSCRIBE, "maukarate_".encode())
        self.zmq_socket.connect(makai_recv_interface)

        # Thead-safe box optimization records
        self.box_optimization_records = box_optimization_records

        # Logging
        self.logger = logger

    # pylint: disable=E1101
    # noinspection PyUnresolvedReferences
    def run(self):
        """
        Run loop which continuously attempts to receive triggered data from Makai.
        """
        self.logger.info("MakaiDataSubscriber thread started")
        while True:
            # Receive data and extract parameters
            self.logger.debug("Recv optimization resp.")
            data = self.zmq_socket.recv_multipart()
            identity = data[0].decode()
            response = pb_util.opqbox3_pb2.Response()
            response.ParseFromString(data[1])
            self.logger.debug("Recv optimization response %s" % str(response))
            self.box_optimization_records.check_record(identity)


def modify_measurement_window_cycles(makai_send_socket: zmq.Socket,
                                     box_ids: typing.List[str],
                                     measurement_window_cycles: int,
                                     box_optimization_records: BoxOptimizationRecords,
                                     logger: BoxOptimizationPluginLogger):

    if measurement_window_cycles <= 0:
        logger.error("measurement_window_cycles must be strictly larger than 0")
        return

    logger.debug("Modifying measurement_window_cycles=%d for %s" % (measurement_window_cycles, str(box_ids)))

    box_commands = pb_util.build_makai_rate_change_commands(box_ids, measurement_window_cycles)

    for (box_command, identity) in box_commands:
        serialized_box_command = pb_util.serialize_message(box_command)
        makai_send_socket.send(serialized_box_command)
        box_optimization_records.add_record(identity)
        logger.debug("Sent optimization request command with identity=%s" % identity)


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

        # Logging
        self.box_optimization_logger = BoxOptimizationPluginLogger(self)

        # ZMQ
        zmq_context = zmq.Context()
        self.makai_send_interface: str = conf.get("zmq.trigger.interface")
        self.makai_recv_interface: str = conf.get("zmq.data.interface")
        self.makai_send_socket = zmq_context.socket(zmq.PUSH)
        self.makai_send_socket.connect(self.makai_send_interface)

        # Box optimization records
        self.box_optimization_records = BoxOptimizationRecords(self.box_optimization_logger)

        # Start up the subscription thread
        self.makai_optimization_results_subscriber = MakaiOptimizationResultSubscriber(self.makai_recv_interface,
                                                                                       self.box_optimization_records,
                                                                                       self.logger)

        self.makai_optimization_results_subscriber.start()

    def on_message(self, topic: str, mauka_message: pb_util.mauka_pb2.MaukaMessage):
        """
        Called when this plugin receives a message.
        :param topic: The topic that this message is associated with
        :param mauka_message: The message
        """
        if pb_util.is_box_optimization_request(mauka_message):
            self.box_optimization_logger.debug("Recv box optimization request %s" % str(mauka_message))
            box_optimization_request = mauka_message.box_optimization_request
            modify_measurement_window_cycles(self.makai_send_socket,
                                             box_optimization_request.box_ids,
                                             box_optimization_request.measurement_window_cycles,
                                             self.box_optimization_records,
                                             self.logger)
        else:
            self.box_optimization_logger.error("Received incorrect type of MaukaMessage :%s" % str(mauka_message))


if __name__ == "__main__":
    import logging

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    logger.info("Starting test")

    trigger_interface = "tcp://127.0.0.1:9884"
    data_interface = "tcp://127.0.0.1:9899"

    zmq_context = zmq.Context()

    zmq_trigger_socket = zmq_context.socket(zmq.PUSH)
    zmq_trigger_socket.connect(trigger_interface)

    cmd_socket = zmq_context.socket(zmq.SUB)
    cmd_socket.setsockopt(zmq.SUBSCRIBE, "maukainfo_".encode())
    cmd_socket.connect(data_interface)

    opt_logger = BoxOptimizationPluginLogger(logger)
    box_optimization_records = BoxOptimizationRecords(opt_logger)
    makai_data_subscriber = MakaiOptimizationResultSubscriber(data_interface,
                                                              box_optimization_records,
                                                              opt_logger)

    makai_data_subscriber.start()

    modify_measurement_window_cycles(zmq_trigger_socket,
                                     ["1006"],
                                     60,
                                     box_optimization_records,
                                     opt_logger)
