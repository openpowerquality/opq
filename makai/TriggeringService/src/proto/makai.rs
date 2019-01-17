// This file is generated. Do not edit
// @generated

// https://github.com/Manishearth/rust-clippy/issues/702
#![allow(unknown_lints)]
#![allow(clippy)]

#![cfg_attr(rustfmt, rustfmt_skip)]

#![allow(box_pointers)]
#![allow(dead_code)]
#![allow(missing_docs)]
#![allow(non_camel_case_types)]
#![allow(non_snake_case)]
#![allow(non_upper_case_globals)]
#![allow(trivial_casts)]
#![allow(unsafe_code)]
#![allow(unused_imports)]
#![allow(unused_results)]

use protobuf::Message as Message_imported_for_functions;
use protobuf::ProtobufEnum as ProtobufEnum_imported_for_functions;

#[derive(PartialEq,Clone,Default)]
pub struct RequestEventMessage {
    // message fields
    pub start_timestamp_ms_utc: u64,
    pub end_timestamp_ms_utc: u64,
    pub box_ids: i32,
    pub requestee: ::std::string::String,
    pub description: ::std::string::String,
    pub request_data: bool,
    // special fields
    unknown_fields: ::protobuf::UnknownFields,
    cached_size: ::protobuf::CachedSize,
}

// see codegen.rs for the explanation why impl Sync explicitly
unsafe impl ::std::marker::Sync for RequestEventMessage {}

impl RequestEventMessage {
    pub fn new() -> RequestEventMessage {
        ::std::default::Default::default()
    }

    pub fn default_instance() -> &'static RequestEventMessage {
        static mut instance: ::protobuf::lazy::Lazy<RequestEventMessage> = ::protobuf::lazy::Lazy {
            lock: ::protobuf::lazy::ONCE_INIT,
            ptr: 0 as *const RequestEventMessage,
        };
        unsafe {
            instance.get(RequestEventMessage::new)
        }
    }

    // uint64 start_timestamp_ms_utc = 1;

    pub fn clear_start_timestamp_ms_utc(&mut self) {
        self.start_timestamp_ms_utc = 0;
    }

    // Param is passed by value, moved
    pub fn set_start_timestamp_ms_utc(&mut self, v: u64) {
        self.start_timestamp_ms_utc = v;
    }

    pub fn get_start_timestamp_ms_utc(&self) -> u64 {
        self.start_timestamp_ms_utc
    }

    fn get_start_timestamp_ms_utc_for_reflect(&self) -> &u64 {
        &self.start_timestamp_ms_utc
    }

    fn mut_start_timestamp_ms_utc_for_reflect(&mut self) -> &mut u64 {
        &mut self.start_timestamp_ms_utc
    }

    // uint64 end_timestamp_ms_utc = 2;

    pub fn clear_end_timestamp_ms_utc(&mut self) {
        self.end_timestamp_ms_utc = 0;
    }

    // Param is passed by value, moved
    pub fn set_end_timestamp_ms_utc(&mut self, v: u64) {
        self.end_timestamp_ms_utc = v;
    }

    pub fn get_end_timestamp_ms_utc(&self) -> u64 {
        self.end_timestamp_ms_utc
    }

    fn get_end_timestamp_ms_utc_for_reflect(&self) -> &u64 {
        &self.end_timestamp_ms_utc
    }

    fn mut_end_timestamp_ms_utc_for_reflect(&mut self) -> &mut u64 {
        &mut self.end_timestamp_ms_utc
    }

    // int32 box_ids = 3;

    pub fn clear_box_ids(&mut self) {
        self.box_ids = 0;
    }

    // Param is passed by value, moved
    pub fn set_box_ids(&mut self, v: i32) {
        self.box_ids = v;
    }

    pub fn get_box_ids(&self) -> i32 {
        self.box_ids
    }

    fn get_box_ids_for_reflect(&self) -> &i32 {
        &self.box_ids
    }

    fn mut_box_ids_for_reflect(&mut self) -> &mut i32 {
        &mut self.box_ids
    }

    // string requestee = 4;

    pub fn clear_requestee(&mut self) {
        self.requestee.clear();
    }

    // Param is passed by value, moved
    pub fn set_requestee(&mut self, v: ::std::string::String) {
        self.requestee = v;
    }

    // Mutable pointer to the field.
    // If field is not initialized, it is initialized with default value first.
    pub fn mut_requestee(&mut self) -> &mut ::std::string::String {
        &mut self.requestee
    }

    // Take field
    pub fn take_requestee(&mut self) -> ::std::string::String {
        ::std::mem::replace(&mut self.requestee, ::std::string::String::new())
    }

    pub fn get_requestee(&self) -> &str {
        &self.requestee
    }

    fn get_requestee_for_reflect(&self) -> &::std::string::String {
        &self.requestee
    }

    fn mut_requestee_for_reflect(&mut self) -> &mut ::std::string::String {
        &mut self.requestee
    }

    // string description = 5;

    pub fn clear_description(&mut self) {
        self.description.clear();
    }

    // Param is passed by value, moved
    pub fn set_description(&mut self, v: ::std::string::String) {
        self.description = v;
    }

    // Mutable pointer to the field.
    // If field is not initialized, it is initialized with default value first.
    pub fn mut_description(&mut self) -> &mut ::std::string::String {
        &mut self.description
    }

    // Take field
    pub fn take_description(&mut self) -> ::std::string::String {
        ::std::mem::replace(&mut self.description, ::std::string::String::new())
    }

    pub fn get_description(&self) -> &str {
        &self.description
    }

    fn get_description_for_reflect(&self) -> &::std::string::String {
        &self.description
    }

    fn mut_description_for_reflect(&mut self) -> &mut ::std::string::String {
        &mut self.description
    }

    // bool request_data = 6;

    pub fn clear_request_data(&mut self) {
        self.request_data = false;
    }

    // Param is passed by value, moved
    pub fn set_request_data(&mut self, v: bool) {
        self.request_data = v;
    }

    pub fn get_request_data(&self) -> bool {
        self.request_data
    }

    fn get_request_data_for_reflect(&self) -> &bool {
        &self.request_data
    }

    fn mut_request_data_for_reflect(&mut self) -> &mut bool {
        &mut self.request_data
    }
}

