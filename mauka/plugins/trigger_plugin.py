"""
This module contains a plugin that provides capabilities for triggering boxes through Makai.
"""

import itertools
import logging
import multiprocessing
import threading
import time
import typing
import uuid

import zmq

import config
import mongo
import plugins.base_plugin
import protobuf.pb_util as pb_util


def next_event_id(event_id_socket: zmq.Socket) -> int:
    event_id_socket.send_string("")
    return int(event_id_socket.recv_string())


def timestamp_ms() -> int:
    """
    :return: The current timestamp as milliseconds since the epoch.
    """
    return int(round(time.time() * 1000.0))


def cycles_to_data(cycles: typing.List[pb_util.opqbox3_pb2.Cycle]) -> typing.List[int]:
    """
    Extracts all samples from the passed in cycles.
    :param cycles: Makai cycles.
    :return: A list of samples from the Makai cycles.
    """
    return list(itertools.chain(*map(lambda cycle: cycle.datapoints, cycles)))


def extract_timestamps(cycles: typing.List[pb_util.opqbox3_pb2.Cycle]) -> typing.Tuple[int, int]:
    """
    Extracts the first and last timestamps of the received cycles.
    :param cycles: Cycles to extract timestamps
    :return: A tuple containing the first and last timestamps from the cycles.
    """
    return cycles[0].timestamp_ms, cycles[-1].timestamp_ms


class TriggerRecords:
    def __init__(self):
        self.event_token_to_event_id: typing.Dict[str, int] = {}
        self.event_token_to_incident_id: typing.Dict[str, int] = {}
        self.event_token_to_timestamp_ms: typing.Dict[str, int] = {}
        self.event_token_to_triggered_boxes: typing.Dict[str, typing.Set[str]] = {}
        self.lock = multiprocessing.RLock()

    def __insert_record(self,
                        event_token: str,
                        event_id: int,
                        incident_id: int,
                        box_ids: typing.Set[str]):
        self.event_token_to_event_id[event_token] = event_id
        self.event_token_to_incident_id[event_token] = incident_id
        self.event_token_to_timestamp_ms[event_token] = timestamp_ms()
        self.event_token_to_triggered_boxes[event_token] = box_ids

    def insert_record(self,
                      event_token: str,
                      event_id: int,
                      incident_id: int,
                      box_ids: typing.Set[str]):
        with self.lock:
            self.__insert_record(event_token, event_id, incident_id, box_ids)

    def __remove_record(self, event_token: str):
        if event_token in self.event_token_to_event_id:
            del self.event_token_to_event_id[event_token]

        if event_token in self.event_token_to_event_id:
            del self.event_token_to_incident_id[event_token]

        if event_token in self.event_token_to_event_id:
            del self.event_token_to_timestamp_ms[event_token]

        if event_token in self.event_token_to_triggered_boxes:
            del self.event_token_to_triggered_boxes[event_token]

    def remove_record(self, event_token: str):
        with self.lock:
            self.__remove_record(event_token)

    def __prune(self):
        now = timestamp_ms()
        for event_token, ts_ms in self.event_token_to_timestamp_ms.items():
            if now - ts_ms > 1_000 * 3_600:  # 1 hour
                self.__remove_record(event_token)

    def prune(self):
        with self.lock:
            self.__prune()

    def event_id(self, event_token: str) -> int:
        with self.lock:
            if event_token in self.event_token_to_event_id:
                return self.event_token_to_event_id[event_token]

    def remove_box_id(self, event_token: str, box_id: str):
        with self.lock:
            if event_token in self.event_token_to_triggered_boxes:
                if box_id in self.event_token_to_triggered_boxes[event_token]:
                    self.event_token_to_triggered_boxes[event_token].remove(box_id)

    def box_ids_for_token(self, event_token: str) -> typing.Set[str]:
        with self.lock:
            if event_token in self.event_token_to_triggered_boxes:
                return self.event_token_to_triggered_boxes[event_token]



class MakaiDataSubscriber(threading.Thread):
    """
    This class handles receiving triggered data back from Makai. This class is ran in a separate thread.
    """

    # pylint: disable=E1101
    def __init__(self,
                 zmq_data_interface: str,
                 zmq_producer_interface: str,
                 trigger_records: TriggerRecords,
                 logger: logging.Logger,
                 opq_mongo_client: typing.Optional[mongo.OpqMongoClient] = None):
        super().__init__()
        self.zmq_context = zmq.Context()
        # noinspection PyUnresolvedReferences
        self.zmq_socket = self.zmq_context.socket(zmq.SUB)
        self.zmq_socket.setsockopt(zmq.SUBSCRIBE, "mauka_".encode())

        self.zmq_socket.connect(zmq_data_interface)
        # noinspection PyUnresolvedReferences
        # self.zmq_producer = self.zmq_context.socket(zmq.PUB)
        # self.zmq_producer.connect(zmq_producer_interface)
        self.trigger_records = trigger_records
        self.mongo_client = mongo.get_default_client(opq_mongo_client)

    def run(self):
        """
        Run loop which continuously attempts to receive triggered data from Makai.
        """
        logger.info("MakaiDataSubscriber thread started")
        while True:
            data = self.zmq_socket.recv_multipart()
            identity = data[0].decode()
            topic, event_token, box_id = identity.split("_")
            response = pb_util.deserialize_makai_response(data[1])
            box_id = str(response.box_id)
            cycles = list(map(pb_util.deserialize_makai_cycle, data[2:]))
            start_ts, end_ts = extract_timestamps(cycles)
            samples = cycles_to_data(cycles)
            event_id = self.trigger_records.event_id(event_token)

            # Update event
            mongo.update_event(event_id, box_id, self.mongo_client)
            self.trigger_records.remove_record(event_token)

            # Store box_event
            mongo.store_box_event(event_id,
                                  box_id,
                                  start_ts,
                                  end_ts,
                                  samples,
                                  self.mongo_client)

            # Cleanup
            self.trigger_records.remove_box_id(event_token, box_id)
            if len(self.trigger_records.box_ids_for_token(event_token)) == 0:
                self.trigger_records.remove_record(event_token)

            # Prune any old records that might still be hanging around
            self.trigger_records.prune()




