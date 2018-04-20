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
pub struct Cycle {
    // message fields
    time: ::std::option::Option<u64>,
    data: ::std::vec::Vec<i32>,
    last_gps: ::std::option::Option<i32>,
    current_count: ::std::option::Option<i32>,
    flags: ::std::option::Option<i32>,
    // special fields
    unknown_fields: ::protobuf::UnknownFields,
    cached_size: ::protobuf::CachedSize,
}

// see codegen.rs for the explanation why impl Sync explicitly
unsafe impl ::std::marker::Sync for Cycle {}

impl Cycle {
    pub fn new() -> Cycle {
        ::std::default::Default::default()
    }

    pub fn default_instance() -> &'static Cycle {
        static mut instance: ::protobuf::lazy::Lazy<Cycle> = ::protobuf::lazy::Lazy {
            lock: ::protobuf::lazy::ONCE_INIT,
            ptr: 0 as *const Cycle,
        };
        unsafe {
            instance.get(Cycle::new)
        }
    }

    // required uint64 time = 1;

    pub fn clear_time(&mut self) {
        self.time = ::std::option::Option::None;
    }

    pub fn has_time(&self) -> bool {
        self.time.is_some()
    }

    // Param is passed by value, moved
    pub fn set_time(&mut self, v: u64) {
        self.time = ::std::option::Option::Some(v);
    }

    pub fn get_time(&self) -> u64 {
        self.time.unwrap_or(0)
    }

    fn get_time_for_reflect(&self) -> &::std::option::Option<u64> {
        &self.time
    }

    fn mut_time_for_reflect(&mut self) -> &mut ::std::option::Option<u64> {
        &mut self.time
    }

    // repeated int32 data = 2;

    pub fn clear_data(&mut self) {
        self.data.clear();
    }

    // Param is passed by value, moved
    pub fn set_data(&mut self, v: ::std::vec::Vec<i32>) {
        self.data = v;
    }

    // Mutable pointer to the field.
    pub fn mut_data(&mut self) -> &mut ::std::vec::Vec<i32> {
        &mut self.data
    }

    // Take field
    pub fn take_data(&mut self) -> ::std::vec::Vec<i32> {
        ::std::mem::replace(&mut self.data, ::std::vec::Vec::new())
    }

    pub fn get_data(&self) -> &[i32] {
        &self.data
    }

    fn get_data_for_reflect(&self) -> &::std::vec::Vec<i32> {
        &self.data
    }

    fn mut_data_for_reflect(&mut self) -> &mut ::std::vec::Vec<i32> {
        &mut self.data
    }

    // optional int32 last_gps = 3;

    pub fn clear_last_gps(&mut self) {
        self.last_gps = ::std::option::Option::None;
    }

    pub fn has_last_gps(&self) -> bool {
        self.last_gps.is_some()
    }

    // Param is passed by value, moved
    pub fn set_last_gps(&mut self, v: i32) {
        self.last_gps = ::std::option::Option::Some(v);
    }

    pub fn get_last_gps(&self) -> i32 {
        self.last_gps.unwrap_or(0)
    }

    fn get_last_gps_for_reflect(&self) -> &::std::option::Option<i32> {
        &self.last_gps
    }

    fn mut_last_gps_for_reflect(&mut self) -> &mut ::std::option::Option<i32> {
        &mut self.last_gps
    }

    // optional int32 current_count = 4;

    pub fn clear_current_count(&mut self) {
        self.current_count = ::std::option::Option::None;
    }

    pub fn has_current_count(&self) -> bool {
        self.current_count.is_some()
    }

    // Param is passed by value, moved
    pub fn set_current_count(&mut self, v: i32) {
        self.current_count = ::std::option::Option::Some(v);
    }

    pub fn get_current_count(&self) -> i32 {
        self.current_count.unwrap_or(0)
    }

    fn get_current_count_for_reflect(&self) -> &::std::option::Option<i32> {
        &self.current_count
    }

    fn mut_current_count_for_reflect(&mut self) -> &mut ::std::option::Option<i32> {
        &mut self.current_count
    }

    // optional int32 flags = 5;

    pub fn clear_flags(&mut self) {
        self.flags = ::std::option::Option::None;
    }

    pub fn has_flags(&self) -> bool {
        self.flags.is_some()
    }

    // Param is passed by value, moved
    pub fn set_flags(&mut self, v: i32) {
        self.flags = ::std::option::Option::Some(v);
    }

    pub fn get_flags(&self) -> i32 {
        self.flags.unwrap_or(0)
    }

    fn get_flags_for_reflect(&self) -> &::std::option::Option<i32> {
        &self.flags
    }

    fn mut_flags_for_reflect(&mut self) -> &mut ::std::option::Option<i32> {
        &mut self.flags
    }
}

impl ::protobuf::Message for Cycle {
    fn is_initialized(&self) -> bool {
        if self.time.is_none() {
            return false;
        }
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
                    self.time = ::std::option::Option::Some(tmp);
                },
                2 => {
                    ::protobuf::rt::read_repeated_int32_into(wire_type, is, &mut self.data)?;
                },
                3 => {
                    if wire_type != ::protobuf::wire_format::WireTypeVarint {
                        return ::std::result::Result::Err(::protobuf::rt::unexpected_wire_type(wire_type));
                    }
                    let tmp = is.read_int32()?;
                    self.last_gps = ::std::option::Option::Some(tmp);
                },
                4 => {
                    if wire_type != ::protobuf::wire_format::WireTypeVarint {
                        return ::std::result::Result::Err(::protobuf::rt::unexpected_wire_type(wire_type));
                    }
                    let tmp = is.read_int32()?;
                    self.current_count = ::std::option::Option::Some(tmp);
                },
                5 => {
                    if wire_type != ::protobuf::wire_format::WireTypeVarint {
                        return ::std::result::Result::Err(::protobuf::rt::unexpected_wire_type(wire_type));
                    }
                    let tmp = is.read_int32()?;
                    self.flags = ::std::option::Option::Some(tmp);
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
        if let Some(v) = self.time {
            my_size += ::protobuf::rt::value_size(1, v, ::protobuf::wire_format::WireTypeVarint);
        }
        for value in &self.data {
            my_size += ::protobuf::rt::value_size(2, *value, ::protobuf::wire_format::WireTypeVarint);
        };
        if let Some(v) = self.last_gps {
            my_size += ::protobuf::rt::value_size(3, v, ::protobuf::wire_format::WireTypeVarint);
        }
        if let Some(v) = self.current_count {
            my_size += ::protobuf::rt::value_size(4, v, ::protobuf::wire_format::WireTypeVarint);
        }
        if let Some(v) = self.flags {
            my_size += ::protobuf::rt::value_size(5, v, ::protobuf::wire_format::WireTypeVarint);
        }
        my_size += ::protobuf::rt::unknown_fields_size(self.get_unknown_fields());
        self.cached_size.set(my_size);
        my_size
    }

