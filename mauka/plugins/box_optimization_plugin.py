"""
This module provides methods for modifying Box measurement send rate dynamically.
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
from plugins.routes import Routes
PLUGIN_NAME = "BoxOptimizationPlugin"
SUBSCRIBED_TOPICS = [Routes.box_optimization_request,
                     Routes.box_measurement_rate_request]


def timestamp_ms() -> int:
    """
    :return: The current timestamp as milliseconds since the epoch.
    """
    return int(round(time.time() * 1000.0))


class BoxOptimizationPluginLogger:
    """
    This class represents a generic logger than can work with either Mauka plugins, a logger, or send data to stdout.
    """

    def __init__(self,
                 loggable: typing.Optional[typing.Union['BoxOptimizationPlugin', logging.Logger]] = None):
        """
        :param loggable: Either an optional instance of the BoxOptimizationPlugin or an optional instance of a logger.
        """
        self.log_interface: typing.Optional[logging.Logger] = None
        self.plugin_interface: typing.Optional['BoxOptimizationPlugin'] = None

        if loggable is not None:
            if isinstance(loggable, BoxOptimizationPlugin):
                self.plugin_interface = loggable

            if isinstance(loggable, logging.Logger):
                self.log_interface = loggable

    def _default(self, msg: str):
        """
        If not logger or plugin instance exists, then write the output to stdout.
        :param msg: The message to write to stdout.
        """
        print(msg)

    def debug(self, msg: str):
        """
        Log a debug message.
        :param msg: The message to log.
        """
        if self.plugin_interface is not None:
            self.plugin_interface.debug(msg)
        elif self.log_interface is not None:
            self.log_interface.debug(msg)
        else:
            self._default(msg)

    def info(self, msg: str):
        """
        Log an info message.
        :param msg: The message to log.
        """
        if self.log_interface is not None:
            self.log_interface.info(msg)
        else:
            self._default("info: " + msg)

    def warn(self, msg: str):
        """
        Log a warn message.
        :param msg: The message to log.
        """
        if self.log_interface is not None:
            self.log_interface.warning(msg)
        else:
            self._default("warn: " + msg)

    def error(self, msg: str):
        """
        Log an error message.
        :param msg: The message to log.
        """
        if self.log_interface is not None:
            self.log_interface.error(msg)
        else:
            self._default("error: " + msg)


class BoxOptimizationRecords:
    """
    This class provides thread safe access to optimization request and response records.
    """

    def __init__(self, logger: BoxOptimizationPluginLogger):
        self.records: typing.Dict[str, int] = dict()
        self.lock = multiprocessing.RLock()
        self.logger = logger

    def __prune(self):
        """
        Prunes any old records that have not received a response in over 10 minutes.
        """
        now = timestamp_ms()
        self.logger.debug("Pruning records.")
        for record, timestamp in self.records.items():
            if now - timestamp > 1_000 * 60 * 10:  # 10 minutes
                self.logger.error("Removing orphaned record %s" % record)
                del self.records[record]

    def add_record(self, record_id: str):
        """
        Adds a new record to the record set.
        :param record_id: The record id to add.
        """
        self.logger.debug("Adding record %s" % record_id)
        with self.lock:
            self.records[record_id] = timestamp_ms()
            self.__prune()

    def check_record(self, record_id: str):
        """
        Checks an existing record in the record set.
        :param record_id: The record to check.
        """
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
    # pylint: disable=E1101
    def __init__(self,
                 makai_recv_interface: str,
                 box_optimization_records: BoxOptimizationRecords,
                 logger: BoxOptimizationPluginLogger,
                 box_optimization_plugin: typing.Optional['BoxOptimizationPlugin'] = None):

        super().__init__()

        # ZMQ
        self.zmq_context = zmq.Context()
        self.zmq_socket = self.zmq_context.socket(zmq.SUB)
        self.zmq_socket.setsockopt(zmq.SUBSCRIBE, "maukarate_".encode())
        self.zmq_socket.setsockopt(zmq.SUBSCRIBE, "maukainfo_".encode())
        self.zmq_socket.connect(makai_recv_interface)

        # Thead-safe box optimization records
        self.box_optimization_records = box_optimization_records

        # Logging
        self.logger = logger

        self.box_optimization_plugin = box_optimization_plugin

    # pylint: disable=E1101
    # noinspection PyUnresolvedReferences
    def run(self):
        """
        Run loop which continuously attempts to receive triggered data from Makai.
        """
        self.logger.info("MakaiDataSubscriber thread started")
        while True:
            # Receive data and extract parameters
            self.logger.debug("Recv resp.")
            data = self.zmq_socket.recv_multipart()
            identity = data[0].decode()
            response = pb_util.deserialize_makai_response(data[1])
            if pb_util.is_makai_message_rate_response(response):
                self.logger.debug("Recv makai message rate response %s" % str(response))
                self.box_optimization_records.check_record(identity)
            elif pb_util.is_makai_info_response(response) and self.box_optimization_plugin is not None:
                self.logger.debug("Recv box info response")
                self.box_optimization_records.check_record(identity)
                info_response = response.info_response
                if info_response.measurement_rate > 0:
                    box_measurement_rate_response = pb_util.build_box_measurement_rate_response(
                        "box_optimization_plugin",
                        str(response.box_id),
                        info_response.measurement_rate)
                    self.box_optimization_plugin.produce(Routes.box_measurement_rate_response,
                                                         box_measurement_rate_response)
            else:
                self.logger.error("Recv incorrect resp type")


def modify_measurement_window_cycles(makai_send_socket: zmq.Socket,
                                     box_ids: typing.List[str],
                                     measurement_window_cycles: int,
                                     box_optimization_records: BoxOptimizationRecords,
                                     logger: BoxOptimizationPluginLogger):
    """
    Dynamically modifies the measurement rate of boxes.
    :param makai_send_socket: The ZMQ socket to send modification requests to.
    :param box_ids: A list of box ids to modify.
    :param measurement_window_cycles: Number of cycles in a measurement.
    :param box_optimization_records: Thread safe req/resp of records.
    :param logger: The logger.
    """

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


def send_box_info_cmds(makai_send_socket: zmq.Socket,
                       box_ids: typing.List[str],
                       box_optimization_records: BoxOptimizationRecords,
                       logger: BoxOptimizationPluginLogger):
    """
    Send info requests to Makai.
    :param makai_send_socket: The makai ZMQ socket.
    :param box_ids: List of box ids to request the info for.
    :param box_optimization_records: Records.
    :param logger: Logger.
    """
    logger.debug("Sending info commands to Makai for the following boxes: %s" % str(box_ids))
    for box_id in box_ids:
        cmd, identity = pb_util.build_makai_get_info_command(box_id)
        box_optimization_records.add_record(identity)
        serialized_cmd = pb_util.serialize_message(cmd)
        makai_send_socket.send(serialized_cmd)
        logger.debug("Sent box info command %s" % str(cmd))


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
                                                                                       self.box_optimization_logger,
                                                                                       self)

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
                                             self.box_optimization_logger)
        if pb_util.is_box_measurement_rate_request(mauka_message):
            self.box_optimization_logger.debug("Recv box measurement rate request: %s" % str(mauka_message))
            send_box_info_cmds(self.makai_send_socket,
                               mauka_message.box_measurement_rate_request.box_ids,
                               self.box_optimization_records,
                               self.box_optimization_logger)
        else:
            self.box_optimization_logger.error("Received incorrect type of MaukaMessage :%s" % str(mauka_message))

# if __name__ == "__main__":
#     import logging
#
#     logger = logging.getLogger()
#     logger.setLevel(logging.DEBUG)
#
#     logger.info("Starting test")
#
#     trigger_interface = "tcp://127.0.0.1:9884"
#     data_interface = "tcp://127.0.0.1:9899"
#
#     zmq_context = zmq.Context()
#
#     zmq_trigger_socket = zmq_context.socket(zmq.PUSH)
#     zmq_trigger_socket.connect(trigger_interface)
#
#     cmd_socket = zmq_context.socket(zmq.SUB)
#     cmd_socket.setsockopt(zmq.SUBSCRIBE, "maukainfo_".encode())
#     cmd_socket.connect(data_interface)
#
#     opt_logger = BoxOptimizationPluginLogger(logger)
#     box_optimization_records = BoxOptimizationRecords(opt_logger)
#     makai_data_subscriber = MakaiOptimizationResultSubscriber(data_interface,
#                                                               box_optimization_records,
#                                                               opt_logger)
#
#     makai_data_subscriber.start()
#
#     modify_measurement_window_cycles(zmq_trigger_socket,
#                                      ["1004", "1006"],
#                                      60,
#                                      box_optimization_records,
#                                      opt_logger)
