import mongo.mongo
import plugins.base

import protobuf.opq_pb2
import zmq

import time

from typing import List


def run_plugin(config):
    plugins.base.run_plugin(AcquisitionTriggerPlugin, config)


class AcquisitionTriggerPlugin(plugins.base.MaukaPlugin):
    def __init__(self, config):
        super().__init__(config, ["VoltageEvent", "FrequencyEvent"], "AcquisitionTriggerPlugin")
        self.zmq_req_ctx = zmq.Context()
        self.req_socket = self.zmq_req_ctx.socket(zmq.REQ)
        self.req_socket.connect(self.config_get("zmq.makai.req.interface"))
        self.msBefore = self.config_get("plugins.AcquisitionTriggerPlugin.msBefore")
        self.msAfter = self.config_get("plugins.AcquisitionTriggerPlugin.msAfter")
        self.sDeadZone = self.config_get("plugins.AcquisitionTriggerPlugin.sDeadZoneAfterTrigger")

        self.event_type_to_last_event = {}

    def request_event_message(self, start_ms: int, end_ms: int, trigger_type: str, percent_magnitude: float,
                              box_ids: List[int], requestee: str, description: str, request_data: bool):
        msg = protobuf.opq_pb2.RequestEventMessage()
        msg.start_timestamp_ms_utc = start_ms - self.msBefore
        msg.end_timestamp_ms_utc = end_ms + self.msAfter
        msg.trigger_type = protobuf.opq_pb2.RequestEventMessage.TriggerType.Value(trigger_type)
        msg.percent_magnitude = percent_magnitude
        msg.box_ids.extend(box_ids)
        msg.requestee = requestee
        msg.description = description
        msg.request_data = request_data
        return msg.SerializeToString()

    def is_deadzone(self, event_type, now):
        if event_type in self.event_type_to_last_event:
            return now - self.event_type_to_last_event[event_type] <= self.sDeadZone
        else:
            return False

    def on_message(self, topic, message):
        msg = self.from_json(message.decode())
        print(topic, msg)
        event_id = msg["eventId"]
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
