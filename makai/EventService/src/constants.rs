//Mongo common

///Remapping of names for protobuf to

///Mongo database that makai will be using.
pub static MONGO_DATABASE: &str = "opq";

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
//pub static MONGO_BOX_EVENTS_WINDOW_TS_FIELD: &str  = "window_timestamps_ms";
pub static MONGO_BOX_EVENTS_LOCATION_FIELD: &str  = "location";
pub static MONGO_BOX_EVENTS_FS_FIELD: &str  = "data_fs_filename";
//Mongo events collection:
pub static MONGO_EVENTS_COLLECTION: &str = "events";
pub static MONGO_EVENTS_ID_FIELD: &str ="event_id";
pub static MONGO_EVENTS_DESCRIPTION_FIELD: &str ="description";
pub static MONGO_EVENTS_TRIGGERED_FIELD: &str ="boxes_triggered";
pub static MONGO_EVENTS_RECEIVED_FIELD: &str ="boxes_received";
pub static MONGO_EVENTS_EXPIRE_AT: &str = "expire_at";

//pub static MONGO_EVENTS_LATENCIES_FIELD: &str ="latencies_ms";
pub static MONGO_EVENTS_START_FIELD: &str ="target_event_start_timestamp_ms";
pub static MONGO_EVENTS_END_FIELD: &str ="target_event_end_timestamp_ms";

pub static MONGO_LAHA_CONFIG_COLLECTION: &str = "laha_config";
pub const MONGO_LAHA_CONFIG_TTLS: &str = &"ttls";

pub const MONGO_LAHA_CONFIG_EVENTS_TTL: &str = "events";

pub static ENVIRONMENT_SETTINGS_VAR: &str = "MAKAI_SETTINGS";
pub static ZMQ_DATA_PREFIX: &str = "data_";

