# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: rustproto.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import descriptor_pb2 as google_dot_protobuf_dot_descriptor__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='rustproto.proto',
  package='rustproto',
  syntax='proto2',
  serialized_options=None,
  serialized_pb=_b('\n\x0frustproto.proto\x12\trustproto\x1a google/protobuf/descriptor.proto:8\n\x10\x65xpose_oneof_all\x12\x1c.google.protobuf.FileOptions\x18\xe9\x84\x01 \x01(\x08:9\n\x11\x65xpose_fields_all\x12\x1c.google.protobuf.FileOptions\x18\xeb\x84\x01 \x01(\x08:>\n\x16generate_accessors_all\x12\x1c.google.protobuf.FileOptions\x18\xec\x84\x01 \x01(\x08:;\n\x13generate_getter_all\x12\x1c.google.protobuf.FileOptions\x18\xed\x84\x01 \x01(\x08:F\n\x1e\x63\x61rllerche_bytes_for_bytes_all\x12\x1c.google.protobuf.FileOptions\x18\xf3\x84\x01 \x01(\x08:G\n\x1f\x63\x61rllerche_bytes_for_string_all\x12\x1c.google.protobuf.FileOptions\x18\xf4\x84\x01 \x01(\x08:>\n\x16repeated_field_vec_all\x12\x1c.google.protobuf.FileOptions\x18\xfc\x84\x01 \x01(\x08:E\n\x1dsingular_field_option_box_all\x12\x1c.google.protobuf.FileOptions\x18\x80\x85\x01 \x01(\x08:A\n\x19singular_field_option_all\x12\x1c.google.protobuf.FileOptions\x18\x81\x85\x01 \x01(\x08:8\n\x10serde_derive_all\x12\x1c.google.protobuf.FileOptions\x18\x86\x85\x01 \x01(\x08:7\n\x0c\x65xpose_oneof\x12\x1f.google.protobuf.MessageOptions\x18\xe9\x84\x01 \x01(\x08:8\n\rexpose_fields\x12\x1f.google.protobuf.MessageOptions\x18\xeb\x84\x01 \x01(\x08:=\n\x12generate_accessors\x12\x1f.google.protobuf.MessageOptions\x18\xec\x84\x01 \x01(\x08::\n\x0fgenerate_getter\x12\x1f.google.protobuf.MessageOptions\x18\xed\x84\x01 \x01(\x08:E\n\x1a\x63\x61rllerche_bytes_for_bytes\x12\x1f.google.protobuf.MessageOptions\x18\xf3\x84\x01 \x01(\x08:F\n\x1b\x63\x61rllerche_bytes_for_string\x12\x1f.google.protobuf.MessageOptions\x18\xf4\x84\x01 \x01(\x08:=\n\x12repeated_field_vec\x12\x1f.google.protobuf.MessageOptions\x18\xfc\x84\x01 \x01(\x08:D\n\x19singular_field_option_box\x12\x1f.google.protobuf.MessageOptions\x18\x80\x85\x01 \x01(\x08:@\n\x15singular_field_option\x12\x1f.google.protobuf.MessageOptions\x18\x81\x85\x01 \x01(\x08:7\n\x0cserde_derive\x12\x1f.google.protobuf.MessageOptions\x18\x86\x85\x01 \x01(\x08:<\n\x13\x65xpose_fields_field\x12\x1d.google.protobuf.FieldOptions\x18\xeb\x84\x01 \x01(\x08:A\n\x18generate_accessors_field\x12\x1d.google.protobuf.FieldOptions\x18\xec\x84\x01 \x01(\x08:>\n\x15generate_getter_field\x12\x1d.google.protobuf.FieldOptions\x18\xed\x84\x01 \x01(\x08:I\n carllerche_bytes_for_bytes_field\x12\x1d.google.protobuf.FieldOptions\x18\xf3\x84\x01 \x01(\x08:J\n!carllerche_bytes_for_string_field\x12\x1d.google.protobuf.FieldOptions\x18\xf4\x84\x01 \x01(\x08:A\n\x18repeated_field_vec_field\x12\x1d.google.protobuf.FieldOptions\x18\xfc\x84\x01 \x01(\x08:H\n\x1fsingular_field_option_box_field\x12\x1d.google.protobuf.FieldOptions\x18\x80\x85\x01 \x01(\x08:D\n\x1bsingular_field_option_field\x12\x1d.google.protobuf.FieldOptions\x18\x81\x85\x01 \x01(\x08')
  ,
  dependencies=[google_dot_protobuf_dot_descriptor__pb2.DESCRIPTOR,])


