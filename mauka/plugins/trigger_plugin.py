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


def produce_makai_event_id(pub_socket: zmq.Socket, event_id: int):
    makai_event = pb_util.build_makai_event("TriggerPlugin", event_id)
    serialized_makai_event = pb_util.serialize_message(makai_event)
    pub_socket.send_multipart(("MakaiEvent".encode(), serialized_makai_event))

def next_event_id(event_id_socket: zmq.Socket) -> int:
    """
    Atomically returns the next event_id by requesting the event_id from Makai's EventIdService.
    :param event_id_socket: Makai's EventIdServiceBroker
    :return: The next available event_id.
    """
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
    """
    This class provides a thread safe mapping between an event_token and all of event_id, incident_id, timestamp_ms,
    and triggered Boxes. When records are inserted, they are inserted with a timestamp so that old records for Boxes we
    may not have received from can be garbage collected. Records are garbage collected after ten minutes.
    """

    def __init__(self):
        self.event_token_to_event_id: typing.Dict[str, int] = {}
        self.event_token_to_incident_id: typing.Dict[str, int] = {}
        self.event_token_to_timestamp_ms: typing.Dict[str, int] = {}
        self.event_token_to_triggered_boxes: typing.Dict[str, typing.Set[str]] = {}
        self.lock = multiprocessing.Lock()

    def __insert_record(self,
                        event_token: str,
                        event_id: int,
                        incident_id: int,
                        box_ids: typing.Set[str]):
        """
        Inserts a new record. This method is NOT thread safe.
        :param event_token: The event token.
        :param event_id: The event id.
        :param incident_id: The incident id.
        :param box_ids: The box ids.
        """
        self.event_token_to_event_id[event_token] = event_id
        self.event_token_to_incident_id[event_token] = incident_id
        self.event_token_to_timestamp_ms[event_token] = timestamp_ms()
        self.event_token_to_triggered_boxes[event_token] = box_ids

    def insert_record(self,
                      event_token: str,
                      event_id: int,
                      incident_id: int,
                      box_ids: typing.Set[str]):
        """
        Inserts a new record. Thread-safe wrapper around __insert_record.
        :param event_token: The event token.
        :param event_id: The event id.
        :param incident_id: The incident id.
        :param box_ids: The box ids.
        """
        with self.lock:
            self.__insert_record(event_token, event_id, incident_id, box_ids)

    def __remove_record(self, event_token: str):
        """
        Removes a record attached to an event token. This method is NOT thread safe.
        :param event_token: The event token.
        """
        if event_token in self.event_token_to_event_id:
            del self.event_token_to_event_id[event_token]

        if event_token in self.event_token_to_event_id:
            del self.event_token_to_incident_id[event_token]

        if event_token in self.event_token_to_event_id:
            del self.event_token_to_timestamp_ms[event_token]

        if event_token in self.event_token_to_triggered_boxes:
            del self.event_token_to_triggered_boxes[event_token]

    def remove_record(self, event_token: str):
        """
        Removes a record attached to an event token. This is a thread-safe wrapper around __remove_record.
        :param event_token: The event token.
        """
        with self.lock:
            self.__remove_record(event_token)

    def __prune(self) -> typing.List[int]:
        """
        Garbage collects records where Boxes were not received in over 10 minutes. This method is NOT thread safe.
        :return: A list of pruned event_ids.
        """
        pruned_event_ids = []
        now = timestamp_ms()
        for event_token, ts_ms in self.event_token_to_timestamp_ms.items():
            if now - ts_ms > 1_000 * 60 * 10:  # 10 minutes
                pruned_event_ids.append(self.event_token_to_event_id[event_token])
                self.__remove_record(event_token)
        return pruned_event_ids

    def prune(self) -> typing.List[int]:
        """
        Garbage collects records where Boxes were not received in over 10 minutes. Thread-safe wrapper around __prune.
        :return: A list of pruned event_ids.
        """
        with self.lock:
            return self.__prune()

    def event_id(self, event_token: str) -> int:
        """
        Returns the event_id associated with an event_token. This method is thread safe.
        :param event_token: The event token.
        :return: The event_id associated with the event_token.
        """
        with self.lock:
            if event_token in self.event_token_to_event_id:
                return self.event_token_to_event_id[event_token]

    def remove_box_id(self, event_token: str, box_id: str):
        """
        Removes a triggered_box id from the record once that box has been received. This method is thread safe.
        :param event_token:
        :param box_id:
        :return:
        """
        with self.lock:
            if event_token in self.event_token_to_triggered_boxes:
                if box_id in self.event_token_to_triggered_boxes[event_token]:
                    self.event_token_to_triggered_boxes[event_token].remove(box_id)

    def box_ids_for_token(self, event_token: str) -> typing.Set[str]:
        """
        Returns the remaining box_ids for a given token. This method is thread safe.
        :param event_token: The event_token.
        :return: Remaining box_ids associated with this token.
        """
        with self.lock:
            if event_token in self.event_token_to_triggered_boxes:
                return self.event_token_to_triggered_boxes[event_token]
            else:
                return set()