    fn write_to_with_cached_sizes(&self, os: &mut ::protobuf::CodedOutputStream) -> ::protobuf::ProtobufResult<()> {
        if let Some(v) = self.time {
            os.write_uint64(1, v)?;
        }
        for v in &self.data {
            os.write_int32(2, *v)?;
        };
        if let Some(v) = self.last_gps {
            os.write_int32(3, v)?;
        }
        if let Some(v) = self.current_count {
            os.write_int32(4, v)?;
        }
        if let Some(v) = self.flags {
            os.write_int32(5, v)?;
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

impl ::protobuf::MessageStatic for Cycle {
    fn new() -> Cycle {
        Cycle::new()
    }

    fn descriptor_static(_: ::std::option::Option<Cycle>) -> &'static ::protobuf::reflect::MessageDescriptor {
        static mut descriptor: ::protobuf::lazy::Lazy<::protobuf::reflect::MessageDescriptor> = ::protobuf::lazy::Lazy {
            lock: ::protobuf::lazy::ONCE_INIT,
            ptr: 0 as *const ::protobuf::reflect::MessageDescriptor,
        };
        unsafe {
            descriptor.get(|| {
                let mut fields = ::std::vec::Vec::new();
                fields.push(::protobuf::reflect::accessor::make_option_accessor::<_, ::protobuf::types::ProtobufTypeUint64>(
                    "time",
                    Cycle::get_time_for_reflect,
                    Cycle::mut_time_for_reflect,
                ));
                fields.push(::protobuf::reflect::accessor::make_vec_accessor::<_, ::protobuf::types::ProtobufTypeInt32>(
                    "data",
                    Cycle::get_data_for_reflect,
                    Cycle::mut_data_for_reflect,
                ));
                fields.push(::protobuf::reflect::accessor::make_option_accessor::<_, ::protobuf::types::ProtobufTypeInt32>(
                    "last_gps",
                    Cycle::get_last_gps_for_reflect,
                    Cycle::mut_last_gps_for_reflect,
                ));
                fields.push(::protobuf::reflect::accessor::make_option_accessor::<_, ::protobuf::types::ProtobufTypeInt32>(
                    "current_count",
                    Cycle::get_current_count_for_reflect,
                    Cycle::mut_current_count_for_reflect,
                ));
                fields.push(::protobuf::reflect::accessor::make_option_accessor::<_, ::protobuf::types::ProtobufTypeInt32>(
                    "flags",
                    Cycle::get_flags_for_reflect,
                    Cycle::mut_flags_for_reflect,
                ));
                ::protobuf::reflect::MessageDescriptor::new::<Cycle>(
                    "Cycle",
                    fields,
                    file_descriptor_proto()
                )
            })
        }
    }
}

impl ::protobuf::Clear for Cycle {
    fn clear(&mut self) {
        self.clear_time();
        self.clear_data();
        self.clear_last_gps();
        self.clear_current_count();
        self.clear_flags();
        self.unknown_fields.clear();
    }
}

impl ::std::fmt::Debug for Cycle {
    fn fmt(&self, f: &mut ::std::fmt::Formatter) -> ::std::fmt::Result {
        ::protobuf::text_format::fmt(self, f)
    }
}

impl ::protobuf::reflect::ProtobufValue for Cycle {
    fn as_ref(&self) -> ::protobuf::reflect::ProtobufValueRef {
        ::protobuf::reflect::ProtobufValueRef::Message(self)
    }
}

#[derive(PartialEq,Clone,Default)]
pub struct DataMessage {
    // message fields
    id: ::std::option::Option<i32>,
    cycles: ::protobuf::RepeatedField<Cycle>,
    // special fields
    unknown_fields: ::protobuf::UnknownFields,
    cached_size: ::protobuf::CachedSize,
}

// see codegen.rs for the explanation why impl Sync explicitly
unsafe impl ::std::marker::Sync for DataMessage {}

impl DataMessage {
    pub fn new() -> DataMessage {
        ::std::default::Default::default()
    }

    pub fn default_instance() -> &'static DataMessage {
        static mut instance: ::protobuf::lazy::Lazy<DataMessage> = ::protobuf::lazy::Lazy {
            lock: ::protobuf::lazy::ONCE_INIT,
            ptr: 0 as *const DataMessage,
        };
        unsafe {
            instance.get(DataMessage::new)
        }
    }

    // required int32 id = 1;

    pub fn clear_id(&mut self) {
        self.id = ::std::option::Option::None;
    }

    pub fn has_id(&self) -> bool {
        self.id.is_some()
    }

    // Param is passed by value, moved
    pub fn set_id(&mut self, v: i32) {
        self.id = ::std::option::Option::Some(v);
    }

    pub fn get_id(&self) -> i32 {
        self.id.unwrap_or(0)
    }

    fn get_id_for_reflect(&self) -> &::std::option::Option<i32> {
        &self.id
    }

    fn mut_id_for_reflect(&mut self) -> &mut ::std::option::Option<i32> {
        &mut self.id
    }

    // repeated .opq.proto.Cycle cycles = 3;

    pub fn clear_cycles(&mut self) {
        self.cycles.clear();
    }

    // Param is passed by value, moved
    pub fn set_cycles(&mut self, v: ::protobuf::RepeatedField<Cycle>) {
        self.cycles = v;
    }

    // Mutable pointer to the field.
    pub fn mut_cycles(&mut self) -> &mut ::protobuf::RepeatedField<Cycle> {
        &mut self.cycles
    }

    // Take field
    pub fn take_cycles(&mut self) -> ::protobuf::RepeatedField<Cycle> {
        ::std::mem::replace(&mut self.cycles, ::protobuf::RepeatedField::new())
    }

    pub fn get_cycles(&self) -> &[Cycle] {
        &self.cycles
    }

    fn get_cycles_for_reflect(&self) -> &::protobuf::RepeatedField<Cycle> {
        &self.cycles
    }

    fn mut_cycles_for_reflect(&mut self) -> &mut ::protobuf::RepeatedField<Cycle> {
        &mut self.cycles
    }
}

impl ::protobuf::Message for DataMessage {
    fn is_initialized(&self) -> bool {
        if self.id.is_none() {
            return false;
        }
        for v in &self.cycles {
            if !v.is_initialized() {
                return false;
            }
        };
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
                    let tmp = is.read_int32()?;
                    self.id = ::std::option::Option::Some(tmp);
                },
                3 => {
                    ::protobuf::rt::read_repeated_message_into(wire_type, is, &mut self.cycles)?;
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
        if let Some(v) = self.id {
            my_size += ::protobuf::rt::value_size(1, v, ::protobuf::wire_format::WireTypeVarint);
        }
        for value in &self.cycles {
            let len = value.compute_size();
            my_size += 1 + ::protobuf::rt::compute_raw_varint32_size(len) + len;
        };
        my_size += ::protobuf::rt::unknown_fields_size(self.get_unknown_fields());
        self.cached_size.set(my_size);
        my_size
    }

    fn write_to_with_cached_sizes(&self, os: &mut ::protobuf::CodedOutputStream) -> ::protobuf::ProtobufResult<()> {
        if let Some(v) = self.id {
            os.write_int32(1, v)?;
        }
        for v in &self.cycles {
            os.write_tag(3, ::protobuf::wire_format::WireTypeLengthDelimited)?;
            os.write_raw_varint32(v.get_cached_size())?;
            v.write_to_with_cached_sizes(os)?;
        };
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

impl ::protobuf::MessageStatic for DataMessage {
    fn new() -> DataMessage {
        DataMessage::new()
    }

    fn descriptor_static(_: ::std::option::Option<DataMessage>) -> &'static ::protobuf::reflect::MessageDescriptor {
        static mut descriptor: ::protobuf::lazy::Lazy<::protobuf::reflect::MessageDescriptor> = ::protobuf::lazy::Lazy {
            lock: ::protobuf::lazy::ONCE_INIT,
            ptr: 0 as *const ::protobuf::reflect::MessageDescriptor,
        };
        unsafe {
            descriptor.get(|| {
                let mut fields = ::std::vec::Vec::new();
                fields.push(::protobuf::reflect::accessor::make_option_accessor::<_, ::protobuf::types::ProtobufTypeInt32>(
                    "id",
                    DataMessage::get_id_for_reflect,
                    DataMessage::mut_id_for_reflect,
                ));
                fields.push(::protobuf::reflect::accessor::make_repeated_field_accessor::<_, ::protobuf::types::ProtobufTypeMessage<Cycle>>(
                    "cycles",
                    DataMessage::get_cycles_for_reflect,
                    DataMessage::mut_cycles_for_reflect,
                ));
                ::protobuf::reflect::MessageDescriptor::new::<DataMessage>(
                    "DataMessage",
                    fields,
                    file_descriptor_proto()
                )
            })
        }
    }
}

impl ::protobuf::Clear for DataMessage {
    fn clear(&mut self) {
        self.clear_id();
        self.clear_cycles();
        self.unknown_fields.clear();
    }
}

impl ::std::fmt::Debug for DataMessage {
    fn fmt(&self, f: &mut ::std::fmt::Formatter) -> ::std::fmt::Result {
        ::protobuf::text_format::fmt(self, f)
    }
}

impl ::protobuf::reflect::ProtobufValue for DataMessage {
    fn as_ref(&self) -> ::protobuf::reflect::ProtobufValueRef {
        ::protobuf::reflect::ProtobufValueRef::Message(self)
    }
}

#[derive(PartialEq,Clone,Default)]
pub struct TriggerMessage {
    // message fields
    id: ::std::option::Option<i32>,
    time: ::std::option::Option<u64>,
    frequency: ::std::option::Option<f32>,
    rms: ::std::option::Option<f32>,
    thd: ::std::option::Option<f32>,
    last_gps: ::std::option::Option<i32>,
    current_count: ::std::option::Option<i32>,
    flags: ::std::option::Option<i32>,
    // special fields
    unknown_fields: ::protobuf::UnknownFields,
    cached_size: ::protobuf::CachedSize,
}

// see codegen.rs for the explanation why impl Sync explicitly
unsafe impl ::std::marker::Sync for TriggerMessage {}

impl TriggerMessage {
    pub fn new() -> TriggerMessage {
        ::std::default::Default::default()
    }

    pub fn default_instance() -> &'static TriggerMessage {
        static mut instance: ::protobuf::lazy::Lazy<TriggerMessage> = ::protobuf::lazy::Lazy {
            lock: ::protobuf::lazy::ONCE_INIT,
            ptr: 0 as *const TriggerMessage,
        };
        unsafe {
            instance.get(TriggerMessage::new)
        }
    }

    // required int32 id = 1;

    pub fn clear_id(&mut self) {
        self.id = ::std::option::Option::None;
    }