def trigger_boxes(zmq_trigger_socket: zmq.Socket,
                  zmq_event_id_socket: zmq.Socket,
                  trigger_records: TriggerRecords,
                  start_timestamp_ms: int,
                  end_timestamp_ms: int,
                  box_ids: typing.List[str],
                  incident_id: int,
                  source: str,
                  logger: logging.Logger,
                  opq_mongo_client: typing.Optional[mongo.OpqMongoClient] = None) -> str:
    """
    This function triggers boxes through Makai.
    :param zmq_trigger_socket: Makai interface.
    :param start_timestamp_ms: Start of the requested data time window.
    :param end_timestamp_ms: End of the requested data time window.
    :param box_ids: A list of box ids to trigger.
    :param incident_id: The associated incident id.
    :param source: The source of the trigger (generally a plugin).
    :param logger: The logger from the base plugin.
    :return: The event token.
    """
    event_token = str(uuid.uuid4())
    trigger_commands = pb_util.build_makai_trigger_commands(start_timestamp_ms,
                                                            end_timestamp_ms,
                                                            box_ids,
                                                            event_token)

    mongo_client = mongo.get_default_client(opq_mongo_client)
    event_id = next_event_id(zmq_event_id_socket)

    # Update trigger records
    trigger_records.insert_record(event_token,
                                  event_id,
                                  0,
                                  set(box_ids))

    # Create a new event
    mongo.store_event(event_id,
                      "Mauka %s" % event_token,
                      box_ids,
                      start_timestamp_ms,
                      end_timestamp_ms,
                      mongo_client)

    # Trigger the boxes
    for trigger_command in trigger_commands:
        try:
            zmq_trigger_socket.send(pb_util.serialize_message(trigger_command))
        except Exception as exception:  # pylint: disable=W0703
            logger.error(str(exception))

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
        # Setup ZMQ
        self.zmq_trigger_interface: str = conf.get("zmq.trigger.interface")
        self.zmq_data_interface: str = conf.get("zmq.data.interface")
        self.zmq_producer_interface: str = conf.get("zmq.mauka.plugin.pub.interface")
        self.zmq_event_id_interface: str = conf.get("zmq.event_id.interface")
        zmq_context = zmq.Context()
        # pylint: disable=E1101
        # noinspection PyUnresolvedReferences
        self.zmq_trigger_socket = zmq_context.socket(zmq.PUSH)
        self.zmq_trigger_socket.connect(self.zmq_trigger_interface)
        # pylint: disable=E1101
        # noinspection PyUnresolvedReferences
        self.zmq_event_id_socket = zmq_context.socket(zmq.REQ)
        self.zmq_event_id_socket.connect(self.zmq_event_id_interface)
        self.trigger_records = TriggerRecords()



        # Start MakaiDataSubscriber thread
        makai_data_subscriber = MakaiDataSubscriber(self.zmq_data_interface,
                                                    self.zmq_producer_interface,
                                                    self.trigger_records,
                                                    self.logger)
        makai_data_subscriber.start()

    def on_message(self, topic: str, mauka_message: pb_util.mauka_pb2.MaukaMessage):
        """Subscribed messages occur async

        Messages are printed to stdout

        :param topic: The topic that this message is associated with
        :param mauka_message: The message
        """
        if pb_util.is_trigger_request(mauka_message):
            self.debug("Recv trigger request %s" % str(mauka_message))
            trigger_boxes(self.zmq_trigger_socket,
                          self.zmq_event_id_socket,
                          self.trigger_records,
                          mauka_message.trigger_request.start_timestamp_ms,
                          mauka_message.trigger_request.end_timestamp_ms,
                          mauka_message.trigger_request.box_ids[:],
                          mauka_message.trigger_request.incident_id,
                          mauka_message.source,
                          self.logger,
                          self.mongo_client)
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

    zmq_event_id_socket = zmq_context.socket(zmq.REQ)
    zmq_event_id_socket.connect(event_id_interface)

    zmq_event_id_socket.send_string("")

    print(zmq_event_id_socket.recv_string())

    # makai_data_subscriber = MakaiDataSubscriber(data_interface,
    #                                             None,
    #                                             logger)
    # makai_data_subscriber.start()
    #
    # end = timestamp_ms() - 2_000
    # start = end - 10_000
    #
    # trigger_boxes(zmq_trigger_socket,
    #               start,
    #               end,
    #               ["1001"],
    #               0,
    #               "test",
    #               logger)
