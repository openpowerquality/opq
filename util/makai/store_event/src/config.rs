use serde_json::{from_reader};
use std::fs::File;
use std::path::Path;

///Representation of the configuration file's required fields.
#[derive(Debug, Serialize, Deserialize)]
pub struct Settings {
    ///zmq endpoint for event
    pub zmq_event_endpoint: String,
    ///Mongo endpoint.
    pub mongo_host: String,
    ///Mongo port.
    pub mongo_port: u16,
    ///Directory to store events.
    pub path : String,
    ///How long to wait till we grab the event:
    pub grace_ms : u32,

}

impl Settings {
    /// Load the settings file from disk.
    pub fn load_from_file<P: AsRef<Path>>(path: P) -> Result<Settings, String> {
        let file = File::open(path).or(Err("No such file"))?;
        let settings : Settings = from_reader(file).or(Err("Could not parse config file."))?;
        Ok(settings)
    }
}
