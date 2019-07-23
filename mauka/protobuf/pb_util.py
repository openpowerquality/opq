"""
Utility methods for interacting with protobuf messages from Makai and/or Mauka.
"""

import time
import typing

import numpy

import log
import protobuf.mauka_pb2 as mauka_pb2
import protobuf.opqbox3_pb2 as opqbox3_pb2

LAHA = "laha"
LAHA_TYPE = "laha_type"
LAHA_ONEOF_TTL = "ttl"
LAHA_ONEOF_GC_TRIGGER = "gc_trigger"
LAHA_ONEOF_GC_UPDATE = "gc_update"
LAHA_ONEOF_GC_STAT = "gc_stat"
TRIGGER_REQUEST = "trigger_request"

# pylint: disable=C0103
logger = log.get_logger(__name__)


def get_timestamp_ms() -> int:
    """
    Returns the current time as a timestamp as the number of milliseconds since the epoch.
    :return: The number of milliseconds since the epoch.
    """
    return int(round(time.time() * 1000))


def build_mauka_message(source: str,
                        timestamp_ms: int = get_timestamp_ms()) -> mauka_pb2.MaukaMessage:
    """
    Instantiates a MaukaMessage.
    :param source: Where this message is created from (plugin name or service name)
    :param timestamp_ms: When this message was created (ms since epoch)
    :return: Insantiated MaukaMessage
    """
    mauka_message = mauka_pb2.MaukaMessage()
    mauka_message.source = source
    mauka_message.timestamp_ms = timestamp_ms
    return mauka_message


# pylint: disable=E1101
def build_payload(source: str,
                  event_id: int,
                  box_id: str,
                  payload_type: mauka_pb2.PayloadType,
                  data: typing.Union[numpy.ndarray, typing.List],
                  start_timestamp_ms: int,
                  end_timestamp_ms: int) -> mauka_pb2.MaukaMessage:
    """
    Builds an instance of a MaukaMessage with message type Payload
    :param source: Where this message is created from (plugin name or service name)
    :param event_id: Event_id this payload is associated with
    :param box_id: Box id this payload is associated with
    :param payload_type: The type of payload that this represents (see PayloadType of mauka.proto)
    :param data: Payload data cast to float64's
    :param start_timestamp_ms: Start timestamp of this payload
    :param end_timestamp_ms: End timestamp of this payload
    :return: Instance of MaukaMessage Payload
    """
    mauka_message = build_mauka_message(source)
    mauka_message.payload.event_id = event_id
    mauka_message.payload.box_id = box_id
    mauka_message.payload.payload_type = payload_type
    mauka_message.payload.data.extend(data)
    mauka_message.payload.start_timestamp_ms = start_timestamp_ms
    mauka_message.payload.end_timestamp_ms = end_timestamp_ms
    return mauka_message


# pylint: disable=E1101
def build_heartbeat(source: str,
                    last_received_timestamp_ms: int,
                    on_message_count: int,
                    status: str) -> mauka_pb2.MaukaMessage:
    """
    Instance of Heartbeat protobuf message
    :param source: Where this message is created from (plugin name or service name)
    :param last_received_timestamp_ms: Last time a plugin received a on_message
    :param on_message_count: Number of times a plugin's on_message has been fired
    :param status: Custom status message
    :return: Insantiated MaukaMessage with message type heartbeat
    """
    mauka_message = build_mauka_message(source)
    mauka_message.heartbeat.last_received_timestamp_ms = last_received_timestamp_ms
    mauka_message.heartbeat.on_message_count = on_message_count
    mauka_message.heartbeat.status = status

    return mauka_message


# pylint: disable=E1101
def build_makai_event(source: str, event_id: int) -> mauka_pb2.MaukaMessage:
    """
    Instance of a MakaiEvent that gets injected into the Mauka system by a service broker.
    :param source: Where this message is created from (plugin name or service name)
    :param event_id:
    :return:
    """
    mauka_message = build_mauka_message(source)
    mauka_message.makai_event.event_id = event_id
    return mauka_message


# pylint: disable=E1101
def build_makai_trigger(source: str,
                        event_start_timestamp_ms: int,
                        event_end_timestamp_ms: int,
                        event_type: str,
                        max_value: float,
                        box_id: str) -> mauka_pb2.MaukaMessage:
    """
    Instantiates a makai trigger message.
    :param source: Where this message is created from (plugin name or service name)
    :param event_start_timestamp_ms: Start time of makai trigger
    :param event_end_timestamp_ms: End time of makai trigger
    :param event_type: Type of event that causes this trigger
    :param max_value: Max deviation from nominal
    :param box_id: Box id that caused this trigger message to be created
    :return: Instantiated MaukaMessage with a message type of makai trigger
    """
    mauka_message = build_mauka_message(source)
    mauka_message.makai_trigger.event_start_timestamp_ms = event_start_timestamp_ms
    mauka_message.makai_trigger.event_end_timestamp_ms = event_end_timestamp_ms
    mauka_message.makai_trigger.event_type = event_type
    mauka_message.makai_trigger.max_value = max_value
    mauka_message.makai_trigger.box_id = box_id
    return mauka_message