EXPOSE_ONEOF_ALL_FIELD_NUMBER = 17001
expose_oneof_all = _descriptor.FieldDescriptor(
  name='expose_oneof_all', full_name='rustproto.expose_oneof_all', index=0,
  number=17001, type=8, cpp_type=7, label=1,
  has_default_value=False, default_value=False,
  message_type=None, enum_type=None, containing_type=None,
  is_extension=True, extension_scope=None,
  serialized_options=None, file=DESCRIPTOR)
EXPOSE_FIELDS_ALL_FIELD_NUMBER = 17003
expose_fields_all = _descriptor.FieldDescriptor(
  name='expose_fields_all', full_name='rustproto.expose_fields_all', index=1,
  number=17003, type=8, cpp_type=7, label=1,
  has_default_value=False, default_value=False,
  message_type=None, enum_type=None, containing_type=None,
  is_extension=True, extension_scope=None,
  serialized_options=None, file=DESCRIPTOR)
GENERATE_ACCESSORS_ALL_FIELD_NUMBER = 17004
generate_accessors_all = _descriptor.FieldDescriptor(
  name='generate_accessors_all', full_name='rustproto.generate_accessors_all', index=2,
  number=17004, type=8, cpp_type=7, label=1,
  has_default_value=False, default_value=False,
  message_type=None, enum_type=None, containing_type=None,
  is_extension=True, extension_scope=None,
  serialized_options=None, file=DESCRIPTOR)
GENERATE_GETTER_ALL_FIELD_NUMBER = 17005
generate_getter_all = _descriptor.FieldDescriptor(
  name='generate_getter_all', full_name='rustproto.generate_getter_all', index=3,
  number=17005, type=8, cpp_type=7, label=1,
  has_default_value=False, default_value=False,
  message_type=None, enum_type=None, containing_type=None,
  is_extension=True, extension_scope=None,
  serialized_options=None, file=DESCRIPTOR)
CARLLERCHE_BYTES_FOR_BYTES_ALL_FIELD_NUMBER = 17011
carllerche_bytes_for_bytes_all = _descriptor.FieldDescriptor(
  name='carllerche_bytes_for_bytes_all', full_name='rustproto.carllerche_bytes_for_bytes_all', index=4,
  number=17011, type=8, cpp_type=7, label=1,
  has_default_value=False, default_value=False,
  message_type=None, enum_type=None, containing_type=None,
  is_extension=True, extension_scope=None,
  serialized_options=None, file=DESCRIPTOR)
CARLLERCHE_BYTES_FOR_STRING_ALL_FIELD_NUMBER = 17012
carllerche_bytes_for_string_all = _descriptor.FieldDescriptor(
  name='carllerche_bytes_for_string_all', full_name='rustproto.carllerche_bytes_for_string_all', index=5,
  number=17012, type=8, cpp_type=7, label=1,
  has_default_value=False, default_value=False,
  message_type=None, enum_type=None, containing_type=None,
  is_extension=True, extension_scope=None,
  serialized_options=None, file=DESCRIPTOR)
REPEATED_FIELD_VEC_ALL_FIELD_NUMBER = 17020
repeated_field_vec_all = _descriptor.FieldDescriptor(
  name='repeated_field_vec_all', full_name='rustproto.repeated_field_vec_all', index=6,
  number=17020, type=8, cpp_type=7, label=1,
  has_default_value=False, default_value=False,
  message_type=None, enum_type=None, containing_type=None,
  is_extension=True, extension_scope=None,
  serialized_options=None, file=DESCRIPTOR)