impl ::protobuf::Message for RequestEventMessage {
    fn is_initialized(&self) -> bool {
        true
    }

    fn merge_from(&mut self, is: &mut ::protobuf::CodedInputStream) -> ::protobuf::ProtobufResult<()> {
        while !is.eof()? {
            let (field_number, wire_type) = is.read_tag_unpack()?;
            match field_number {
                1 => {
                    if wire_type != ::protobuf::wire_format::WireTypeVarint {
                        return ::std::result::Result::Err(::protobuf::rt::unexpected_wire_type(wire_type));
                    }
                    let tmp = is.read_uint64()?;
                    self.start_timestamp_ms_utc = tmp;
                },
                2 => {
                    if wire_type != ::protobuf::wire_format::WireTypeVarint {
                        return ::std::result::Result::Err(::protobuf::rt::unexpected_wire_type(wire_type));
                    }
                    let tmp = is.read_uint64()?;
                    self.end_timestamp_ms_utc = tmp;
                },
                3 => {
                    if wire_type != ::protobuf::wire_format::WireTypeVarint {
                        return ::std::result::Result::Err(::protobuf::rt::unexpected_wire_type(wire_type));
                    }
                    let tmp = is.read_int32()?;
                    self.box_ids = tmp;
                },
                4 => {
                    ::protobuf::rt::read_singular_proto3_string_into(wire_type, is, &mut self.requestee)?;
                },
                5 => {
                    ::protobuf::rt::read_singular_proto3_string_into(wire_type, is, &mut self.description)?;
                },
                6 => {
                    if wire_type != ::protobuf::wire_format::WireTypeVarint {
                        return ::std::result::Result::Err(::protobuf::rt::unexpected_wire_type(wire_type));
                    }
                    let tmp = is.read_bool()?;
                    self.request_data = tmp;
                },
                _ => {
                    ::protobuf::rt::read_unknown_or_skip_group(field_number, wire_type, is, self.mut_unknown_fields())?;
                },
            };
        }
        ::std::result::Result::Ok(())
    }