# pylint: disable=E1101
def build_measurement(source: str,
                      box_id: str,
                      timestamp_ms: int,
                      frequency: float,
                      voltage_rms: float,
                      thd: float) -> mauka_pb2.MaukaMessage:
    """
    Instantiates a protobuf mauka measurement.
    :param source: Where this message is created from (plugin name or service name)
    :param box_id: Id of the box that created this measurement
    :param timestamp_ms: Timestamp that this measurement was created
    :param frequency: Frequency value when this measurement was recorded
    :param voltage_rms: Voltage value when this measurement was recorded
    :param thd: THD value when this measurement was recorded
    :return: Instance of MaukaMessage with message type of measurement.
    """
    mauka_message = build_mauka_message(source)
    mauka_message.measurement.box_id = box_id
    mauka_message.measurement.timestamp_ms = timestamp_ms
    mauka_message.measurement.frequency = frequency
    mauka_message.measurement.voltage_rms = voltage_rms
    mauka_message.measurement.thd = thd
    return mauka_message


def build_ttl(source: str,
              collection: str,
              ttl_s: int) -> mauka_pb2.MaukaMessage:
    """
    Builds a TTL message.
    :param source: The source of this message.
    :param collection: The collection to modify the TTL of.
    :param ttl_s: The TTL in seconds.
    :return: The MaukaMessage.
    """
    mauka_message = build_mauka_message(source)
    mauka_message.laha.ttl.collection = collection
    mauka_message.laha.ttl.ttl_s = ttl_s
    return mauka_message


def build_gc_trigger(source: str,
                     gc_domains: typing.List) -> mauka_pb2.MaukaMessage:
    """
    Builds a gc_trigger message.
    :param source: Where this message was created.
    :param gc_domains: List of GC domains to trigger.
    :return: A GcTrigger message.
    """
    mauka_message = build_mauka_message(source)
    mauka_message.laha.gc_trigger.gc_domains[:] = gc_domains
    return mauka_message


def build_gc_update(source: str,
                    from_domain: mauka_pb2.GcDomain,
                    _id: int) -> mauka_pb2.MaukaMessage:
    """
    Builds a gc_update message.
    :param source: Where this message was created.
    :param from_domain: The GC domain creating this update.
    :param _id: The _id of the document creating this update.
    :return: A GcUpdate message.
    """
    mauka_message = build_mauka_message(source)
    mauka_message.laha.gc_update.from_domain = from_domain
    mauka_message.laha.gc_update.id = int(_id) if isinstance(_id, str) else _id
    return mauka_message


def build_gc_stat(source: str,
                  gc_domain: mauka_pb2.GcDomain,
                  gc_cnt: int) -> mauka_pb2.MaukaMessage:
    """
    Builds a GcStat message.
    :param source: Where this message was created.
    :param gc_domain: The GC domain items were GC from.
    :param gc_cnt: The count of items GCed.
    :return: GcStat message.
    """
    mauka_message = build_mauka_message(source)
    mauka_message.laha.gc_stat.gc_domain = gc_domain
    mauka_message.laha.gc_stat.gc_cnt = gc_cnt
    return mauka_message


def build_trigger_request(source: str,
                          start_timestamp_ms: int,
                          end_timestamp_ms: int,
                          box_ids: typing.List[str],
                          incident_id: int) -> mauka_pb2.MaukaMessage:
    mauka_message = build_mauka_message(source)
    mauka_message.trigger_request.start_timestamp_ms = start_timestamp_ms
    mauka_message.trigger_request.end_timestamp_ms = end_timestamp_ms
    mauka_message.trigger_request.box_ids[:] = box_ids
    mauka_message.trigger_request.incident_id = incident_id
    return mauka_message


def format_makai_triggering_identity(event_token: str, uuid: str) -> str:
    return "data_%s_%s" % (event_token, uuid)


def build_makai_trigger_commands(start_timestamp_ms,
                                 end_timestamp_ms,
                                 box_ids: typing.List[str],
                                 event_token: str,
                                 uuid: str) -> typing.List[opqbox3_pb2.Command]:
    identity = format_makai_triggering_identity(event_token, uuid)

    def _make_command(box_id: str) -> opqbox3_pb2.Command:
        command = opqbox3_pb2.Command()
        command.box_id = int(box_id)
        command.timestamp_ms = get_timestamp_ms()
        command.identity = identity
        command.data_command.start_ms = start_timestamp_ms
        command.data_command.end_ms = end_timestamp_ms
        command.data_command.wait = False
        return command

    return list(map(_make_command, box_ids))


def serialize_message(message: typing.Union[mauka_pb2.MaukaMessage, opqbox3_pb2.Command]) -> bytes:
    """
    Serializes an instance of a protobuf into bytes.
    :param message: The protobuf to serialize.
    :return: Serialized bytes.
    """
    return message.SerializeToString()