SINGULAR_FIELD_OPTION_BOX_ALL_FIELD_NUMBER = 17024
singular_field_option_box_all = _descriptor.FieldDescriptor(
  name='singular_field_option_box_all', full_name='rustproto.singular_field_option_box_all', index=7,
  number=17024, type=8, cpp_type=7, label=1,
  has_default_value=False, default_value=False,
  message_type=None, enum_type=None, containing_type=None,
  is_extension=True, extension_scope=None,
  serialized_options=None, file=DESCRIPTOR)
SINGULAR_FIELD_OPTION_ALL_FIELD_NUMBER = 17025
singular_field_option_all = _descriptor.FieldDescriptor(
  name='singular_field_option_all', full_name='rustproto.singular_field_option_all', index=8,
  number=17025, type=8, cpp_type=7, label=1,
  has_default_value=False, default_value=False,
  message_type=None, enum_type=None, containing_type=None,
  is_extension=True, extension_scope=None,
  serialized_options=None, file=DESCRIPTOR)
SERDE_DERIVE_ALL_FIELD_NUMBER = 17030
serde_derive_all = _descriptor.FieldDescriptor(
  name='serde_derive_all', full_name='rustproto.serde_derive_all', index=9,
  number=17030, type=8, cpp_type=7, label=1,
  has_default_value=False, default_value=False,
  message_type=None, enum_type=None, containing_type=None,
  is_extension=True, extension_scope=None,
  serialized_options=None, file=DESCRIPTOR)
EXPOSE_ONEOF_FIELD_NUMBER = 17001
expose_oneof = _descriptor.FieldDescriptor(
  name='expose_oneof', full_name='rustproto.expose_oneof', index=10,
  number=17001, type=8, cpp_type=7, label=1,
  has_default_value=False, default_value=False,
  message_type=None, enum_type=None, containing_type=None,
  is_extension=True, extension_scope=None,
  serialized_options=None, file=DESCRIPTOR)
EXPOSE_FIELDS_FIELD_NUMBER = 17003
expose_fields = _descriptor.FieldDescriptor(
  name='expose_fields', full_name='rustproto.expose_fields', index=11,
  number=17003, type=8, cpp_type=7, label=1,
  has_default_value=False, default_value=False,
  message_type=None, enum_type=None, containing_type=None,
  is_extension=True, extension_scope=None,
  serialized_options=None, file=DESCRIPTOR)
GENERATE_ACCESSORS_FIELD_NUMBER = 17004
generate_accessors = _descriptor.FieldDescriptor(
  name='generate_accessors', full_name='rustproto.generate_accessors', index=12,
  number=17004, type=8, cpp_type=7, label=1,
  has_default_value=False, default_value=False,
  message_type=None, enum_type=None, containing_type=None,
  is_extension=True, extension_scope=None,
  serialized_options=None, file=DESCRIPTOR)
GENERATE_GETTER_FIELD_NUMBER = 17005
generate_getter = _descriptor.FieldDescriptor(
  name='generate_getter', full_name='rustproto.generate_getter', index=13,
  number=17005, type=8, cpp_type=7, label=1,
  has_default_value=False, default_value=False,
  message_type=None, enum_type=None, containing_type=None,
  is_extension=True, extension_scope=None,
  serialized_options=None, file=DESCRIPTOR)
CARLLERCHE_BYTES_FOR_BYTES_FIELD_NUMBER = 17011
carllerche_bytes_for_bytes = _descriptor.FieldDescriptor(
  name='carllerche_bytes_for_bytes', full_name='rustproto.carllerche_bytes_for_bytes', index=14,
  number=17011, type=8, cpp_type=7, label=1,
  has_default_value=False, default_value=False,
  message_type=None, enum_type=None, containing_type=None,
  is_extension=True, extension_scope=None,
  serialized_options=None, file=DESCRIPTOR)
CARLLERCHE_BYTES_FOR_STRING_FIELD_NUMBER = 17012
carllerche_bytes_for_string = _descriptor.FieldDescriptor(
  name='carllerche_bytes_for_string', full_name='rustproto.carllerche_bytes_for_string', index=15,
  number=17012, type=8, cpp_type=7, label=1,
  has_default_value=False, default_value=False,
  message_type=None, enum_type=None, containing_type=None,
  is_extension=True, extension_scope=None,
  serialized_options=None, file=DESCRIPTOR)