    pub fn has_id(&self) -> bool {
        self.id.is_some()
    }

    // Param is passed by value, moved
    pub fn set_id(&mut self, v: i32) {
        self.id = ::std::option::Option::Some(v);
    }

    pub fn get_id(&self) -> i32 {
        self.id.unwrap_or(0)
    }

    fn get_id_for_reflect(&self) -> &::std::option::Option<i32> {
        &self.id
    }

    fn mut_id_for_reflect(&mut self) -> &mut ::std::option::Option<i32> {
        &mut self.id
    }

    // required uint64 time = 2;

    pub fn clear_time(&mut self) {
        self.time = ::std::option::Option::None;
    }

    pub fn has_time(&self) -> bool {
        self.time.is_some()
    }

    // Param is passed by value, moved
    pub fn set_time(&mut self, v: u64) {
        self.time = ::std::option::Option::Some(v);
    }

    pub fn get_time(&self) -> u64 {
        self.time.unwrap_or(0)
    }

    fn get_time_for_reflect(&self) -> &::std::option::Option<u64> {
        &self.time
    }

    fn mut_time_for_reflect(&mut self) -> &mut ::std::option::Option<u64> {
        &mut self.time
    }

    // required float frequency = 3;

    pub fn clear_frequency(&mut self) {
        self.frequency = ::std::option::Option::None;
    }

    pub fn has_frequency(&self) -> bool {
        self.frequency.is_some()
    }

    // Param is passed by value, moved
    pub fn set_frequency(&mut self, v: f32) {
        self.frequency = ::std::option::Option::Some(v);
    }

    pub fn get_frequency(&self) -> f32 {
        self.frequency.unwrap_or(0.)
    }

    fn get_frequency_for_reflect(&self) -> &::std::option::Option<f32> {
        &self.frequency
    }

    fn mut_frequency_for_reflect(&mut self) -> &mut ::std::option::Option<f32> {
        &mut self.frequency
    }

    // required float rms = 4;

    pub fn clear_rms(&mut self) {
        self.rms = ::std::option::Option::None;
    }

    pub fn has_rms(&self) -> bool {
        self.rms.is_some()
    }

    // Param is passed by value, moved
    pub fn set_rms(&mut self, v: f32) {
        self.rms = ::std::option::Option::Some(v);
    }

    pub fn get_rms(&self) -> f32 {
        self.rms.unwrap_or(0.)
    }

    fn get_rms_for_reflect(&self) -> &::std::option::Option<f32> {
        &self.rms
    }

    fn mut_rms_for_reflect(&mut self) -> &mut ::std::option::Option<f32> {
        &mut self.rms
    }

    // optional float thd = 5;

    pub fn clear_thd(&mut self) {
        self.thd = ::std::option::Option::None;
    }

    pub fn has_thd(&self) -> bool {
        self.thd.is_some()
    }

    // Param is passed by value, moved
    pub fn set_thd(&mut self, v: f32) {
        self.thd = ::std::option::Option::Some(v);
    }

    pub fn get_thd(&self) -> f32 {
        self.thd.unwrap_or(0.)
    }

    fn get_thd_for_reflect(&self) -> &::std::option::Option<f32> {
        &self.thd
    }

    fn mut_thd_for_reflect(&mut self) -> &mut ::std::option::Option<f32> {
        &mut self.thd
    }

    // optional int32 last_gps = 6;

    pub fn clear_last_gps(&mut self) {
        self.last_gps = ::std::option::Option::None;
    }

    pub fn has_last_gps(&self) -> bool {
        self.last_gps.is_some()
    }

    // Param is passed by value, moved
    pub fn set_last_gps(&mut self, v: i32) {
        self.last_gps = ::std::option::Option::Some(v);
    }

    pub fn get_last_gps(&self) -> i32 {
        self.last_gps.unwrap_or(0)
    }

    fn get_last_gps_for_reflect(&self) -> &::std::option::Option<i32> {
        &self.last_gps
    }

    fn mut_last_gps_for_reflect(&mut self) -> &mut ::std::option::Option<i32> {
        &mut self.last_gps
    }

    // optional int32 current_count = 7;

    pub fn clear_current_count(&mut self) {
        self.current_count = ::std::option::Option::None;
    }

    pub fn has_current_count(&self) -> bool {
        self.current_count.is_some()
    }

    // Param is passed by value, moved
    pub fn set_current_count(&mut self, v: i32) {
        self.current_count = ::std::option::Option::Some(v);
    }

    pub fn get_current_count(&self) -> i32 {
        self.current_count.unwrap_or(0)
    }

    fn get_current_count_for_reflect(&self) -> &::std::option::Option<i32> {
        &self.current_count
    }

    fn mut_current_count_for_reflect(&mut self) -> &mut ::std::option::Option<i32> {
        &mut self.current_count
    }

    // optional int32 flags = 8;

    pub fn clear_flags(&mut self) {
        self.flags = ::std::option::Option::None;
    }

    pub fn has_flags(&self) -> bool {
        self.flags.is_some()
    }

    // Param is passed by value, moved
    pub fn set_flags(&mut self, v: i32) {
        self.flags = ::std::option::Option::Some(v);
    }

    pub fn get_flags(&self) -> i32 {
        self.flags.unwrap_or(0)
    }

    fn get_flags_for_reflect(&self) -> &::std::option::Option<i32> {
        &self.flags
    }

    fn mut_flags_for_reflect(&mut self) -> &mut ::std::option::Option<i32> {
        &mut self.flags
    }
}

impl ::protobuf::Message for TriggerMessage {
    fn is_initialized(&self) -> bool {
        if self.id.is_none() {
            return false;
        }
        if self.time.is_none() {
            return false;
        }
        if self.frequency.is_none() {
            return false;
        }
        if self.rms.is_none() {
            return false;
        }
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
                    let tmp = is.read_int32()?;
                    self.id = ::std::option::Option::Some(tmp);
                },
                2 => {
                    if wire_type != ::protobuf::wire_format::WireTypeVarint {
                        return ::std::result::Result::Err(::protobuf::rt::unexpected_wire_type(wire_type));
                    }
                    let tmp = is.read_uint64()?;
                    self.time = ::std::option::Option::Some(tmp);
                },
                3 => {
                    if wire_type != ::protobuf::wire_format::WireTypeFixed32 {
                        return ::std::result::Result::Err(::protobuf::rt::unexpected_wire_type(wire_type));
                    }
                    let tmp = is.read_float()?;
                    self.frequency = ::std::option::Option::Some(tmp);
                },
                4 => {
                    if wire_type != ::protobuf::wire_format::WireTypeFixed32 {
                        return ::std::result::Result::Err(::protobuf::rt::unexpected_wire_type(wire_type));
                    }
                    let tmp = is.read_float()?;
                    self.rms = ::std::option::Option::Some(tmp);
                },
                5 => {
                    if wire_type != ::protobuf::wire_format::WireTypeFixed32 {
                        return ::std::result::Result::Err(::protobuf::rt::unexpected_wire_type(wire_type));
                    }
                    let tmp = is.read_float()?;
                    self.thd = ::std::option::Option::Some(tmp);
                },
                6 => {
                    if wire_type != ::protobuf::wire_format::WireTypeVarint {
                        return ::std::result::Result::Err(::protobuf::rt::unexpected_wire_type(wire_type));
                    }
                    let tmp = is.read_int32()?;
                    self.last_gps = ::std::option::Option::Some(tmp);
                },
                7 => {
                    if wire_type != ::protobuf::wire_format::WireTypeVarint {
                        return ::std::result::Result::Err(::protobuf::rt::unexpected_wire_type(wire_type));
                    }
                    let tmp = is.read_int32()?;
                    self.current_count = ::std::option::Option::Some(tmp);
                },
                8 => {
                    if wire_type != ::protobuf::wire_format::WireTypeVarint {
                        return ::std::result::Result::Err(::protobuf::rt::unexpected_wire_type(wire_type));
                    }
                    let tmp = is.read_int32()?;
                    self.flags = ::std::option::Option::Some(tmp);
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
        if let Some(v) = self.id {
            my_size += ::protobuf::rt::value_size(1, v, ::protobuf::wire_format::WireTypeVarint);
        }
        if let Some(v) = self.time {
            my_size += ::protobuf::rt::value_size(2, v, ::protobuf::wire_format::WireTypeVarint);
        }
        if let Some(v) = self.frequency {
            my_size += 5;
        }
        if let Some(v) = self.rms {
            my_size += 5;
        }
        if let Some(v) = self.thd {
            my_size += 5;
        }
        if let Some(v) = self.last_gps {
            my_size += ::protobuf::rt::value_size(6, v, ::protobuf::wire_format::WireTypeVarint);
        }
        if let Some(v) = self.current_count {
            my_size += ::protobuf::rt::value_size(7, v, ::protobuf::wire_format::WireTypeVarint);
        }
        if let Some(v) = self.flags {
            my_size += ::protobuf::rt::value_size(8, v, ::protobuf::wire_format::WireTypeVarint);
        }
        my_size += ::protobuf::rt::unknown_fields_size(self.get_unknown_fields());
        self.cached_size.set(my_size);
        my_size
    }

