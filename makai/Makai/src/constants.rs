//Mongo common
pub static MONGO_DATABASE: &str = "makai_test";

pub static MONGO_BOX_ID_FIELD: &str = "box_id";
pub static MONGO_TIMESTAMP_FIELD: &str = "timestamp_ms";
pub static MONGO_EXPIRE_FIELD: &str = "expireAt";


//Mongo Measurements
pub static MONGO_MEASUREMENT_COLLECTION: &str = "Measurements";
pub static MONGO_MEASUREMENTS_VOLTAGE_FIELD: &str = "voltage";
pub static MONGO_MEASUREMENTS_FREQUENCY_FIELD: &str = "frequency";
pub static MONGO_MEASUREMENTS_THD_FIELD: &str = "thd";
pub static MONGO_MEASUREMENTS_EXPIRE_TIME_SECONDS: i64 = 60*60*24;


//Mongo Measurements long term
pub static MONGO_LONG_TERM_MEASUREMENT_COLLECTION: &str = "SlowMeasurements";
pub static MONGO_LONG_TERM_MEASUREMENTS_VOLTAGE_FIELD: &str = "voltage";
pub static MONGO_LONG_TERM_MEASUREMENTS_FREQUENCY_FIELD: &str = "frequency";
pub static MONGO_LONG_TERM_MEASUREMENTS_THD_FIELD: &str = "thd";

pub static MONGO_LONG_TERM_MEASUREMENTS_MIN_FIELD: &str = "min";
pub static MONGO_LONG_TERM_MEASUREMENTS_MAX_FIELD: &str = "max";
pub static MONGO_LONG_TERM_MEASUREMENTS_FILTERED_FIELD: &str = "filtered";

pub static MONGO_LONG_TERM_MEASUREMENTS_HOW_OFTEN: i64 = 60;
pub static MONGO_LONG_TERM_MEASUREMENTS_LPF_SAMPLING_RATE: f32 = 6.0;
pub static MONGO_LONG_TERM_MEASUREMENTS_LPF_CUTOFF_FREQUENCY: f32 = 1.0/120.0;
pub static MONGO_LONG_TERM_MEASUREMENTS_LPF_Q: f32 = 0.7071;