def deserialize_mauka_message(mauka_message_bytes: bytes) -> mauka_pb2.MaukaMessage:
    """
    Deserialized a mauka message from bytes to an instance of MaukaMessage.
    :param mauka_message_bytes: Serialized bytes
    :return: An instance of MaukaMessage
    """
    mauka_message = mauka_pb2.MaukaMessage()
    mauka_message.ParseFromString(mauka_message_bytes)
    return mauka_message


def which_message_oneof(mauka_message: mauka_pb2.MaukaMessage) -> str:
    """
    Returns the one_of field type of the message field in the mauka_message.
    :param mauka_message: Mauka message to inspect.
    :return: The message type assigned in the one_of.
    """
    return mauka_message.WhichOneof("message")


def is_payload(mauka_message: mauka_pb2.MaukaMessage, payload_type: mauka_pb2.PayloadType = None) -> bool:
    """
    Determine if message type is payload and optionally checks payload type if provided.
    :param mauka_message: Mauka message to check the message type of.
    :param payload_type: The type of payload to check against.
    :return: True if the message and payload type match, false otherwise.
    """
    if payload_type is None:
        return which_message_oneof(mauka_message) == "payload"

    return which_message_oneof(mauka_message) == "payload" and mauka_message.payload.payload_type == payload_type


def is_heartbeat_message(mauka_message: mauka_pb2.MaukaMessage) -> bool:
    """
    Determine if message type is a heartbeat
    :param mauka_message: Mauka message to check the message type of.
    :return: True if this is a heartbeat type, fasle otherwise
    """
    result = which_message_oneof(mauka_message) == "heartbeat"
    return result


def is_makai_event_message(mauka_message: mauka_pb2.MaukaMessage) -> bool:
    """
    Determine if message type is a makai_event
    :param mauka_message: Mauka message to check the message type of.
    :return: True if this is a makai_event type, fasle otherwise
    """
    return which_message_oneof(mauka_message) == "makai_event"


def is_makai_trigger(mauka_message: mauka_pb2.MaukaMessage) -> bool:
    """
    Determine if message type is a makai_trigger
    :param mauka_message: Mauka message to check the message type of.
    :return: True if this is a makai_trigger type, fasle otherwise
    """
    return which_message_oneof(mauka_message) == "makai_trigger"


def is_measurement(mauka_message: mauka_pb2.MaukaMessage) -> bool:
    """
    Determine if message type is a measurement
    :param mauka_message: Mauka message to check the message type of.
    :return: True if this is a measurement type, fasle otherwise
    """
    return which_message_oneof(mauka_message) == "measurement"


def is_laha(mauka_message: mauka_pb2.MaukaMessage) -> bool:
    """
    Returns whether this message is a LahaConfig message or not.
    :param mauka_message: Message to test.
    :return: True if this is a Laga Config message, False otherwise.
    """
    return which_message_oneof(mauka_message) == LAHA


def is_ttl(mauka_message: mauka_pb2.MaukaMessage) -> bool:
    """
    Returns whether this message is a TTL message or not.
    :param mauka_message: Message to test.
    :return: True if this is a TTL message, False otherwise.
    """
    return is_laha(mauka_message) and mauka_message.laha.WhichOneof(LAHA_TYPE) == LAHA_ONEOF_TTL


def is_gc_trigger(mauka_message: mauka_pb2.MaukaMessage) -> bool:
    """
    Tests if the provided mauka_message is a GcTrigger message.
    :param mauka_message: Message to test.
    :return: True if it is, False otherwise.
    """
    return is_laha(mauka_message) and mauka_message.laha.WhichOneof(LAHA_TYPE) == LAHA_ONEOF_GC_TRIGGER


def is_gc_update(mauka_message: mauka_pb2.MaukaMessage) -> bool:
    """
    Tests if the provided mauka_message is a GcUpdate message.
    :param mauka_message: Message to test.
    :return: True if it is, False otherwise.
    """
    return is_laha(mauka_message) and mauka_message.laha.WhichOneof(LAHA_TYPE) == LAHA_ONEOF_GC_UPDATE


def is_gc_stat(mauka_message: mauka_pb2.MaukaMessage) -> bool:
    """
    Tests if the provided mauka_message is a GcStat message.
    :param mauka_message: Message to test.
    :return: True if it is, False otherwise.
    """
    return is_laha(mauka_message) and mauka_message.laha.WhichOneof(LAHA_TYPE) == LAHA_ONEOF_GC_STAT


def is_trigger_request(mauka_message: mauka_pb2.MaukaMessage) -> bool:
    return which_message_oneof(mauka_message) == TRIGGER_REQUEST


def repeated_as_ndarray(repeated) -> numpy.ndarray:
    """
    Converts a protobuf repeated field to a numpy array.
    :param repeated: Protobuf repeated field
    :return: Numpy array
    """
    return numpy.array(repeated)