    // Compute sizes of nested messages
    #[allow(unused_variables)]
    fn compute_size(&self) -> u32 {
        let mut my_size = 0;
        if self.start_timestamp_ms_utc != 0 {
            my_size += ::protobuf::rt::value_size(1, self.start_timestamp_ms_utc, ::protobuf::wire_format::WireTypeVarint);
        }
        if self.end_timestamp_ms_utc != 0 {
            my_size += ::protobuf::rt::value_size(2, self.end_timestamp_ms_utc, ::protobuf::wire_format::WireTypeVarint);
        }
        if self.box_ids != 0 {
            my_size += ::protobuf::rt::value_size(3, self.box_ids, ::protobuf::wire_format::WireTypeVarint);
        }
        if !self.requestee.is_empty() {
            my_size += ::protobuf::rt::string_size(4, &self.requestee);
        }
        if !self.description.is_empty() {
            my_size += ::protobuf::rt::string_size(5, &self.description);
        }
        if self.request_data != false {
            my_size += 2;
        }
        my_size += ::protobuf::rt::unknown_fields_size(self.get_unknown_fields());
        self.cached_size.set(my_size);
        my_size
    }

    fn write_to_with_cached_sizes(&self, os: &mut ::protobuf::CodedOutputStream) -> ::protobuf::ProtobufResult<()> {
        if self.start_timestamp_ms_utc != 0 {
            os.write_uint64(1, self.start_timestamp_ms_utc)?;
        }
        if self.end_timestamp_ms_utc != 0 {
            os.write_uint64(2, self.end_timestamp_ms_utc)?;
        }
        if self.box_ids != 0 {
            os.write_int32(3, self.box_ids)?;
        }
        if !self.requestee.is_empty() {
            os.write_string(4, &self.requestee)?;
        }
        if !self.description.is_empty() {
            os.write_string(5, &self.description)?;
        }
        if self.request_data != false {
            os.write_bool(6, self.request_data)?;
        }
        os.write_unknown_fields(self.get_unknown_fields())?;
        ::std::result::Result::Ok(())
    }

    fn get_cached_size(&self) -> u32 {
        self.cached_size.get()
    }

    fn get_unknown_fields(&self) -> &::protobuf::UnknownFields {
        &self.unknown_fields
    }

    fn mut_unknown_fields(&mut self) -> &mut ::protobuf::UnknownFields {
        &mut self.unknown_fields
    }

    fn as_any(&self) -> &::std::any::Any {
        self as &::std::any::Any
    }
    fn as_any_mut(&mut self) -> &mut ::std::any::Any {
        self as &mut ::std::any::Any
    }
    fn into_any(self: Box<Self>) -> ::std::boxed::Box<::std::any::Any> {
        self
    }

    fn descriptor(&self) -> &'static ::protobuf::reflect::MessageDescriptor {
        ::protobuf::MessageStatic::descriptor_static(None::<Self>)
    }
}

impl ::protobuf::MessageStatic for RequestEventMessage {
    fn new() -> RequestEventMessage {
        RequestEventMessage::new()
    }

