use serde_json::{from_reader, Value};
use std::env;
use std::fs::File;
use std::path::Path;
use uuid::Uuid;

///Representation of the configuration file's required fields.
#[derive(Debug, Serialize, Deserialize)]
pub struct Settings {
    ///zmq endpoint for the acquisition broker.
    pub zmq_data_endpoint: String,
    ///zmq endpoint for event
    pub zmq_event_endpoint: String,
    ///Mongo endpoint.
    pub mongo_host: String,
    ///Mongo port.
    pub mongo_port: u16,
    ///How long the measurements live in mongo before they expire.
    pub mongo_measurement_expiration_seconds: u64,
    ///Window width for the trend calculation.
    pub mongo_trends_update_interval_seconds: u64,
    ///How long the overlapping intervals structure keeps data.
    pub event_request_expiration_window_ms: u64,
    ///Makai Instance Identity.
    pub identity: Option<String>,
    ///Plugin specific settings.
    pub plugins: Vec<Value>,
    //TTL cache.
    pub ttl_cache_ttl: u64,
}

impl Settings {
    /// Load the settings file from disk.
    pub fn load_from_file<P: AsRef<Path>>(path: P) -> Result<Settings, String> {
        let file = File::open(path).or(Err("No such file"))?;
        let mut settings: Settings = from_reader(file).or(Err("Could not parse config file."))?;
        if settings.identity.is_none() {
            settings.identity = Some(Uuid::new_v4().to_string());
        }
        println!(
            "Staring with identity: {}",
            settings.identity.clone().unwrap()
        );
        Ok(settings)
    }

    pub fn load_from_env(env: &str) -> Result<Settings, String> {
        let contents = env::var(env).or(Err("Could not parse config from environment."))?;
        let mut settings: Settings =
            from_reader(contents.as_bytes()).or(Err("Could not parse config file."))?;
        if settings.identity.is_none() {
            settings.identity = Some(Uuid::new_v4().to_string());
        }
        println!(
            "Starting with identity: {}",
            settings.identity.clone().unwrap()
        );
        Ok(settings)
    }
}
