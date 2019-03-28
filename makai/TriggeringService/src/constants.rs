//Mongo common

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
pub static MONGO_EXPIRE_FIELD: &str = "expire_at";

//Mongo Measurements
///Mongo measurements collection.
pub static MONGO_MEASUREMENT_COLLECTION: &str = "measurements";

//Mongo Measurements long term
///Mongo long term measurements collection
pub static MONGO_LONG_TERM_MEASUREMENT_COLLECTION: &str = "trends";


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


pub static MONGO_LAHA_CONFIG_COLLECTION: &str = "laha_config";
pub const MONGO_LAHA_CONFIG_MEASUREMENTS_TTL: &str = "ttls.measurements";
pub const MONGO_LAHA_CONFIG_TRENDS_TTL: &str = "ttls.trends";
pub const MONGO_LAHA_CONFIG_EVENTS_TTL: &str = "ttls.events";

pub static ENVIRONMENT_SETTINGS_VAR: &str = "MAKAI_SETTINGS";
pub static ZMQ_DATA_PREFIX: &str = "data_";