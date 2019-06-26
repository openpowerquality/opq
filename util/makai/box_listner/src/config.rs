use serde_json::{from_reader};
use std::fs::File;
use std::path::Path;
use uuid::Uuid;

///Representation of the configuration file's required fields.
#[derive(Debug, Serialize, Deserialize)]
pub struct Settings {
    /// zmq endpoint for the triggering broker.
    pub zmq_trigger_endpoint: String,
    ///zmq endpoint for the acquisition broker.
    pub zmq_acquisition_endpoint: String,
    ///zmq endpoint for the acquisition broker.
    pub zmq_data_endpoint: String,
    ///zmq endpoint for event
    pub zmq_event_endpoint: String,
    ///Mongo endpoint.
    pub mongo_host: String,
    ///Mongo port.
    pub mongo_port: u16,
    ///Makai Instance Identity.
    pub identity : Option<String>,
}

impl Settings {
    /// Load the settings file from disk.
    pub fn load_from_file<P: AsRef<Path>>(path: P) -> Result<Settings, String> {
        let file = File::open(path).or(Err("No such file"))?;
        let mut settings : Settings = from_reader(file).or(Err("Could not parse config file."))?;
        if settings.identity.is_none(){
            settings.identity = Some(Uuid::new_v4().to_string());
        }
        println!("Staring with identity: {}", settings.identity.clone().unwrap());
        Ok(settings)
    }
}
