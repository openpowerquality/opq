"""
This module provides the acquisition trigger plugin whose job it is to look at interesting events and query for
raw data when interesting events occur.
"""

import multiprocessing
import time
import typing

import zmq

import plugins.base
import protobuf.opq_pb2


class AcquisitionTriggerPlugin(plugins.base.MaukaPlugin):
    """
    This class provides the acquisition trigger plugin whose job it is to look at interesting events and query for
    raw data when interesting events occur

    This class subscribes to voltage and frequency event topics
    """

    NAME = "AcquisitionTriggerPlugin"

    def __init__(self, config: typing.Dict, exit_event: multiprocessing.Event):
        """ Initializes this plugin

        :param config: Configuration dictionary
        """
        super().__init__(config, ["VoltageEvent", "FrequencyEvent"], AcquisitionTriggerPlugin.NAME, exit_event)

        self.zmq_req_ctx = zmq.Context()
        """ZeroMQ context"""

        self.req_socket = self.zmq_req_ctx.socket(zmq.REQ)
        """ZeroMQ request socket"""

        self.ms_before = int(self.config_get("plugins.AcquisitionTriggerPlugin.msBefore"))
        """Number of ms before an event that we should also request data"""

        self.ms_after = int(self.config_get("plugins.AcquisitionTriggerPlugin.msAfter"))
        """Number of ms after an event that we should also request data"""

        self.s_dead_zone = int(self.config_get("plugins.AcquisitionTriggerPlugin.sDeadZoneAfterTrigger"))
        """Number of seconds of deadzone that we should not request raw data after just requesting data"""

        self.event_type_to_last_event = {}
        """Store event types to the last event of that type"""

        self.req_socket.connect(self.config_get("zmq.makai.req.interface"))

    def request_event_message(self, start_ms: int, end_ms: int, trigger_type: str, percent_magnitude: float,
                              box_ids: typing.List[int], requestee: str, description: str, request_data: bool):
        """ Creates a new protobuf serialized event request message

        :param start_ms: Start time in ms since the epoch
        :param end_ms: End time in ms since the epoch
        :param trigger_type: Why are we requesting data
        :param percent_magnitude: The percentage of the power value from steady state
        :param box_ids: List of box ids included in event
        :param requestee: The plugin or analysis that is requesting data
        :param description: Human description filled in by plugin
        :param request_data: Whether or not data should actually be requested
        :return: A serialized event message
        """
        msg = protobuf.opq_pb2.RequestEventMessage()
        msg.start_timestamp_ms_utc = start_ms - self.ms_before
        msg.end_timestamp_ms_utc = end_ms + self.ms_after
        msg.trigger_type = trigger_type
        msg.percent_magnitude = percent_magnitude
        msg.box_ids.extend(box_ids)
        msg.requestee = requestee
        msg.description = description
        msg.request_data = request_data
        return msg.SerializeToString()

    def is_deadzone(self, event_type, now) -> bool:
        """Determines if we are currently in a deadzone

        :param event_type: The current event type
        :param now: The current time
        :return: If we are currently in a deadzone or not
        """
        if event_type in self.event_type_to_last_event:
            return now - self.event_type_to_last_event[event_type] <= self.s_dead_zone
        else:
            return False

    def on_message(self, topic, message):
        """Subscribed messages appear here

        :param topic: The topic that this message is associated with
        :param message: The message
        """
        msg = self.from_json(message.decode())
        print(topic, msg)
        event_type = msg["eventType"]

        now = time.time()
        if self.is_deadzone(event_type, now):
            request_data = False
        else:
            request_data = True
            self.event_type_to_last_event[event_type] = now

        start_ts_ms_utc = msg["eventStart"]
        end_ts_ms_utc = msg["eventEnd"]
        trigger_type = protobuf.opq_pb2.RequestEventMessage.TriggerType.Value(event_type)
        percent_magnitude = msg["percent"]
        device_ids = list(map(int, [msg["deviceId"]]))
        requestee = "AcquisitionTriggerPlugin"
        description = "{} {}-{}".format(str(trigger_type), start_ts_ms_utc, end_ts_ms_utc)

        event_msg = self.request_event_message(start_ts_ms_utc, end_ts_ms_utc, trigger_type, percent_magnitude,
                                               device_ids, requestee, description, request_data)
        self.req_socket.send(event_msg)
