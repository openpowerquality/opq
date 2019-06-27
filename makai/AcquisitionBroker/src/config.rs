use serde_json::from_reader;
use std::env;
use std::fs::File;
use std::path::Path;

///Representation of the configuration file's required fields.
#[derive(Debug, Deserialize, Clone)]
pub struct Settings {
    pub server_cert: String,
    pub box_pub: String,
    pub box_pull: String,
    pub backend_pull: String,
    pub backend_pub: String,
    pub mongo_host: String,
    pub mongo_port: u16,
    pub metric_update_sec: u64,
    pub pub_key: Option<String>,
    pub sec_key: Option<String>,
}

impl Settings {
    /// Load the settings file from disk.
    pub fn load_from_file<P: AsRef<Path>>(path: P) -> Result<Settings, String> {
        let file = File::open(path).or(Err("No such file"))?;
        let settings: Settings = from_reader(file).unwrap();
        Ok(settings)
    }

    pub fn load_from_env(env: &str) -> Result<Settings, String> {
        let contents = env::var(env).or(Err("Could not parse config from environment."))?;
        let settings: Settings = from_reader(contents.as_bytes()).unwrap();
        Ok(settings)
    }
}