REPEATED_FIELD_VEC_FIELD_NUMBER = 17020
repeated_field_vec = _descriptor.FieldDescriptor(
  name='repeated_field_vec', full_name='rustproto.repeated_field_vec', index=16,
  number=17020, type=8, cpp_type=7, label=1,
  has_default_value=False, default_value=False,
  message_type=None, enum_type=None, containing_type=None,
  is_extension=True, extension_scope=None,
  serialized_options=None, file=DESCRIPTOR)
SINGULAR_FIELD_OPTION_BOX_FIELD_NUMBER = 17024
singular_field_option_box = _descriptor.FieldDescriptor(
  name='singular_field_option_box', full_name='rustproto.singular_field_option_box', index=17,
  number=17024, type=8, cpp_type=7, label=1,
  has_default_value=False, default_value=False,
  message_type=None, enum_type=None, containing_type=None,
  is_extension=True, extension_scope=None,
  serialized_options=None, file=DESCRIPTOR)
SINGULAR_FIELD_OPTION_FIELD_NUMBER = 17025
singular_field_option = _descriptor.FieldDescriptor(
  name='singular_field_option', full_name='rustproto.singular_field_option', index=18,
  number=17025, type=8, cpp_type=7, label=1,
  has_default_value=False, default_value=False,
  message_type=None, enum_type=None, containing_type=None,
  is_extension=True, extension_scope=None,
  serialized_options=None, file=DESCRIPTOR)
SERDE_DERIVE_FIELD_NUMBER = 17030
serde_derive = _descriptor.FieldDescriptor(
  name='serde_derive', full_name='rustproto.serde_derive', index=19,
  number=17030, type=8, cpp_type=7, label=1,
  has_default_value=False, default_value=False,
  message_type=None, enum_type=None, containing_type=None,
  is_extension=True, extension_scope=None,
  serialized_options=None, file=DESCRIPTOR)
EXPOSE_FIELDS_FIELD_FIELD_NUMBER = 17003
expose_fields_field = _descriptor.FieldDescriptor(
  name='expose_fields_field', full_name='rustproto.expose_fields_field', index=20,
  number=17003, type=8, cpp_type=7, label=1,
  has_default_value=False, default_value=False,
  message_type=None, enum_type=None, containing_type=None,
  is_extension=True, extension_scope=None,
  serialized_options=None, file=DESCRIPTOR)
GENERATE_ACCESSORS_FIELD_FIELD_NUMBER = 17004
generate_accessors_field = _descriptor.FieldDescriptor(
  name='generate_accessors_field', full_name='rustproto.generate_accessors_field', index=21,
  number=17004, type=8, cpp_type=7, label=1,
  has_default_value=False, default_value=False,
  message_type=None, enum_type=None, containing_type=None,
  is_extension=True, extension_scope=None,
  serialized_options=None, file=DESCRIPTOR)
GENERATE_GETTER_FIELD_FIELD_NUMBER = 17005
generate_getter_field = _descriptor.FieldDescriptor(
  name='generate_getter_field', full_name='rustproto.generate_getter_field', index=22,
  number=17005, type=8, cpp_type=7, label=1,
  has_default_value=False, default_value=False,
  message_type=None, enum_type=None, containing_type=None,
  is_extension=True, extension_scope=None,
  serialized_options=None, file=DESCRIPTOR)
CARLLERCHE_BYTES_FOR_BYTES_FIELD_FIELD_NUMBER = 17011
carllerche_bytes_for_bytes_field = _descriptor.FieldDescriptor(
  name='carllerche_bytes_for_bytes_field', full_name='rustproto.carllerche_bytes_for_bytes_field', index=23,
  number=17011, type=8, cpp_type=7, label=1,
  has_default_value=False, default_value=False,
  message_type=None, enum_type=None, containing_type=None,
  is_extension=True, extension_scope=None,
  serialized_options=None, file=DESCRIPTOR)
