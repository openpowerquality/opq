use serde_json::{from_reader, Value};
use std::fs::File;
use std::path::Path;

#[derive(Debug, Serialize, Deserialize)]
pub struct Settings {
    pub zmq_trigger_endpoint: String,
    pub zmq_acquisition_endpoint: String,
    pub mongo_host: String,
    pub mongo_port: u16,
    pub mongo_measurement_expiration_seconds: u64,
    pub mongo_trends_update_interval_seconds: u64,
    pub event_request_expiration_window_ms: u64,
    pub plugins: Vec<Value>,
}

impl Settings {
    pub fn load_from_file<P: AsRef<Path>>(path: P) -> Result<Settings, String> {
        let file = File::open(path).or(Err("No such file"))?;
        let u = from_reader(file).or(Err("Could not parse config file."))?;
        Ok(u)
    }
}
