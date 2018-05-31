import time
import typing

import numpy

import protobuf.mauka_pb2 as mauka_pb2
import protobuf.opq_pb2


def decode_trigger_message(encoded_trigger_message):
    """ Decodes and returns a serialized triggering message

    :param encoded_measurement: The protobuf encoded triggering message
    :return: The decoded TriggerMessage object
    """
    trigger_message = protobuf.opq_pb2.TriggerMessage()
    trigger_message.ParseFromString(encoded_trigger_message)
    return trigger_message


def encode_trigger_message(idd,
                           time,
                           frequency,
                           rms):
    trigger_message = protobuf.opq_pb2.TriggerMessage()
    trigger_message.id = idd
    trigger_message.time = time
    trigger_message.frequency = frequency
    trigger_message.rms = rms
    return trigger_message.SerializeToString()


def get_timestamp_ms() -> int:
    return int(round(time.time() * 1000))


def build_mauka_message(source: str,
                        timestamp_ms: int = get_timestamp_ms()) -> mauka_pb2.MaukaMessage:
    mauka_message = mauka_pb2.MaukaMessage()
    mauka_message.source = source
    mauka_message.timestamp_ms = timestamp_ms
    return mauka_message


def build_payload(source: str,
                  event_id: int,
                  box_id: str,
                  payload_type: mauka_pb2.PayloadType,
                  data: typing.Union[numpy.ndarray, typing.List]) -> mauka_pb2.MaukaMessage:
    mauka_message = build_mauka_message(source)
    mauka_message.payload.event_id = event_id
    mauka_message.payload.box_id = box_id
    mauka_message.payload.payload_type = payload_type
    mauka_message.payload.data.extend(data)
    return mauka_message


def build_heartbeat(source: str,
                    last_received_timestamp_ms: int,
                    on_message_count: int,
                    status: str) -> mauka_pb2.MaukaMessage:
    mauka_message = build_mauka_message(source)
    mauka_message.heartbeat.last_received_timestamp_ms = last_received_timestamp_ms
    mauka_message.heartbeat.on_message_count = on_message_count
    mauka_message.heartbeat.status = status

    return mauka_message


def build_makai_event(source: str, event_id: int) -> mauka_pb2.MaukaMessage:
    mauka_message = build_mauka_message(source)
    mauka_message.makai_event.event_id = event_id
    return mauka_message


def build_makai_trigger(source: str,
                        event_start_timestamp_ms: int,
                        event_end_timestamp_ms: int,
                        event_type: str,
                        max_value: float,
                        box_id: str) -> mauka_pb2.MaukaMessage:
    mauka_message = build_mauka_message(source)
    mauka_message.makai_trigger.event_start_timestamp_ms = event_start_timestamp_ms
    mauka_message.makai_trigger.event_end_timestamp_ms = event_end_timestamp_ms
    mauka_message.makai_trigger.event_type = event_type
    mauka_message.makai_trigger.max_value = max_value
    mauka_message.makai_trigger.box_id = box_id
    return mauka_message


def build_measurement(source: str,
                      box_id: str,
                      timestamp_ms: int,
                      frequency: float,
                      voltage_rms: float,
                      thd: float) -> mauka_pb2.MaukaMessage:
    mauka_message = build_mauka_message(source)
    mauka_message.measurement.box_id = box_id
    mauka_message.measurement.timestamp_ms = timestamp_ms
    mauka_message.measurement.frequency = frequency
    mauka_message.measurement.voltage_rms = voltage_rms
    mauka_message.measurement.thd = thd
    return mauka_message


def serialize_mauka_message(mauka_message: mauka_pb2.MaukaMessage) -> bytes:
    return mauka_message.SerializeToString()


def deserialize_mauka_message(mauka_message_bytes: bytes) -> mauka_pb2.MaukaMessage:
    mauka_message = mauka_pb2.MaukaMessage()
    mauka_message.ParseFromString(mauka_message_bytes)
    return mauka_message


def which_message_oneof(mauka_message: mauka_pb2.MaukaMessage) -> str:
    return mauka_message.WhichOneof("message")


def is_payload(mauka_message: mauka_pb2.MaukaMessage, payload_type: mauka_pb2.PayloadType = None) -> bool:
    if payload_type is None:
        return which_message_oneof(mauka_message) == "payload"
    else:
        return which_message_oneof(mauka_message) == "payload" and mauka_message.payload.payload_type == payload_type


def is_heartbeat_message(mauka_message: mauka_pb2.MaukaMessage) -> bool:
    return which_message_oneof(mauka_message) == "heartbeat"


def is_makai_event_message(mauka_message: mauka_pb2.MaukaMessage) -> bool:
    return which_message_oneof(mauka_message) == "makai_event"


def is_makai_trigger(mauka_message: mauka_pb2.MaukaMessage) -> bool:
    return which_message_oneof(mauka_message) == "makai_trigger"


def is_measurement(mauka_message: mauka_pb2.Measurement) -> bool:
    return which_message_oneof(mauka_message) == "measurement"


def repeated_as_ndarray(repeated) -> numpy.ndarray:
    # Maybe someone knows a better way to do this?
    return numpy.ndarray(list(repeated))


if __name__ == "__main__":
    mauka_message = build_payload("test_source",
                                  1,
                                  "2",
                                  mauka_pb2.VOLTAGE_RAW,
                                  numpy.array([1, 2, 3]))
    print(mauka_message)