    fn descriptor_static(_: ::std::option::Option<RequestEventMessage>) -> &'static ::protobuf::reflect::MessageDescriptor {
        static mut descriptor: ::protobuf::lazy::Lazy<::protobuf::reflect::MessageDescriptor> = ::protobuf::lazy::Lazy {
            lock: ::protobuf::lazy::ONCE_INIT,
            ptr: 0 as *const ::protobuf::reflect::MessageDescriptor,
        };
        unsafe {
            descriptor.get(|| {
                let mut fields = ::std::vec::Vec::new();
                fields.push(::protobuf::reflect::accessor::make_simple_field_accessor::<_, ::protobuf::types::ProtobufTypeUint64>(
                    "start_timestamp_ms_utc",
                    RequestEventMessage::get_start_timestamp_ms_utc_for_reflect,
                    RequestEventMessage::mut_start_timestamp_ms_utc_for_reflect,
                ));
                fields.push(::protobuf::reflect::accessor::make_simple_field_accessor::<_, ::protobuf::types::ProtobufTypeUint64>(
                    "end_timestamp_ms_utc",
                    RequestEventMessage::get_end_timestamp_ms_utc_for_reflect,
                    RequestEventMessage::mut_end_timestamp_ms_utc_for_reflect,
                ));
                fields.push(::protobuf::reflect::accessor::make_simple_field_accessor::<_, ::protobuf::types::ProtobufTypeInt32>(
                    "box_ids",
                    RequestEventMessage::get_box_ids_for_reflect,
                    RequestEventMessage::mut_box_ids_for_reflect,
                ));
                fields.push(::protobuf::reflect::accessor::make_simple_field_accessor::<_, ::protobuf::types::ProtobufTypeString>(
                    "requestee",
                    RequestEventMessage::get_requestee_for_reflect,
                    RequestEventMessage::mut_requestee_for_reflect,
                ));
                fields.push(::protobuf::reflect::accessor::make_simple_field_accessor::<_, ::protobuf::types::ProtobufTypeString>(
                    "description",
                    RequestEventMessage::get_description_for_reflect,
                    RequestEventMessage::mut_description_for_reflect,
                ));
                fields.push(::protobuf::reflect::accessor::make_simple_field_accessor::<_, ::protobuf::types::ProtobufTypeBool>(
                    "request_data",
                    RequestEventMessage::get_request_data_for_reflect,
                    RequestEventMessage::mut_request_data_for_reflect,
                ));
                ::protobuf::reflect::MessageDescriptor::new::<RequestEventMessage>(
                    "RequestEventMessage",
                    fields,
                    file_descriptor_proto()
                )
            })
        }
    }
}

impl ::protobuf::Clear for RequestEventMessage {
    fn clear(&mut self) {
        self.clear_start_timestamp_ms_utc();
        self.clear_end_timestamp_ms_utc();
        self.clear_box_ids();
        self.clear_requestee();
        self.clear_description();
        self.clear_request_data();
        self.unknown_fields.clear();
    }
}

impl ::std::fmt::Debug for RequestEventMessage {
    fn fmt(&self, f: &mut ::std::fmt::Formatter) -> ::std::fmt::Result {
        ::protobuf::text_format::fmt(self, f)
    }
}

impl ::protobuf::reflect::ProtobufValue for RequestEventMessage {
    fn as_ref(&self) -> ::protobuf::reflect::ProtobufValueRef {
        ::protobuf::reflect::ProtobufValueRef::Message(self)
    }
}

static file_descriptor_proto_data: &'static [u8] = b"\
    \n\x0bmakai.proto\x12\topq.makai\x1a\x0frustproto.proto\"\xf7\x01\n\x13R\
    equestEventMessage\x123\n\x16start_timestamp_ms_utc\x18\x01\x20\x01(\x04\
    R\x13startTimestampMsUtc\x12/\n\x14end_timestamp_ms_utc\x18\x02\x20\x01(\
    \x04R\x11endTimestampMsUtc\x12\x17\n\x07box_ids\x18\x03\x20\x01(\x05R\
    \x06boxIds\x12\x1c\n\trequestee\x18\x04\x20\x01(\tR\trequestee\x12\x20\n\
    \x0bdescription\x18\x05\x20\x01(\tR\x0bdescription\x12!\n\x0crequest_dat\
    a\x18\x06\x20\x01(\x08R\x0brequestDatab\x06proto3\
";

static mut file_descriptor_proto_lazy: ::protobuf::lazy::Lazy<::protobuf::descriptor::FileDescriptorProto> = ::protobuf::lazy::Lazy {
    lock: ::protobuf::lazy::ONCE_INIT,
    ptr: 0 as *const ::protobuf::descriptor::FileDescriptorProto,
};

fn parse_descriptor_proto() -> ::protobuf::descriptor::FileDescriptorProto {
    ::protobuf::parse_from_bytes(file_descriptor_proto_data).unwrap()
}

pub fn file_descriptor_proto() -> &'static ::protobuf::descriptor::FileDescriptorProto {
    unsafe {
        file_descriptor_proto_lazy.get(|| {
            parse_descriptor_proto()
        })
    }
}
