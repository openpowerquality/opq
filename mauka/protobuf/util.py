import time

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


def build_heartbeat(source: str,
                    last_received_timestamp_ms: int,
                    on_message_count: int,
                    status: str) -> mauka_pb2.MaukaMessage:
    mauka_message = build_mauka_message(source)
    mauka_message.heartbeat.last_received_timestamp_ms = last_received_timestamp_ms
    mauka_message.heartbeat.on_message_count = on_message_count
    mauka_message.heartbeat.status = status

    return mauka_message


def serialize_mauka_message(mauka_message: mauka_pb2.MaukaMessage) -> bytes:
    return mauka_message.SerializeToString()


def deserialize_mauka_message(mauka_message_bytes: bytes) -> mauka_pb2.MaukaMessage:
    mauka_message = mauka_pb2.MaukaMessage()
    mauka_message.ParseFromString(mauka_message_bytes)
    return mauka_message


def which_message_oneof(mauka_message: mauka_pb2.MaukaMessage) -> str:
    return mauka_message.WhichOneof("message")


def is_heartbeat_message(mauka_message: mauka_pb2.MaukaMessage) -> bool:
    return which_message_oneof(mauka_message) == "heartbeat"


if __name__ == "__main__":
    heartbeat = build_heartbeat("test_source", 10, 100, "test status")
    print(heartbeat)
    serialized = serialize_mauka_message(heartbeat)
    print(serialized)
    deserialized = deserialize_mauka_message(serialized)
    print(deserialized)
    print(which_message_oneof(deserialized))