    fn write_to_with_cached_sizes(&self, os: &mut ::protobuf::CodedOutputStream) -> ::protobuf::ProtobufResult<()> {
        if let Some(v) = self.id {
            os.write_int32(1, v)?;
        }
        if let Some(v) = self.time {
            os.write_uint64(2, v)?;
        }
        if let Some(v) = self.frequency {
            os.write_float(3, v)?;
        }
        if let Some(v) = self.rms {
            os.write_float(4, v)?;
        }
        if let Some(v) = self.thd {
            os.write_float(5, v)?;
        }
        if let Some(v) = self.last_gps {
            os.write_int32(6, v)?;
        }
        if let Some(v) = self.current_count {
            os.write_int32(7, v)?;
        }
        if let Some(v) = self.flags {
            os.write_int32(8, v)?;
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

impl ::protobuf::MessageStatic for TriggerMessage {
    fn new() -> TriggerMessage {
        TriggerMessage::new()
    }

    fn descriptor_static(_: ::std::option::Option<TriggerMessage>) -> &'static ::protobuf::reflect::MessageDescriptor {
        static mut descriptor: ::protobuf::lazy::Lazy<::protobuf::reflect::MessageDescriptor> = ::protobuf::lazy::Lazy {
            lock: ::protobuf::lazy::ONCE_INIT,
            ptr: 0 as *const ::protobuf::reflect::MessageDescriptor,
        };
        unsafe {
            descriptor.get(|| {
                let mut fields = ::std::vec::Vec::new();
                fields.push(::protobuf::reflect::accessor::make_option_accessor::<_, ::protobuf::types::ProtobufTypeInt32>(
                    "id",
                    TriggerMessage::get_id_for_reflect,
                    TriggerMessage::mut_id_for_reflect,
                ));
                fields.push(::protobuf::reflect::accessor::make_option_accessor::<_, ::protobuf::types::ProtobufTypeUint64>(
                    "time",
                    TriggerMessage::get_time_for_reflect,
                    TriggerMessage::mut_time_for_reflect,
                ));
                fields.push(::protobuf::reflect::accessor::make_option_accessor::<_, ::protobuf::types::ProtobufTypeFloat>(
                    "frequency",
                    TriggerMessage::get_frequency_for_reflect,
                    TriggerMessage::mut_frequency_for_reflect,
                ));
                fields.push(::protobuf::reflect::accessor::make_option_accessor::<_, ::protobuf::types::ProtobufTypeFloat>(
                    "rms",
                    TriggerMessage::get_rms_for_reflect,
                    TriggerMessage::mut_rms_for_reflect,
                ));
                fields.push(::protobuf::reflect::accessor::make_option_accessor::<_, ::protobuf::types::ProtobufTypeFloat>(
                    "thd",
                    TriggerMessage::get_thd_for_reflect,
                    TriggerMessage::mut_thd_for_reflect,
                ));
                fields.push(::protobuf::reflect::accessor::make_option_accessor::<_, ::protobuf::types::ProtobufTypeInt32>(
                    "last_gps",
                    TriggerMessage::get_last_gps_for_reflect,
                    TriggerMessage::mut_last_gps_for_reflect,
                ));
                fields.push(::protobuf::reflect::accessor::make_option_accessor::<_, ::protobuf::types::ProtobufTypeInt32>(
                    "current_count",
                    TriggerMessage::get_current_count_for_reflect,
                    TriggerMessage::mut_current_count_for_reflect,
                ));
                fields.push(::protobuf::reflect::accessor::make_option_accessor::<_, ::protobuf::types::ProtobufTypeInt32>(
                    "flags",
                    TriggerMessage::get_flags_for_reflect,
                    TriggerMessage::mut_flags_for_reflect,
                ));
                ::protobuf::reflect::MessageDescriptor::new::<TriggerMessage>(
                    "TriggerMessage",
                    fields,
                    file_descriptor_proto()
                )
            })
        }
    }
}

impl ::protobuf::Clear for TriggerMessage {
    fn clear(&mut self) {
        self.clear_id();
        self.clear_time();
        self.clear_frequency();
        self.clear_rms();
        self.clear_thd();
        self.clear_last_gps();
        self.clear_current_count();
        self.clear_flags();
        self.unknown_fields.clear();
    }
}

impl ::std::fmt::Debug for TriggerMessage {
    fn fmt(&self, f: &mut ::std::fmt::Formatter) -> ::std::fmt::Result {
        ::protobuf::text_format::fmt(self, f)
    }
}

impl ::protobuf::reflect::ProtobufValue for TriggerMessage {
    fn as_ref(&self) -> ::protobuf::reflect::ProtobufValueRef {
        ::protobuf::reflect::ProtobufValueRef::Message(self)
    }
}

#[derive(PartialEq,Clone,Default)]
pub struct RequestDataMessage {
    // message fields
    field_type: ::std::option::Option<RequestDataMessage_RequestType>,
    sequence_number: ::std::option::Option<u32>,
    boxId: ::std::option::Option<u32>,
    time: ::std::option::Option<u64>,
    back: ::std::option::Option<u64>,
    forward: ::std::option::Option<u64>,
    num_cycles: ::std::option::Option<u32>,
    // special fields
    unknown_fields: ::protobuf::UnknownFields,
    cached_size: ::protobuf::CachedSize,
}

// see codegen.rs for the explanation why impl Sync explicitly
unsafe impl ::std::marker::Sync for RequestDataMessage {}

impl RequestDataMessage {
    pub fn new() -> RequestDataMessage {
        ::std::default::Default::default()
    }

    pub fn default_instance() -> &'static RequestDataMessage {
        static mut instance: ::protobuf::lazy::Lazy<RequestDataMessage> = ::protobuf::lazy::Lazy {
            lock: ::protobuf::lazy::ONCE_INIT,
            ptr: 0 as *const RequestDataMessage,
        };
        unsafe {
            instance.get(RequestDataMessage::new)
        }
    }

    // required .opq.proto.RequestDataMessage.RequestType type = 1;

    pub fn clear_field_type(&mut self) {
        self.field_type = ::std::option::Option::None;
    }

    pub fn has_field_type(&self) -> bool {
        self.field_type.is_some()
    }

    // Param is passed by value, moved
    pub fn set_field_type(&mut self, v: RequestDataMessage_RequestType) {
        self.field_type = ::std::option::Option::Some(v);
    }

    pub fn get_field_type(&self) -> RequestDataMessage_RequestType {
        self.field_type.unwrap_or(RequestDataMessage_RequestType::PING)
    }

    fn get_field_type_for_reflect(&self) -> &::std::option::Option<RequestDataMessage_RequestType> {
        &self.field_type
    }

    fn mut_field_type_for_reflect(&mut self) -> &mut ::std::option::Option<RequestDataMessage_RequestType> {
        &mut self.field_type
    }

    // required uint32 sequence_number = 2;

    pub fn clear_sequence_number(&mut self) {
        self.sequence_number = ::std::option::Option::None;
    }

    pub fn has_sequence_number(&self) -> bool {
        self.sequence_number.is_some()
    }

    // Param is passed by value, moved
    pub fn set_sequence_number(&mut self, v: u32) {
        self.sequence_number = ::std::option::Option::Some(v);
    }

    pub fn get_sequence_number(&self) -> u32 {
        self.sequence_number.unwrap_or(0)
    }

    fn get_sequence_number_for_reflect(&self) -> &::std::option::Option<u32> {
        &self.sequence_number
    }

    fn mut_sequence_number_for_reflect(&mut self) -> &mut ::std::option::Option<u32> {
        &mut self.sequence_number
    }

    // optional uint32 boxId = 3;

    pub fn clear_boxId(&mut self) {
        self.boxId = ::std::option::Option::None;
    }

    pub fn has_boxId(&self) -> bool {
        self.boxId.is_some()
    }

    // Param is passed by value, moved
    pub fn set_boxId(&mut self, v: u32) {
        self.boxId = ::std::option::Option::Some(v);
    }

    pub fn get_boxId(&self) -> u32 {
        self.boxId.unwrap_or(0)
    }

    fn get_boxId_for_reflect(&self) -> &::std::option::Option<u32> {
        &self.boxId
    }

    fn mut_boxId_for_reflect(&mut self) -> &mut ::std::option::Option<u32> {
        &mut self.boxId
    }

    // optional uint64 time = 4;

    pub fn clear_time(&mut self) {
        self.time = ::std::option::Option::None;
    }

    pub fn has_time(&self) -> bool {
        self.time.is_some()
    }

    // Param is passed by value, moved
    pub fn set_time(&mut self, v: u64) {
        self.time = ::std::option::Option::Some(v);
    }

    pub fn get_time(&self) -> u64 {
        self.time.unwrap_or(0)
    }

    fn get_time_for_reflect(&self) -> &::std::option::Option<u64> {
        &self.time
    }

    fn mut_time_for_reflect(&mut self) -> &mut ::std::option::Option<u64> {
        &mut self.time
    }

    // optional uint64 back = 5;

    pub fn clear_back(&mut self) {
        self.back = ::std::option::Option::None;
    }

    pub fn has_back(&self) -> bool {
        self.back.is_some()
    }

    // Param is passed by value, moved
    pub fn set_back(&mut self, v: u64) {
        self.back = ::std::option::Option::Some(v);
    }

    pub fn get_back(&self) -> u64 {
        self.back.unwrap_or(0)
    }

    fn get_back_for_reflect(&self) -> &::std::option::Option<u64> {
        &self.back
    }

    fn mut_back_for_reflect(&mut self) -> &mut ::std::option::Option<u64> {
        &mut self.back
    }

    // optional uint64 forward = 6;

    pub fn clear_forward(&mut self) {
        self.forward = ::std::option::Option::None;
    }

    pub fn has_forward(&self) -> bool {
        self.forward.is_some()
    }

    // Param is passed by value, moved
    pub fn set_forward(&mut self, v: u64) {
        self.forward = ::std::option::Option::Some(v);
    }

    pub fn get_forward(&self) -> u64 {
        self.forward.unwrap_or(0)
    }

    fn get_forward_for_reflect(&self) -> &::std::option::Option<u64> {
        &self.forward
    }

    fn mut_forward_for_reflect(&mut self) -> &mut ::std::option::Option<u64> {
        &mut self.forward
    }

    // optional uint32 num_cycles = 7;

    pub fn clear_num_cycles(&mut self) {
        self.num_cycles = ::std::option::Option::None;
    }

    pub fn has_num_cycles(&self) -> bool {
        self.num_cycles.is_some()
    }

    // Param is passed by value, moved
    pub fn set_num_cycles(&mut self, v: u32) {
        self.num_cycles = ::std::option::Option::Some(v);
    }

    pub fn get_num_cycles(&self) -> u32 {
        self.num_cycles.unwrap_or(0)
    }

    fn get_num_cycles_for_reflect(&self) -> &::std::option::Option<u32> {
        &self.num_cycles
    }

    fn mut_num_cycles_for_reflect(&mut self) -> &mut ::std::option::Option<u32> {
        &mut self.num_cycles
    }
}

impl ::protobuf::Message for RequestDataMessage {
    fn is_initialized(&self) -> bool {
        if self.field_type.is_none() {
            return false;
        }
        if self.sequence_number.is_none() {
            return false;
        }
        true
    }

