use serde_json::from_reader;
use std::fs::File;
use std::path::Path;
use std::collections::HashMap;
use std::sync::Mutex;
use std::sync::Arc;

#[derive(Debug)]
pub struct Config{
    pub settings : Settings,
    state : Mutex<HashMap<String, f32>>,
}

impl Config {
    pub fn new(file_path:&str) -> Result<Arc<Config>, String>{
        info!("Loading configuration file {} ", file_path);
        let settings = match Settings::load_from_file(file_path) {
            Ok(s) => s,
            Err(e) => {
                return Err(format!("Could not load a settings file {}: {}", file_path, e));
            }
        };
        Ok(Arc::new(Config {
            settings:settings,
            state : Mutex::new(HashMap::new())
        }))
    }
}


///Representation of the configuration file's required fields.
#[derive(Debug, Serialize, Deserialize)]
pub struct Settings {
    /// zmq endpoint for the cmd rx
    pub cmd_sub_ep: String,
    /// zmq endpoint for the cmd tx
    pub cmd_push_ep: String,

    //zmq endpoint for triggering stream
    pub trg_push_ep: String,

    ///box keys
    pub box_secret_key: String,
    pub box_public_key: String,
    ///Server Key
    pub server_public_key: String,
    //Box_id
    pub box_id: u32,

    //Device path:
    pub device_path : String,
    ///Plugin specific settings.
    pub plugins: Vec<String>,
}

impl Settings {
    /// Load the settings file from disk.
    pub fn load_from_file<P: AsRef<Path>>(path: P) -> Result<Settings, String> {
        let file = File::open(path).or(Err("No such file"))?;
        let u = from_reader(file).or(Err("Could not parse config file."))?;
        Ok(u)
    }
}