CARLLERCHE_BYTES_FOR_STRING_FIELD_FIELD_NUMBER = 17012
carllerche_bytes_for_string_field = _descriptor.FieldDescriptor(
  name='carllerche_bytes_for_string_field', full_name='rustproto.carllerche_bytes_for_string_field', index=24,
  number=17012, type=8, cpp_type=7, label=1,
  has_default_value=False, default_value=False,
  message_type=None, enum_type=None, containing_type=None,
  is_extension=True, extension_scope=None,
  serialized_options=None, file=DESCRIPTOR)
REPEATED_FIELD_VEC_FIELD_FIELD_NUMBER = 17020
repeated_field_vec_field = _descriptor.FieldDescriptor(
  name='repeated_field_vec_field', full_name='rustproto.repeated_field_vec_field', index=25,
  number=17020, type=8, cpp_type=7, label=1,
  has_default_value=False, default_value=False,
  message_type=None, enum_type=None, containing_type=None,
  is_extension=True, extension_scope=None,
  serialized_options=None, file=DESCRIPTOR)
SINGULAR_FIELD_OPTION_BOX_FIELD_FIELD_NUMBER = 17024
singular_field_option_box_field = _descriptor.FieldDescriptor(
  name='singular_field_option_box_field', full_name='rustproto.singular_field_option_box_field', index=26,
  number=17024, type=8, cpp_type=7, label=1,
  has_default_value=False, default_value=False,
  message_type=None, enum_type=None, containing_type=None,
  is_extension=True, extension_scope=None,
  serialized_options=None, file=DESCRIPTOR)
SINGULAR_FIELD_OPTION_FIELD_FIELD_NUMBER = 17025
singular_field_option_field = _descriptor.FieldDescriptor(
  name='singular_field_option_field', full_name='rustproto.singular_field_option_field', index=27,
  number=17025, type=8, cpp_type=7, label=1,
  has_default_value=False, default_value=False,
  message_type=None, enum_type=None, containing_type=None,
  is_extension=True, extension_scope=None,
  serialized_options=None, file=DESCRIPTOR)

DESCRIPTOR.extensions_by_name['expose_oneof_all'] = expose_oneof_all
DESCRIPTOR.extensions_by_name['expose_fields_all'] = expose_fields_all
DESCRIPTOR.extensions_by_name['generate_accessors_all'] = generate_accessors_all
DESCRIPTOR.extensions_by_name['generate_getter_all'] = generate_getter_all
DESCRIPTOR.extensions_by_name['carllerche_bytes_for_bytes_all'] = carllerche_bytes_for_bytes_all
DESCRIPTOR.extensions_by_name['carllerche_bytes_for_string_all'] = carllerche_bytes_for_string_all
DESCRIPTOR.extensions_by_name['repeated_field_vec_all'] = repeated_field_vec_all
DESCRIPTOR.extensions_by_name['singular_field_option_box_all'] = singular_field_option_box_all
DESCRIPTOR.extensions_by_name['singular_field_option_all'] = singular_field_option_all
DESCRIPTOR.extensions_by_name['serde_derive_all'] = serde_derive_all
DESCRIPTOR.extensions_by_name['expose_oneof'] = expose_oneof
DESCRIPTOR.extensions_by_name['expose_fields'] = expose_fields
DESCRIPTOR.extensions_by_name['generate_accessors'] = generate_accessors
DESCRIPTOR.extensions_by_name['generate_getter'] = generate_getter
DESCRIPTOR.extensions_by_name['carllerche_bytes_for_bytes'] = carllerche_bytes_for_bytes
DESCRIPTOR.extensions_by_name['carllerche_bytes_for_string'] = carllerche_bytes_for_string
DESCRIPTOR.extensions_by_name['repeated_field_vec'] = repeated_field_vec
DESCRIPTOR.extensions_by_name['singular_field_option_box'] = singular_field_option_box
DESCRIPTOR.extensions_by_name['singular_field_option'] = singular_field_option
DESCRIPTOR.extensions_by_name['serde_derive'] = serde_derive
DESCRIPTOR.extensions_by_name['expose_fields_field'] = expose_fields_field
DESCRIPTOR.extensions_by_name['generate_accessors_field'] = generate_accessors_field
DESCRIPTOR.extensions_by_name['generate_getter_field'] = generate_getter_field
DESCRIPTOR.extensions_by_name['carllerche_bytes_for_bytes_field'] = carllerche_bytes_for_bytes_field
DESCRIPTOR.extensions_by_name['carllerche_bytes_for_string_field'] = carllerche_bytes_for_string_field
DESCRIPTOR.extensions_by_name['repeated_field_vec_field'] = repeated_field_vec_field
DESCRIPTOR.extensions_by_name['singular_field_option_box_field'] = singular_field_option_box_field
DESCRIPTOR.extensions_by_name['singular_field_option_field'] = singular_field_option_field
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

