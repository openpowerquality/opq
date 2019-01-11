use serde_json::from_reader;
use std::collections::HashMap;
use std::fs::File;
use std::path::Path;
use std::sync::Arc;
use std::sync::Mutex;
use zmq::CurveKeyPair;

pub const WINDOWS_PER_MEASUREMENT: &'static str = "windows_per_measurement";

#[derive(Debug)]
pub struct State {
    pub settings: Settings,
    state: Mutex<HashMap<String, f32>>,
}

impl State {
    pub fn new(file_path: &str) -> Result<Arc<State>, String> {
        info!("Loading configuration file {} ", file_path);
        let mut settings = match Settings::load_from_file(file_path) {
            Ok(s) => s,
            Err(e) => {
                return Err(format!(
                    "Could not load a settings file {}: {}",
                    file_path, e
                ));
            }
        };
        if settings.box_public_key.is_none() || settings.box_secret_key.is_none() {
            let key_pair = CurveKeyPair::new().unwrap();
            settings.box_public_key = Some(key_pair.public_key.to_string());
            settings.box_secret_key = Some(key_pair.secret_key.to_string());
            warn!("No keys in configuration. Generating a key pair.");
        }

        let cfg = Arc::new(State {
            settings: settings,
            state: Mutex::new(HashMap::new()),
        });
        let wpm = cfg.settings.windows_per_measurements as f32;
        cfg.set_state(&WINDOWS_PER_MEASUREMENT.to_string(), wpm);
        Ok(cfg)
    }

    pub fn get_state(&self, k: &String) -> Option<f32> {
        let map = self.state.lock().unwrap();
        match map.get(k) {
            None => None,
            Some(val) => Some(*val),
        }
    }
    pub fn set_state(&self, k: &String, val: f32) {
        let mut map = self.state.lock().unwrap();
        map.insert(k.clone(), val);
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
    pub box_secret_key: Option<String>,
    pub box_public_key: Option<String>,
    ///Server Key
    pub server_public_key: String,

    //Box_id
    pub box_id: u32,
    //Calibration constant.
    pub calibration: f32,
    //Device path:
    pub device_path: String,
    //Number of windows to aggregate into a single measurement
    pub windows_per_measurements: usize,
    //Number of stored windows in the ring buffer
    pub windows_in_storage_buffer: usize,
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