    fn merge_from(&mut self, is: &mut ::protobuf::CodedInputStream) -> ::protobuf::ProtobufResult<()> {
        while !is.eof()? {
            let (field_number, wire_type) = is.read_tag_unpack()?;
            match field_number {
                1 => {
                    ::protobuf::rt::read_proto2_enum_with_unknown_fields_into(wire_type, is, &mut self.field_type, 1, &mut self.unknown_fields)?
                },
                2 => {
                    if wire_type != ::protobuf::wire_format::WireTypeVarint {
                        return ::std::result::Result::Err(::protobuf::rt::unexpected_wire_type(wire_type));
                    }
                    let tmp = is.read_uint32()?;
                    self.sequence_number = ::std::option::Option::Some(tmp);
                },
                3 => {
                    if wire_type != ::protobuf::wire_format::WireTypeVarint {
                        return ::std::result::Result::Err(::protobuf::rt::unexpected_wire_type(wire_type));
                    }
                    let tmp = is.read_uint32()?;
                    self.boxId = ::std::option::Option::Some(tmp);
                },
                4 => {
                    if wire_type != ::protobuf::wire_format::WireTypeVarint {
                        return ::std::result::Result::Err(::protobuf::rt::unexpected_wire_type(wire_type));
                    }
                    let tmp = is.read_uint64()?;
                    self.time = ::std::option::Option::Some(tmp);
                },
                5 => {
                    if wire_type != ::protobuf::wire_format::WireTypeVarint {
                        return ::std::result::Result::Err(::protobuf::rt::unexpected_wire_type(wire_type));
                    }
                    let tmp = is.read_uint64()?;
                    self.back = ::std::option::Option::Some(tmp);
                },
                6 => {
                    if wire_type != ::protobuf::wire_format::WireTypeVarint {
                        return ::std::result::Result::Err(::protobuf::rt::unexpected_wire_type(wire_type));
                    }
                    let tmp = is.read_uint64()?;
                    self.forward = ::std::option::Option::Some(tmp);
                },
                7 => {
                    if wire_type != ::protobuf::wire_format::WireTypeVarint {
                        return ::std::result::Result::Err(::protobuf::rt::unexpected_wire_type(wire_type));
                    }
                    let tmp = is.read_uint32()?;
                    self.num_cycles = ::std::option::Option::Some(tmp);
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
        if let Some(v) = self.field_type {
            my_size += ::protobuf::rt::enum_size(1, v);
        }
        if let Some(v) = self.sequence_number {
            my_size += ::protobuf::rt::value_size(2, v, ::protobuf::wire_format::WireTypeVarint);
        }
        if let Some(v) = self.boxId {
            my_size += ::protobuf::rt::value_size(3, v, ::protobuf::wire_format::WireTypeVarint);
        }
        if let Some(v) = self.time {
            my_size += ::protobuf::rt::value_size(4, v, ::protobuf::wire_format::WireTypeVarint);
        }
        if let Some(v) = self.back {
            my_size += ::protobuf::rt::value_size(5, v, ::protobuf::wire_format::WireTypeVarint);
        }
        if let Some(v) = self.forward {
            my_size += ::protobuf::rt::value_size(6, v, ::protobuf::wire_format::WireTypeVarint);
        }
        if let Some(v) = self.num_cycles {
            my_size += ::protobuf::rt::value_size(7, v, ::protobuf::wire_format::WireTypeVarint);
        }
        my_size += ::protobuf::rt::unknown_fields_size(self.get_unknown_fields());
        self.cached_size.set(my_size);
        my_size
    }

    fn write_to_with_cached_sizes(&self, os: &mut ::protobuf::CodedOutputStream) -> ::protobuf::ProtobufResult<()> {
        if let Some(v) = self.field_type {
            os.write_enum(1, v.value())?;
        }
        if let Some(v) = self.sequence_number {
            os.write_uint32(2, v)?;
        }
        if let Some(v) = self.boxId {
            os.write_uint32(3, v)?;
        }
        if let Some(v) = self.time {
            os.write_uint64(4, v)?;
        }
        if let Some(v) = self.back {
            os.write_uint64(5, v)?;
        }
        if let Some(v) = self.forward {
            os.write_uint64(6, v)?;
        }
        if let Some(v) = self.num_cycles {
            os.write_uint32(7, v)?;
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

impl ::protobuf::MessageStatic for RequestDataMessage {
    fn new() -> RequestDataMessage {
        RequestDataMessage::new()
    }

    fn descriptor_static(_: ::std::option::Option<RequestDataMessage>) -> &'static ::protobuf::reflect::MessageDescriptor {
        static mut descriptor: ::protobuf::lazy::Lazy<::protobuf::reflect::MessageDescriptor> = ::protobuf::lazy::Lazy {
            lock: ::protobuf::lazy::ONCE_INIT,
            ptr: 0 as *const ::protobuf::reflect::MessageDescriptor,
        };
        unsafe {
            descriptor.get(|| {
                let mut fields = ::std::vec::Vec::new();
                fields.push(::protobuf::reflect::accessor::make_option_accessor::<_, ::protobuf::types::ProtobufTypeEnum<RequestDataMessage_RequestType>>(
                    "type",
                    RequestDataMessage::get_field_type_for_reflect,
                    RequestDataMessage::mut_field_type_for_reflect,
                ));
                fields.push(::protobuf::reflect::accessor::make_option_accessor::<_, ::protobuf::types::ProtobufTypeUint32>(
                    "sequence_number",
                    RequestDataMessage::get_sequence_number_for_reflect,
                    RequestDataMessage::mut_sequence_number_for_reflect,
                ));
                fields.push(::protobuf::reflect::accessor::make_option_accessor::<_, ::protobuf::types::ProtobufTypeUint32>(
                    "boxId",
                    RequestDataMessage::get_boxId_for_reflect,
                    RequestDataMessage::mut_boxId_for_reflect,
                ));
                fields.push(::protobuf::reflect::accessor::make_option_accessor::<_, ::protobuf::types::ProtobufTypeUint64>(
                    "time",
                    RequestDataMessage::get_time_for_reflect,
                    RequestDataMessage::mut_time_for_reflect,
                ));
                fields.push(::protobuf::reflect::accessor::make_option_accessor::<_, ::protobuf::types::ProtobufTypeUint64>(
                    "back",
                    RequestDataMessage::get_back_for_reflect,
                    RequestDataMessage::mut_back_for_reflect,
                ));
                fields.push(::protobuf::reflect::accessor::make_option_accessor::<_, ::protobuf::types::ProtobufTypeUint64>(
                    "forward",
                    RequestDataMessage::get_forward_for_reflect,
                    RequestDataMessage::mut_forward_for_reflect,
                ));
                fields.push(::protobuf::reflect::accessor::make_option_accessor::<_, ::protobuf::types::ProtobufTypeUint32>(
                    "num_cycles",
                    RequestDataMessage::get_num_cycles_for_reflect,
                    RequestDataMessage::mut_num_cycles_for_reflect,
                ));
                ::protobuf::reflect::MessageDescriptor::new::<RequestDataMessage>(
                    "RequestDataMessage",
                    fields,
                    file_descriptor_proto()
                )
            })
        }
    }
}

impl ::protobuf::Clear for RequestDataMessage {
    fn clear(&mut self) {
        self.clear_field_type();
        self.clear_sequence_number();
        self.clear_boxId();
        self.clear_time();
        self.clear_back();
        self.clear_forward();
        self.clear_num_cycles();
        self.unknown_fields.clear();
    }
}

impl ::std::fmt::Debug for RequestDataMessage {
    fn fmt(&self, f: &mut ::std::fmt::Formatter) -> ::std::fmt::Result {
        ::protobuf::text_format::fmt(self, f)
    }
}

impl ::protobuf::reflect::ProtobufValue for RequestDataMessage {
    fn as_ref(&self) -> ::protobuf::reflect::ProtobufValueRef {
        ::protobuf::reflect::ProtobufValueRef::Message(self)
    }
}

#[derive(Clone,PartialEq,Eq,Debug,Hash)]
pub enum RequestDataMessage_RequestType {
    PING = 1,
    PONG = 2,
    READ = 3,
    RESP = 4,
    ERROR = 5,
}

impl ::protobuf::ProtobufEnum for RequestDataMessage_RequestType {
    fn value(&self) -> i32 {
        *self as i32
    }

    fn from_i32(value: i32) -> ::std::option::Option<RequestDataMessage_RequestType> {
        match value {
            1 => ::std::option::Option::Some(RequestDataMessage_RequestType::PING),
            2 => ::std::option::Option::Some(RequestDataMessage_RequestType::PONG),
            3 => ::std::option::Option::Some(RequestDataMessage_RequestType::READ),
            4 => ::std::option::Option::Some(RequestDataMessage_RequestType::RESP),
            5 => ::std::option::Option::Some(RequestDataMessage_RequestType::ERROR),
            _ => ::std::option::Option::None
        }
    }

    fn values() -> &'static [Self] {
        static values: &'static [RequestDataMessage_RequestType] = &[
            RequestDataMessage_RequestType::PING,
            RequestDataMessage_RequestType::PONG,
            RequestDataMessage_RequestType::READ,
            RequestDataMessage_RequestType::RESP,
            RequestDataMessage_RequestType::ERROR,
        ];
        values
    }

    fn enum_descriptor_static(_: ::std::option::Option<RequestDataMessage_RequestType>) -> &'static ::protobuf::reflect::EnumDescriptor {
        static mut descriptor: ::protobuf::lazy::Lazy<::protobuf::reflect::EnumDescriptor> = ::protobuf::lazy::Lazy {
            lock: ::protobuf::lazy::ONCE_INIT,
            ptr: 0 as *const ::protobuf::reflect::EnumDescriptor,
        };
        unsafe {
            descriptor.get(|| {
                ::protobuf::reflect::EnumDescriptor::new("RequestDataMessage_RequestType", file_descriptor_proto())
            })
        }
    }
}

impl ::std::marker::Copy for RequestDataMessage_RequestType {
}

impl ::protobuf::reflect::ProtobufValue for RequestDataMessage_RequestType {
    fn as_ref(&self) -> ::protobuf::reflect::ProtobufValueRef {
        ::protobuf::reflect::ProtobufValueRef::Enum(self.descriptor())
    }
}

#[derive(PartialEq,Clone,Default)]
pub struct RequestEventMessage {
    // message fields
    start_timestamp_ms_utc: ::std::option::Option<u64>,
    end_timestamp_ms_utc: ::std::option::Option<u64>,
    trigger_type: ::std::option::Option<RequestEventMessage_TriggerType>,
    percent_magnitude: ::std::option::Option<f64>,
    box_ids: ::std::vec::Vec<i32>,
    requestee: ::protobuf::SingularField<::std::string::String>,
    description: ::protobuf::SingularField<::std::string::String>,
    request_data: ::std::option::Option<bool>,
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

    // required uint64 start_timestamp_ms_utc = 1;

    pub fn clear_start_timestamp_ms_utc(&mut self) {
        self.start_timestamp_ms_utc = ::std::option::Option::None;
    }

    pub fn has_start_timestamp_ms_utc(&self) -> bool {
        self.start_timestamp_ms_utc.is_some()
    }

    // Param is passed by value, moved
    pub fn set_start_timestamp_ms_utc(&mut self, v: u64) {
        self.start_timestamp_ms_utc = ::std::option::Option::Some(v);
    }

    pub fn get_start_timestamp_ms_utc(&self) -> u64 {
        self.start_timestamp_ms_utc.unwrap_or(0)
    }

    fn get_start_timestamp_ms_utc_for_reflect(&self) -> &::std::option::Option<u64> {
        &self.start_timestamp_ms_utc
    }

    fn mut_start_timestamp_ms_utc_for_reflect(&mut self) -> &mut ::std::option::Option<u64> {
        &mut self.start_timestamp_ms_utc
    }

    // required uint64 end_timestamp_ms_utc = 2;

    pub fn clear_end_timestamp_ms_utc(&mut self) {
        self.end_timestamp_ms_utc = ::std::option::Option::None;
    }

    pub fn has_end_timestamp_ms_utc(&self) -> bool {
        self.end_timestamp_ms_utc.is_some()
    }

    // Param is passed by value, moved
    pub fn set_end_timestamp_ms_utc(&mut self, v: u64) {
        self.end_timestamp_ms_utc = ::std::option::Option::Some(v);
    }

    pub fn get_end_timestamp_ms_utc(&self) -> u64 {
        self.end_timestamp_ms_utc.unwrap_or(0)
    }

    fn get_end_timestamp_ms_utc_for_reflect(&self) -> &::std::option::Option<u64> {
        &self.end_timestamp_ms_utc
    }

    fn mut_end_timestamp_ms_utc_for_reflect(&mut self) -> &mut ::std::option::Option<u64> {
        &mut self.end_timestamp_ms_utc
    }

    // required .opq.proto.RequestEventMessage.TriggerType trigger_type = 3;

    pub fn clear_trigger_type(&mut self) {
        self.trigger_type = ::std::option::Option::None;
    }

    pub fn has_trigger_type(&self) -> bool {
        self.trigger_type.is_some()
    }

    // Param is passed by value, moved
    pub fn set_trigger_type(&mut self, v: RequestEventMessage_TriggerType) {
        self.trigger_type = ::std::option::Option::Some(v);
    }

    pub fn get_trigger_type(&self) -> RequestEventMessage_TriggerType {
        self.trigger_type.unwrap_or(RequestEventMessage_TriggerType::FREQUENCY_SAG)
    }

    fn get_trigger_type_for_reflect(&self) -> &::std::option::Option<RequestEventMessage_TriggerType> {
        &self.trigger_type
    }

    fn mut_trigger_type_for_reflect(&mut self) -> &mut ::std::option::Option<RequestEventMessage_TriggerType> {
        &mut self.trigger_type
    }

    // required double percent_magnitude = 4;

    pub fn clear_percent_magnitude(&mut self) {
        self.percent_magnitude = ::std::option::Option::None;
    }

    pub fn has_percent_magnitude(&self) -> bool {
        self.percent_magnitude.is_some()
    }

    // Param is passed by value, moved
    pub fn set_percent_magnitude(&mut self, v: f64) {
        self.percent_magnitude = ::std::option::Option::Some(v);
    }

    pub fn get_percent_magnitude(&self) -> f64 {
        self.percent_magnitude.unwrap_or(0.)
    }

    fn get_percent_magnitude_for_reflect(&self) -> &::std::option::Option<f64> {
        &self.percent_magnitude
    }

    fn mut_percent_magnitude_for_reflect(&mut self) -> &mut ::std::option::Option<f64> {
        &mut self.percent_magnitude
    }

    // repeated int32 box_ids = 5;

    pub fn clear_box_ids(&mut self) {
        self.box_ids.clear();
    }

    // Param is passed by value, moved
    pub fn set_box_ids(&mut self, v: ::std::vec::Vec<i32>) {
        self.box_ids = v;
    }

    // Mutable pointer to the field.
    pub fn mut_box_ids(&mut self) -> &mut ::std::vec::Vec<i32> {
        &mut self.box_ids
    }

    // Take field
    pub fn take_box_ids(&mut self) -> ::std::vec::Vec<i32> {
        ::std::mem::replace(&mut self.box_ids, ::std::vec::Vec::new())
    }

    pub fn get_box_ids(&self) -> &[i32] {
        &self.box_ids
    }

    fn get_box_ids_for_reflect(&self) -> &::std::vec::Vec<i32> {
        &self.box_ids
    }

    fn mut_box_ids_for_reflect(&mut self) -> &mut ::std::vec::Vec<i32> {
        &mut self.box_ids
    }

    // required string requestee = 6;

    pub fn clear_requestee(&mut self) {
        self.requestee.clear();
    }

    pub fn has_requestee(&self) -> bool {
        self.requestee.is_some()
    }

    // Param is passed by value, moved
    pub fn set_requestee(&mut self, v: ::std::string::String) {
        self.requestee = ::protobuf::SingularField::some(v);
    }

    // Mutable pointer to the field.
    // If field is not initialized, it is initialized with default value first.
    pub fn mut_requestee(&mut self) -> &mut ::std::string::String {
        if self.requestee.is_none() {
            self.requestee.set_default();
        }
        self.requestee.as_mut().unwrap()
    }

    // Take field
    pub fn take_requestee(&mut self) -> ::std::string::String {
        self.requestee.take().unwrap_or_else(|| ::std::string::String::new())
    }

    pub fn get_requestee(&self) -> &str {
        match self.requestee.as_ref() {
            Some(v) => &v,
            None => "",
        }
    }

    fn get_requestee_for_reflect(&self) -> &::protobuf::SingularField<::std::string::String> {
        &self.requestee
    }

    fn mut_requestee_for_reflect(&mut self) -> &mut ::protobuf::SingularField<::std::string::String> {
        &mut self.requestee
    }

    // required string description = 7;

    pub fn clear_description(&mut self) {
        self.description.clear();
    }

    pub fn has_description(&self) -> bool {
        self.description.is_some()
    }

    // Param is passed by value, moved
    pub fn set_description(&mut self, v: ::std::string::String) {
        self.description = ::protobuf::SingularField::some(v);
    }

    // Mutable pointer to the field.
    // If field is not initialized, it is initialized with default value first.
    pub fn mut_description(&mut self) -> &mut ::std::string::String {
        if self.description.is_none() {
            self.description.set_default();
        }
        self.description.as_mut().unwrap()
    }

    // Take field
    pub fn take_description(&mut self) -> ::std::string::String {
        self.description.take().unwrap_or_else(|| ::std::string::String::new())
    }

    pub fn get_description(&self) -> &str {
        match self.description.as_ref() {
            Some(v) => &v,
            None => "",
        }
    }

    fn get_description_for_reflect(&self) -> &::protobuf::SingularField<::std::string::String> {
        &self.description
    }

    fn mut_description_for_reflect(&mut self) -> &mut ::protobuf::SingularField<::std::string::String> {
        &mut self.description
    }

    // required bool request_data = 8;

    pub fn clear_request_data(&mut self) {
        self.request_data = ::std::option::Option::None;
    }

    pub fn has_request_data(&self) -> bool {
        self.request_data.is_some()
    }

    // Param is passed by value, moved
    pub fn set_request_data(&mut self, v: bool) {
        self.request_data = ::std::option::Option::Some(v);
    }

    pub fn get_request_data(&self) -> bool {
        self.request_data.unwrap_or(false)
    }

    fn get_request_data_for_reflect(&self) -> &::std::option::Option<bool> {
        &self.request_data
    }

    fn mut_request_data_for_reflect(&mut self) -> &mut ::std::option::Option<bool> {
        &mut self.request_data
    }
}

impl ::protobuf::Message for RequestEventMessage {
    fn is_initialized(&self) -> bool {
        if self.start_timestamp_ms_utc.is_none() {
            return false;
        }
        if self.end_timestamp_ms_utc.is_none() {
            return false;
        }
        if self.trigger_type.is_none() {
            return false;
        }
        if self.percent_magnitude.is_none() {
            return false;
        }
        if self.requestee.is_none() {
            return false;
        }
        if self.description.is_none() {
            return false;
        }
        if self.request_data.is_none() {
            return false;
        }
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
                    self.start_timestamp_ms_utc = ::std::option::Option::Some(tmp);
                },
                2 => {
                    if wire_type != ::protobuf::wire_format::WireTypeVarint {
                        return ::std::result::Result::Err(::protobuf::rt::unexpected_wire_type(wire_type));
                    }
                    let tmp = is.read_uint64()?;
                    self.end_timestamp_ms_utc = ::std::option::Option::Some(tmp);
                },
                3 => {
                    ::protobuf::rt::read_proto2_enum_with_unknown_fields_into(wire_type, is, &mut self.trigger_type, 3, &mut self.unknown_fields)?
                },
                4 => {
                    if wire_type != ::protobuf::wire_format::WireTypeFixed64 {
                        return ::std::result::Result::Err(::protobuf::rt::unexpected_wire_type(wire_type));
                    }
                    let tmp = is.read_double()?;
                    self.percent_magnitude = ::std::option::Option::Some(tmp);
                },
                5 => {
                    ::protobuf::rt::read_repeated_int32_into(wire_type, is, &mut self.box_ids)?;
                },
                6 => {
                    ::protobuf::rt::read_singular_string_into(wire_type, is, &mut self.requestee)?;
                },
                7 => {
                    ::protobuf::rt::read_singular_string_into(wire_type, is, &mut self.description)?;
                },
                8 => {
                    if wire_type != ::protobuf::wire_format::WireTypeVarint {
                        return ::std::result::Result::Err(::protobuf::rt::unexpected_wire_type(wire_type));
                    }
                    let tmp = is.read_bool()?;
                    self.request_data = ::std::option::Option::Some(tmp);
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
        if let Some(v) = self.start_timestamp_ms_utc {
            my_size += ::protobuf::rt::value_size(1, v, ::protobuf::wire_format::WireTypeVarint);
        }
        if let Some(v) = self.end_timestamp_ms_utc {
            my_size += ::protobuf::rt::value_size(2, v, ::protobuf::wire_format::WireTypeVarint);
        }
        if let Some(v) = self.trigger_type {
            my_size += ::protobuf::rt::enum_size(3, v);
        }
        if let Some(v) = self.percent_magnitude {
            my_size += 9;
        }
        for value in &self.box_ids {
            my_size += ::protobuf::rt::value_size(5, *value, ::protobuf::wire_format::WireTypeVarint);
        };
        if let Some(ref v) = self.requestee.as_ref() {
            my_size += ::protobuf::rt::string_size(6, &v);
        }
        if let Some(ref v) = self.description.as_ref() {
            my_size += ::protobuf::rt::string_size(7, &v);
        }
        if let Some(v) = self.request_data {
            my_size += 2;
        }
        my_size += ::protobuf::rt::unknown_fields_size(self.get_unknown_fields());
        self.cached_size.set(my_size);
        my_size
    }

    fn write_to_with_cached_sizes(&self, os: &mut ::protobuf::CodedOutputStream) -> ::protobuf::ProtobufResult<()> {
        if let Some(v) = self.start_timestamp_ms_utc {
            os.write_uint64(1, v)?;
        }
        if let Some(v) = self.end_timestamp_ms_utc {
            os.write_uint64(2, v)?;
        }
        if let Some(v) = self.trigger_type {
            os.write_enum(3, v.value())?;
        }
        if let Some(v) = self.percent_magnitude {
            os.write_double(4, v)?;
        }
        for v in &self.box_ids {
            os.write_int32(5, *v)?;
        };
        if let Some(ref v) = self.requestee.as_ref() {
            os.write_string(6, &v)?;
        }
        if let Some(ref v) = self.description.as_ref() {
            os.write_string(7, &v)?;
        }
        if let Some(v) = self.request_data {
            os.write_bool(8, v)?;
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
                fields.push(::protobuf::reflect::accessor::make_option_accessor::<_, ::protobuf::types::ProtobufTypeUint64>(
                    "start_timestamp_ms_utc",
                    RequestEventMessage::get_start_timestamp_ms_utc_for_reflect,
                    RequestEventMessage::mut_start_timestamp_ms_utc_for_reflect,
                ));
                fields.push(::protobuf::reflect::accessor::make_option_accessor::<_, ::protobuf::types::ProtobufTypeUint64>(
                    "end_timestamp_ms_utc",
                    RequestEventMessage::get_end_timestamp_ms_utc_for_reflect,
                    RequestEventMessage::mut_end_timestamp_ms_utc_for_reflect,
                ));
                fields.push(::protobuf::reflect::accessor::make_option_accessor::<_, ::protobuf::types::ProtobufTypeEnum<RequestEventMessage_TriggerType>>(
                    "trigger_type",
                    RequestEventMessage::get_trigger_type_for_reflect,
                    RequestEventMessage::mut_trigger_type_for_reflect,
                ));
                fields.push(::protobuf::reflect::accessor::make_option_accessor::<_, ::protobuf::types::ProtobufTypeDouble>(
                    "percent_magnitude",
                    RequestEventMessage::get_percent_magnitude_for_reflect,
                    RequestEventMessage::mut_percent_magnitude_for_reflect,
                ));
                fields.push(::protobuf::reflect::accessor::make_vec_accessor::<_, ::protobuf::types::ProtobufTypeInt32>(
                    "box_ids",
                    RequestEventMessage::get_box_ids_for_reflect,
                    RequestEventMessage::mut_box_ids_for_reflect,
                ));
                fields.push(::protobuf::reflect::accessor::make_singular_field_accessor::<_, ::protobuf::types::ProtobufTypeString>(
                    "requestee",
                    RequestEventMessage::get_requestee_for_reflect,
                    RequestEventMessage::mut_requestee_for_reflect,
                ));
                fields.push(::protobuf::reflect::accessor::make_singular_field_accessor::<_, ::protobuf::types::ProtobufTypeString>(
                    "description",
                    RequestEventMessage::get_description_for_reflect,
                    RequestEventMessage::mut_description_for_reflect,
                ));
                fields.push(::protobuf::reflect::accessor::make_option_accessor::<_, ::protobuf::types::ProtobufTypeBool>(
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
        self.clear_trigger_type();
        self.clear_percent_magnitude();
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

#[derive(Clone,PartialEq,Eq,Debug,Hash)]
pub enum RequestEventMessage_TriggerType {
    FREQUENCY_SAG = 1,
    FREQUENCY_SWELL = 2,
    VOLTAGE_SAG = 3,
    VOLTAGE_SWELL = 4,
    OTHER = 5,
}

impl ::protobuf::ProtobufEnum for RequestEventMessage_TriggerType {
    fn value(&self) -> i32 {
        *self as i32
    }

    fn from_i32(value: i32) -> ::std::option::Option<RequestEventMessage_TriggerType> {
        match value {
            1 => ::std::option::Option::Some(RequestEventMessage_TriggerType::FREQUENCY_SAG),
            2 => ::std::option::Option::Some(RequestEventMessage_TriggerType::FREQUENCY_SWELL),
            3 => ::std::option::Option::Some(RequestEventMessage_TriggerType::VOLTAGE_SAG),
            4 => ::std::option::Option::Some(RequestEventMessage_TriggerType::VOLTAGE_SWELL),
            5 => ::std::option::Option::Some(RequestEventMessage_TriggerType::OTHER),
            _ => ::std::option::Option::None
        }
    }

    fn values() -> &'static [Self] {
        static values: &'static [RequestEventMessage_TriggerType] = &[
            RequestEventMessage_TriggerType::FREQUENCY_SAG,
            RequestEventMessage_TriggerType::FREQUENCY_SWELL,
            RequestEventMessage_TriggerType::VOLTAGE_SAG,
            RequestEventMessage_TriggerType::VOLTAGE_SWELL,
            RequestEventMessage_TriggerType::OTHER,
        ];
        values
    }

    fn enum_descriptor_static(_: ::std::option::Option<RequestEventMessage_TriggerType>) -> &'static ::protobuf::reflect::EnumDescriptor {
        static mut descriptor: ::protobuf::lazy::Lazy<::protobuf::reflect::EnumDescriptor> = ::protobuf::lazy::Lazy {
            lock: ::protobuf::lazy::ONCE_INIT,
            ptr: 0 as *const ::protobuf::reflect::EnumDescriptor,
        };
        unsafe {
            descriptor.get(|| {
                ::protobuf::reflect::EnumDescriptor::new("RequestEventMessage_TriggerType", file_descriptor_proto())
            })
        }
    }
}

impl ::std::marker::Copy for RequestEventMessage_TriggerType {
}

impl ::protobuf::reflect::ProtobufValue for RequestEventMessage_TriggerType {
    fn as_ref(&self) -> ::protobuf::reflect::ProtobufValueRef {
        ::protobuf::reflect::ProtobufValueRef::Enum(self.descriptor())
    }
}

static file_descriptor_proto_data: &'static [u8] = b"\
    \n\topq.proto\x12\topq.proto\"\x85\x01\n\x05Cycle\x12\x12\n\x04time\x18\
    \x01\x20\x02(\x04R\x04time\x12\x12\n\x04data\x18\x02\x20\x03(\x05R\x04da\
    ta\x12\x19\n\x08last_gps\x18\x03\x20\x01(\x05R\x07lastGps\x12#\n\rcurren\
    t_count\x18\x04\x20\x01(\x05R\x0ccurrentCount\x12\x14\n\x05flags\x18\x05\
    \x20\x01(\x05R\x05flags\"G\n\x0bDataMessage\x12\x0e\n\x02id\x18\x01\x20\
    \x02(\x05R\x02id\x12(\n\x06cycles\x18\x03\x20\x03(\x0b2\x10.opq.proto.Cy\
    cleR\x06cycles\"\xcc\x01\n\x0eTriggerMessage\x12\x0e\n\x02id\x18\x01\x20\
    \x02(\x05R\x02id\x12\x12\n\x04time\x18\x02\x20\x02(\x04R\x04time\x12\x1c\
    \n\tfrequency\x18\x03\x20\x02(\x02R\tfrequency\x12\x10\n\x03rms\x18\x04\
    \x20\x02(\x02R\x03rms\x12\x10\n\x03thd\x18\x05\x20\x01(\x02R\x03thd\x12\
    \x19\n\x08last_gps\x18\x06\x20\x01(\x05R\x07lastGps\x12#\n\rcurrent_coun\
    t\x18\x07\x20\x01(\x05R\x0ccurrentCount\x12\x14\n\x05flags\x18\x08\x20\
    \x01(\x05R\x05flags\"\xb5\x02\n\x12RequestDataMessage\x12=\n\x04type\x18\
    \x01\x20\x02(\x0e2).opq.proto.RequestDataMessage.RequestTypeR\x04type\
    \x12'\n\x0fsequence_number\x18\x02\x20\x02(\rR\x0esequenceNumber\x12\x14\
    \n\x05boxId\x18\x03\x20\x01(\rR\x05boxId\x12\x12\n\x04time\x18\x04\x20\
    \x01(\x04R\x04time\x12\x12\n\x04back\x18\x05\x20\x01(\x04R\x04back\x12\
    \x18\n\x07forward\x18\x06\x20\x01(\x04R\x07forward\x12\x1d\n\nnum_cycles\
    \x18\x07\x20\x01(\rR\tnumCycles\"@\n\x0bRequestType\x12\x08\n\x04PING\
    \x10\x01\x12\x08\n\x04PONG\x10\x02\x12\x08\n\x04READ\x10\x03\x12\x08\n\
    \x04RESP\x10\x04\x12\t\n\x05ERROR\x10\x05\"\xd9\x03\n\x13RequestEventMes\
    sage\x123\n\x16start_timestamp_ms_utc\x18\x01\x20\x02(\x04R\x13startTime\
    stampMsUtc\x12/\n\x14end_timestamp_ms_utc\x18\x02\x20\x02(\x04R\x11endTi\
    mestampMsUtc\x12M\n\x0ctrigger_type\x18\x03\x20\x02(\x0e2*.opq.proto.Req\
    uestEventMessage.TriggerTypeR\x0btriggerType\x12+\n\x11percent_magnitude\
    \x18\x04\x20\x02(\x01R\x10percentMagnitude\x12\x17\n\x07box_ids\x18\x05\
    \x20\x03(\x05R\x06boxIds\x12\x1c\n\trequestee\x18\x06\x20\x02(\tR\treque\
    stee\x12\x20\n\x0bdescription\x18\x07\x20\x02(\tR\x0bdescription\x12!\n\
    \x0crequest_data\x18\x08\x20\x02(\x08R\x0brequestData\"d\n\x0bTriggerTyp\
    e\x12\x11\n\rFREQUENCY_SAG\x10\x01\x12\x13\n\x0fFREQUENCY_SWELL\x10\x02\
    \x12\x0f\n\x0bVOLTAGE_SAG\x10\x03\x12\x11\n\rVOLTAGE_SWELL\x10\x04\x12\t\
    \n\x05OTHER\x10\x05\
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
