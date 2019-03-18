# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: mauka.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='mauka.proto',
  package='',
  syntax='proto3',
  serialized_pb=_b('\n\x0bmauka.proto\"\x92\x02\n\x0cMaukaMessage\x12\x14\n\x0ctimestamp_ms\x18\x01 \x01(\x04\x12\x0e\n\x06source\x18\x02 \x01(\t\x12\x1b\n\x07payload\x18\x03 \x01(\x0b\x32\x08.PayloadH\x00\x12\x1f\n\theartbeat\x18\x04 \x01(\x0b\x32\n.HeartbeatH\x00\x12\"\n\x0bmakai_event\x18\x05 \x01(\x0b\x32\x0b.MakaiEventH\x00\x12#\n\x0bmeasurement\x18\x06 \x01(\x0b\x32\x0c.MeasurementH\x00\x12&\n\rmakai_trigger\x18\x07 \x01(\x0b\x32\r.MakaiTriggerH\x00\x12\"\n\x0blaha_config\x18\x08 \x01(\x0b\x32\x0b.LahaConfigH\x00\x42\t\n\x07message\"\x93\x01\n\x07Payload\x12\x10\n\x08\x65vent_id\x18\x01 \x01(\r\x12\x0e\n\x06\x62ox_id\x18\x02 \x01(\t\x12\x0c\n\x04\x64\x61ta\x18\x03 \x03(\x01\x12\"\n\x0cpayload_type\x18\x04 \x01(\x0e\x32\x0c.PayloadType\x12\x1a\n\x12start_timestamp_ms\x18\x05 \x01(\x04\x12\x18\n\x10\x65nd_timestamp_ms\x18\x06 \x01(\x04\"Y\n\tHeartbeat\x12\"\n\x1alast_received_timestamp_ms\x18\x01 \x01(\x04\x12\x18\n\x10on_message_count\x18\x02 \x01(\r\x12\x0e\n\x06status\x18\x03 \x01(\t\"\x1e\n\nMakaiEvent\x12\x10\n\x08\x65vent_id\x18\x01 \x01(\r\"h\n\x0bMeasurement\x12\x0e\n\x06\x62ox_id\x18\x01 \x01(\t\x12\x14\n\x0ctimestamp_ms\x18\x02 \x01(\x04\x12\x11\n\tfrequency\x18\x03 \x01(\x01\x12\x13\n\x0bvoltage_rms\x18\x04 \x01(\x01\x12\x0b\n\x03thd\x18\x05 \x01(\x01\"\x87\x01\n\x0cMakaiTrigger\x12 \n\x18\x65vent_start_timestamp_ms\x18\x01 \x01(\x04\x12\x1e\n\x16\x65vent_end_timestamp_ms\x18\x02 \x01(\x04\x12\x12\n\nevent_type\x18\x03 \x01(\t\x12\x11\n\tmax_value\x18\x04 \x01(\x01\x12\x0e\n\x06\x62ox_id\x18\x05 \x01(\t\"0\n\nLahaConfig\x12\x13\n\x03ttl\x18\x01 \x01(\x0b\x32\x04.TtlH\x00\x42\r\n\x0blaha_config\"(\n\x03Ttl\x12\x12\n\ncollection\x18\x01 \x01(\t\x12\r\n\x05ttl_s\x18\x02 \x01(\r*r\n\x0bPayloadType\x12\x0f\n\x0b\x41\x44\x43_SAMPLES\x10\x00\x12\x0f\n\x0bVOLTAGE_RAW\x10\x01\x12\x0f\n\x0bVOLTAGE_RMS\x10\x02\x12\x18\n\x14VOLTAGE_RMS_WINDOWED\x10\x03\x12\x16\n\x12\x46REQUENCY_WINDOWED\x10\x04\x62\x06proto3')
)

_PAYLOADTYPE = _descriptor.EnumDescriptor(
  name='PayloadType',
  full_name='PayloadType',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='ADC_SAMPLES', index=0, number=0,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='VOLTAGE_RAW', index=1, number=1,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='VOLTAGE_RMS', index=2, number=2,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='VOLTAGE_RMS_WINDOWED', index=3, number=3,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='FREQUENCY_WINDOWED', index=4, number=4,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=901,
  serialized_end=1015,
)
_sym_db.RegisterEnumDescriptor(_PAYLOADTYPE)

PayloadType = enum_type_wrapper.EnumTypeWrapper(_PAYLOADTYPE)
ADC_SAMPLES = 0
VOLTAGE_RAW = 1
VOLTAGE_RMS = 2
VOLTAGE_RMS_WINDOWED = 3
FREQUENCY_WINDOWED = 4