class MakaiDataSubscriber(threading.Thread):
    """
    This class handles receiving triggered data back from Makai. This class is ran in a separate thread.
    """

    # pylint: disable=E1101
    # noinspection PyUnresolvedReferences
    def __init__(self,
                 zmq_data_interface: str,
                 zmq_producer_interface: str,
                 trigger_records: TriggerRecords,
                 logger: logging.Logger,
                 opq_mongo_client: typing.Optional[mongo.OpqMongoClient] = None):

        super().__init__()

        # ZMQ
        self.zmq_context = zmq.Context()
        self.zmq_socket = self.zmq_context.socket(zmq.SUB)
        self.zmq_socket.setsockopt(zmq.SUBSCRIBE, "mauka_".encode())
        self.zmq_socket.connect(zmq_data_interface)
        self.zmq_producer = self.zmq_context.socket(zmq.PUB)
        self.zmq_producer.connect(zmq_producer_interface)

        # MongoDB client
        self.mongo_client = mongo.get_default_client(opq_mongo_client)

        # Thead-safe trigger records
        self.trigger_records = trigger_records

        # Logging
        self.logger = logger

    def run(self):
        """
        Run loop which continuously attempts to receive triggered data from Makai.
        """
        self.logger.info("MakaiDataSubscriber thread started")
        while True:
            # Receive data and extract parameters
            data = self.zmq_socket.recv_multipart()
            identity = data[0].decode()
            topic, event_token, box_id = identity.split("_")
            response = pb_util.deserialize_makai_response(data[1])
            box_id = str(response.box_id)
            cycles = list(map(pb_util.deserialize_makai_cycle, data[2:]))
            start_ts, end_ts = extract_timestamps(cycles)
            samples = cycles_to_data(cycles)
            event_id = self.trigger_records.event_id(event_token)

            self.logger.debug("Recv data with event_token %s, event_id %d, and box_id %s", event_token, event_id, box_id)

            # Update event
            mongo.update_event(event_id, box_id, self.mongo_client)
            self.trigger_records.remove_record(event_token)
            self.logger.debug("Event with event_id %d updated", event_id)

            # Store box_event
            mongo.store_box_event(event_id,
                                  box_id,
                                  start_ts,
                                  end_ts,
                                  samples,
                                  self.mongo_client)
            self.logger.debug("box_event stored for event_id %d and box_id %s", event_id, box_id)

            # Cleanup
            self.trigger_records.remove_box_id(event_token, box_id)
            self.logger.debug("Removed box_id from record with event_token %s and box_id %s", event_token, box_id)

            # If this was the last box we were waiting on, we can not produce an event_id to MakaiEventPlugin for
            # analysis. We'll also remove the record since we're not longer waiting on any boxes.
            if len(self.trigger_records.box_ids_for_token(event_token)) == 0:
                produce_makai_event_id(self.zmq_producer, event_id)
                self.logger.debug("Removing record for event_token %s", event_token)
                self.trigger_records.remove_record(event_token)

            # Prune any old records that might still be hanging around
            # This occurs when we never received data from a triggered box.
            # We should produce an event message to ensure we process any other boxes we might have recieved from.
            pruned_event_ids = self.trigger_records.prune()
            for pruned_event_id in pruned_event_ids:
                produce_makai_event_id(self.zmq_producer, pruned_event_id)



def trigger_boxes(zmq_trigger_socket: zmq.Socket,
                  zmq_event_id_socket: zmq.Socket,
                  trigger_records: TriggerRecords,
                  start_timestamp_ms: int,
                  end_timestamp_ms: int,
                  box_ids: typing.List[str],
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

    logger.debug("%d trigger commands built.", len(trigger_commands))

    mongo_client = mongo.get_default_client(opq_mongo_client)
    event_id = next_event_id(zmq_event_id_socket)

    # Update trigger records
    trigger_records.insert_record(event_token,
                                  event_id,
                                  0,
                                  set(box_ids))

    logger.debug("Trigger record inserted for event_token %s and event_id %d", event_token, event_id)

    # Create a new event
    mongo.store_event(event_id,
                      "Mauka %s" % event_token,
                      box_ids,
                      start_timestamp_ms,
                      end_timestamp_ms,
                      mongo_client)

    logger.debug("MongoDB event created with event_id %d", event_id)

    # Trigger the boxes
    for trigger_command in trigger_commands:
        try:
            zmq_trigger_socket.send(pb_util.serialize_message(trigger_command))
        except Exception as exception:  # pylint: disable=W0703
            logger.error(str(exception))

    logger.debug("%d boxes triggered", len(box_ids))

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
                          self.logger,
                          self.mongo_client)
        else:
            self.logger.error("Received incorrect type of MaukaMessage :%s", str(mauka_message))


# if __name__ == "__main__":
#
#
    # import logging
    #
    # logger = logging.getLogger()
    # logger.setLevel(logging.DEBUG)
    #
    # logger.info("Starting test")
    #
    # trigger_interface = "tcp://127.0.0.1:9884"
    # data_interface = "tcp://127.0.0.1:9899"
    # event_id_interface = "tcp://127.0.0.1:10001"
    #
    # zmq_context = zmq.Context()
    #
    # zmq_trigger_socket = zmq_context.socket(zmq.PUSH)
    # zmq_trigger_socket.connect(trigger_interface)
    #
    # zmq_event_id_socket = zmq_context.socket(zmq.REQ)
    # zmq_event_id_socket.connect(event_id_interface)
    #
    # trigger_records = TriggerRecords()
    #
    # end_ts = timestamp_ms() - 2000
    # start_ts = end_ts - 7000
    #
    # makai_data_subscripter = MakaiDataSubscriber(data_interface,
    #                                              "",
    #                                              trigger_records,
    #                                              logger,
    #                                              None)
    #
    # makai_data_subscripter.start()
    #
    # event_token = trigger_boxes(zmq_trigger_socket,
    #                             zmq_event_id_socket,
    #                             trigger_records,
    #                             start_ts,
    #                             end_ts,
    #                             ["1001"],
    #                             logger,
    #                             None)
    #
    # logger.debug("event_token from triggered boxes %s", event_token)
