//Mongo common
#![allow(dead_code)]

///Remapping of names for protobuf to

use std::collections::HashMap;

lazy_static! {
    pub static ref MONGO_FIELD_REMAP: HashMap<&'static str, &'static str> = {
        let mut m = HashMap::new();
        m.insert("rms", "voltage");
        m.insert("f", "frequency");
        m.insert("thd", "thd");
        m
    };
}


///Mongo database that makai will be using.
pub static MONGO_DATABASE: &str = "opq";

///Box id mongo field.
pub static MONGO_BOX_ID_FIELD: &str = "box_id";
///Mongo timestamp field.
pub static MONGO_TIMESTAMP_FIELD: &str = "timestamp_ms";
///Mongo expire field.
pub static MONGO_EXPIRE_FIELD: &str = "expireAt";

//Mongo Measurements
///Mongo measurements collection.
pub static MONGO_MEASUREMENT_COLLECTION: &str = "measurements";
///Mongo measurements collection voltage field.
pub static MONGO_MEASUREMENTS_VOLTAGE_FIELD: &str = "voltage";
///Mongo measurements collection frequency field.
pub static MONGO_MEASUREMENTS_FREQUENCY_FIELD: &str = "frequency";
///Mongo measurements collection total harmonic distortion field.
pub static MONGO_MEASUREMENTS_THD_FIELD: &str = "thd";

//Mongo Measurements long term
///Mongo long term measurements collection
pub static MONGO_LONG_TERM_MEASUREMENT_COLLECTION: &str = "trends";
///Mongo long term measurements collection voltage field.
pub static MONGO_LONG_TERM_MEASUREMENTS_VOLTAGE_FIELD: &str = "voltage";
///Mongo long term measurements collection frequency field.
pub static MONGO_LONG_TERM_MEASUREMENTS_FREQUENCY_FIELD: &str = "frequency";
///Mongo long term measurements collection total harmonic distortion field.
pub static MONGO_LONG_TERM_MEASUREMENTS_THD_FIELD: &str = "thd";

///Mongo long term measurements collection statistics minimum.
pub static MONGO_LONG_TERM_MEASUREMENTS_MIN_FIELD: &str = "min";
///Mongo long term measurements collection statistics maximum.
pub static MONGO_LONG_TERM_MEASUREMENTS_MAX_FIELD: &str = "max";
///Mongo long term measurements collection statistics average.
pub static MONGO_LONG_TERM_MEASUREMENTS_FILTERED_FIELD: &str = "average";
//Mongo long term measurements location.
pub static MONGO_LONG_TERM_MEASUREMENTS_LOCATION_FIELD: &str = "location";
//Mongo long term measurements default location.
pub static MONGO_LONG_TERM_MEASUREMENTS_DEFAULT_LOCATION: &str = "unknown";


///Mongo boxes collection.
pub static MONGO_OPQ_BOXES_COLLECTION: &str = "opq_boxes";
//Mongo boxes collection box id.
pub static MONGO_OPQ_BOXES_BOX_ID_FIELD: &str = "box_id";
//Mongo boxes collection box id.
pub static MONGO_OPQ_BOXES_LOCATION_FIELD: &str = "location";


//Mongo box events collection:
pub static MONGO_BOX_EVENTS_COLLECTION: &str = "box_events";
//Mongo events collection event id;
pub static MONGO_BOX_EVENTS_ID_FIELD: &str = "event_id";
pub static MONGO_BOX_EVENTS_BOX_ID_FIELD: &str  = "box_id";
pub static MONGO_BOX_EVENTS_EVENT_START_FIELD: &str  = "event_start_timestamp_ms";
pub static MONGO_BOX_EVENTS_EVENT_END_FIELD: &str  = "event_end_timestamp_ms";
pub static MONGO_BOX_EVENTS_WINDOW_TS_FIELD: &str  = "window_timestamps_ms";
pub static MONGO_BOX_EVENTS_LOCATION_FIELD: &str  = "location";
pub static MONGO_BOX_EVENTS_FS_FIELD: &str  = "data_fs_filename";

//Mongo events collection:
pub static MONGO_EVENTS_COLLECTION: &str = "events";
pub static MONGO_EVENTS_ID_FIELD: &str ="event_id";
pub static MONGO_EVENTS_DESCRIPTION_FIELD: &str ="description";
pub static MONGO_EVENTS_TRIGGERED_FIELD: &str ="boxes_triggered";
pub static MONGO_EVENTS_RECEIVED_FIELD: &str ="boxes_received";
pub static MONGO_EVENTS_LATENCIES_FIELD: &str ="latencies_ms";
pub static MONGO_EVENTS_START_FIELD: &str ="target_event_start_timestamp_ms";
pub static MONGO_EVENTS_END_FIELD: &str ="target_event_end_timestamp_ms";