_MAUKAMESSAGE = _descriptor.Descriptor(
  name='MaukaMessage',
  full_name='MaukaMessage',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='timestamp_ms', full_name='MaukaMessage.timestamp_ms', index=0,
      number=1, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='source', full_name='MaukaMessage.source', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='payload', full_name='MaukaMessage.payload', index=2,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='heartbeat', full_name='MaukaMessage.heartbeat', index=3,
      number=4, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='makai_event', full_name='MaukaMessage.makai_event', index=4,
      number=5, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='measurement', full_name='MaukaMessage.measurement', index=5,
      number=6, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='makai_trigger', full_name='MaukaMessage.makai_trigger', index=6,
      number=7, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='laha_config', full_name='MaukaMessage.laha_config', index=7,
      number=8, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
    _descriptor.OneofDescriptor(
      name='message', full_name='MaukaMessage.message',
      index=0, containing_type=None, fields=[]),
  ],
  serialized_start=16,
  serialized_end=290,
)


_PAYLOAD = _descriptor.Descriptor(
  name='Payload',
  full_name='Payload',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='event_id', full_name='Payload.event_id', index=0,
      number=1, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='box_id', full_name='Payload.box_id', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='data', full_name='Payload.data', index=2,
      number=3, type=1, cpp_type=5, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='payload_type', full_name='Payload.payload_type', index=3,
      number=4, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='start_timestamp_ms', full_name='Payload.start_timestamp_ms', index=4,
      number=5, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='end_timestamp_ms', full_name='Payload.end_timestamp_ms', index=5,
      number=6, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=293,
  serialized_end=440,
)


_HEARTBEAT = _descriptor.Descriptor(
  name='Heartbeat',
  full_name='Heartbeat',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='last_received_timestamp_ms', full_name='Heartbeat.last_received_timestamp_ms', index=0,
      number=1, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='on_message_count', full_name='Heartbeat.on_message_count', index=1,
      number=2, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='status', full_name='Heartbeat.status', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=442,
  serialized_end=531,
)


_MAKAIEVENT = _descriptor.Descriptor(
  name='MakaiEvent',
  full_name='MakaiEvent',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='event_id', full_name='MakaiEvent.event_id', index=0,
      number=1, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=533,
  serialized_end=563,
)


_MEASUREMENT = _descriptor.Descriptor(
  name='Measurement',
  full_name='Measurement',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='box_id', full_name='Measurement.box_id', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='timestamp_ms', full_name='Measurement.timestamp_ms', index=1,
      number=2, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='frequency', full_name='Measurement.frequency', index=2,
      number=3, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='voltage_rms', full_name='Measurement.voltage_rms', index=3,
      number=4, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='thd', full_name='Measurement.thd', index=4,
      number=5, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=565,
  serialized_end=669,
)


_MAKAITRIGGER = _descriptor.Descriptor(
  name='MakaiTrigger',
  full_name='MakaiTrigger',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='event_start_timestamp_ms', full_name='MakaiTrigger.event_start_timestamp_ms', index=0,
      number=1, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='event_end_timestamp_ms', full_name='MakaiTrigger.event_end_timestamp_ms', index=1,
      number=2, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='event_type', full_name='MakaiTrigger.event_type', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='max_value', full_name='MakaiTrigger.max_value', index=3,
      number=4, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='box_id', full_name='MakaiTrigger.box_id', index=4,
      number=5, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=672,
  serialized_end=807,
)


_LAHACONFIG = _descriptor.Descriptor(
  name='LahaConfig',
  full_name='LahaConfig',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='ttl', full_name='LahaConfig.ttl', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
    _descriptor.OneofDescriptor(
      name='laha_config', full_name='LahaConfig.laha_config',
      index=0, containing_type=None, fields=[]),
  ],
  serialized_start=809,
  serialized_end=857,
)


_TTL = _descriptor.Descriptor(
  name='Ttl',
  full_name='Ttl',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='collection', full_name='Ttl.collection', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='ttl_s', full_name='Ttl.ttl_s', index=1,
      number=2, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=859,
  serialized_end=899,
)

_MAUKAMESSAGE.fields_by_name['payload'].message_type = _PAYLOAD
_MAUKAMESSAGE.fields_by_name['heartbeat'].message_type = _HEARTBEAT
_MAUKAMESSAGE.fields_by_name['makai_event'].message_type = _MAKAIEVENT
_MAUKAMESSAGE.fields_by_name['measurement'].message_type = _MEASUREMENT
_MAUKAMESSAGE.fields_by_name['makai_trigger'].message_type = _MAKAITRIGGER
_MAUKAMESSAGE.fields_by_name['laha_config'].message_type = _LAHACONFIG
_MAUKAMESSAGE.oneofs_by_name['message'].fields.append(
  _MAUKAMESSAGE.fields_by_name['payload'])
_MAUKAMESSAGE.fields_by_name['payload'].containing_oneof = _MAUKAMESSAGE.oneofs_by_name['message']
_MAUKAMESSAGE.oneofs_by_name['message'].fields.append(
  _MAUKAMESSAGE.fields_by_name['heartbeat'])
_MAUKAMESSAGE.fields_by_name['heartbeat'].containing_oneof = _MAUKAMESSAGE.oneofs_by_name['message']
_MAUKAMESSAGE.oneofs_by_name['message'].fields.append(
  _MAUKAMESSAGE.fields_by_name['makai_event'])