google_dot_protobuf_dot_descriptor__pb2.FileOptions.RegisterExtension(expose_oneof_all)
google_dot_protobuf_dot_descriptor__pb2.FileOptions.RegisterExtension(expose_fields_all)
google_dot_protobuf_dot_descriptor__pb2.FileOptions.RegisterExtension(generate_accessors_all)
google_dot_protobuf_dot_descriptor__pb2.FileOptions.RegisterExtension(generate_getter_all)
google_dot_protobuf_dot_descriptor__pb2.FileOptions.RegisterExtension(carllerche_bytes_for_bytes_all)
google_dot_protobuf_dot_descriptor__pb2.FileOptions.RegisterExtension(carllerche_bytes_for_string_all)
google_dot_protobuf_dot_descriptor__pb2.FileOptions.RegisterExtension(repeated_field_vec_all)
google_dot_protobuf_dot_descriptor__pb2.FileOptions.RegisterExtension(singular_field_option_box_all)
google_dot_protobuf_dot_descriptor__pb2.FileOptions.RegisterExtension(singular_field_option_all)
google_dot_protobuf_dot_descriptor__pb2.FileOptions.RegisterExtension(serde_derive_all)
google_dot_protobuf_dot_descriptor__pb2.MessageOptions.RegisterExtension(expose_oneof)
google_dot_protobuf_dot_descriptor__pb2.MessageOptions.RegisterExtension(expose_fields)
google_dot_protobuf_dot_descriptor__pb2.MessageOptions.RegisterExtension(generate_accessors)
google_dot_protobuf_dot_descriptor__pb2.MessageOptions.RegisterExtension(generate_getter)
google_dot_protobuf_dot_descriptor__pb2.MessageOptions.RegisterExtension(carllerche_bytes_for_bytes)
google_dot_protobuf_dot_descriptor__pb2.MessageOptions.RegisterExtension(carllerche_bytes_for_string)
google_dot_protobuf_dot_descriptor__pb2.MessageOptions.RegisterExtension(repeated_field_vec)
google_dot_protobuf_dot_descriptor__pb2.MessageOptions.RegisterExtension(singular_field_option_box)
google_dot_protobuf_dot_descriptor__pb2.MessageOptions.RegisterExtension(singular_field_option)
google_dot_protobuf_dot_descriptor__pb2.MessageOptions.RegisterExtension(serde_derive)
google_dot_protobuf_dot_descriptor__pb2.FieldOptions.RegisterExtension(expose_fields_field)
google_dot_protobuf_dot_descriptor__pb2.FieldOptions.RegisterExtension(generate_accessors_field)
google_dot_protobuf_dot_descriptor__pb2.FieldOptions.RegisterExtension(generate_getter_field)
google_dot_protobuf_dot_descriptor__pb2.FieldOptions.RegisterExtension(carllerche_bytes_for_bytes_field)
google_dot_protobuf_dot_descriptor__pb2.FieldOptions.RegisterExtension(carllerche_bytes_for_string_field)
google_dot_protobuf_dot_descriptor__pb2.FieldOptions.RegisterExtension(repeated_field_vec_field)
google_dot_protobuf_dot_descriptor__pb2.FieldOptions.RegisterExtension(singular_field_option_box_field)
google_dot_protobuf_dot_descriptor__pb2.FieldOptions.RegisterExtension(singular_field_option_field)

# @@protoc_insertion_point(module_scope)