_MAUKAMESSAGE.fields_by_name['makai_event'].containing_oneof = _MAUKAMESSAGE.oneofs_by_name['message']
_MAUKAMESSAGE.oneofs_by_name['message'].fields.append(
  _MAUKAMESSAGE.fields_by_name['measurement'])
_MAUKAMESSAGE.fields_by_name['measurement'].containing_oneof = _MAUKAMESSAGE.oneofs_by_name['message']
_MAUKAMESSAGE.oneofs_by_name['message'].fields.append(
  _MAUKAMESSAGE.fields_by_name['makai_trigger'])
_MAUKAMESSAGE.fields_by_name['makai_trigger'].containing_oneof = _MAUKAMESSAGE.oneofs_by_name['message']
_MAUKAMESSAGE.oneofs_by_name['message'].fields.append(
  _MAUKAMESSAGE.fields_by_name['laha_config'])
_MAUKAMESSAGE.fields_by_name['laha_config'].containing_oneof = _MAUKAMESSAGE.oneofs_by_name['message']
_PAYLOAD.fields_by_name['payload_type'].enum_type = _PAYLOADTYPE
_LAHACONFIG.fields_by_name['ttl'].message_type = _TTL
_LAHACONFIG.oneofs_by_name['laha_config'].fields.append(
  _LAHACONFIG.fields_by_name['ttl'])
_LAHACONFIG.fields_by_name['ttl'].containing_oneof = _LAHACONFIG.oneofs_by_name['laha_config']
DESCRIPTOR.message_types_by_name['MaukaMessage'] = _MAUKAMESSAGE
DESCRIPTOR.message_types_by_name['Payload'] = _PAYLOAD
DESCRIPTOR.message_types_by_name['Heartbeat'] = _HEARTBEAT
DESCRIPTOR.message_types_by_name['MakaiEvent'] = _MAKAIEVENT
DESCRIPTOR.message_types_by_name['Measurement'] = _MEASUREMENT
DESCRIPTOR.message_types_by_name['MakaiTrigger'] = _MAKAITRIGGER
DESCRIPTOR.message_types_by_name['LahaConfig'] = _LAHACONFIG
DESCRIPTOR.message_types_by_name['Ttl'] = _TTL
DESCRIPTOR.enum_types_by_name['PayloadType'] = _PAYLOADTYPE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

MaukaMessage = _reflection.GeneratedProtocolMessageType('MaukaMessage', (_message.Message,), dict(
  DESCRIPTOR = _MAUKAMESSAGE,
  __module__ = 'mauka_pb2'
  # @@protoc_insertion_point(class_scope:MaukaMessage)
  ))
_sym_db.RegisterMessage(MaukaMessage)

Payload = _reflection.GeneratedProtocolMessageType('Payload', (_message.Message,), dict(
  DESCRIPTOR = _PAYLOAD,
  __module__ = 'mauka_pb2'
  # @@protoc_insertion_point(class_scope:Payload)
  ))
_sym_db.RegisterMessage(Payload)

Heartbeat = _reflection.GeneratedProtocolMessageType('Heartbeat', (_message.Message,), dict(
  DESCRIPTOR = _HEARTBEAT,
  __module__ = 'mauka_pb2'
  # @@protoc_insertion_point(class_scope:Heartbeat)
  ))
_sym_db.RegisterMessage(Heartbeat)

MakaiEvent = _reflection.GeneratedProtocolMessageType('MakaiEvent', (_message.Message,), dict(
  DESCRIPTOR = _MAKAIEVENT,
  __module__ = 'mauka_pb2'
  # @@protoc_insertion_point(class_scope:MakaiEvent)
  ))
_sym_db.RegisterMessage(MakaiEvent)

Measurement = _reflection.GeneratedProtocolMessageType('Measurement', (_message.Message,), dict(
  DESCRIPTOR = _MEASUREMENT,
  __module__ = 'mauka_pb2'
  # @@protoc_insertion_point(class_scope:Measurement)
  ))
_sym_db.RegisterMessage(Measurement)

MakaiTrigger = _reflection.GeneratedProtocolMessageType('MakaiTrigger', (_message.Message,), dict(
  DESCRIPTOR = _MAKAITRIGGER,
  __module__ = 'mauka_pb2'
  # @@protoc_insertion_point(class_scope:MakaiTrigger)
  ))
_sym_db.RegisterMessage(MakaiTrigger)

LahaConfig = _reflection.GeneratedProtocolMessageType('LahaConfig', (_message.Message,), dict(
  DESCRIPTOR = _LAHACONFIG,
  __module__ = 'mauka_pb2'
  # @@protoc_insertion_point(class_scope:LahaConfig)
  ))
_sym_db.RegisterMessage(LahaConfig)

Ttl = _reflection.GeneratedProtocolMessageType('Ttl', (_message.Message,), dict(
  DESCRIPTOR = _TTL,
  __module__ = 'mauka_pb2'
  # @@protoc_insertion_point(class_scope:Ttl)
  ))
_sym_db.RegisterMessage(Ttl)


# @@protoc_insertion_point(module_scope)
