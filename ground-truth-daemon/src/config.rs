use serde::{Deserialize};
use std::path::Path;
use std::fs::File;
use std::env;
use serde_json::from_reader;

const CONFIG_KEY: &str = "GROUND_TRUTH_DAEMON_SETTINGS";

#[derive(Deserialize)]
pub struct Config {
    pub api_user: String,
    pub api_pass: String,
    pub api_host: String,
    pub api_port: u16,
}

impl Config {
    pub fn load() -> Result<Config, String> {
        // First, try to load from environment.
        match Config::load_from_env(CONFIG_KEY) {
            Ok(config) => Ok(config),
            // If that doesn't work, try to load from path passed into command line.
            Err(err) => {
                let args: Vec<String> = env::args().collect();
                match args.get(1) {
                    None => Err("Config not found in environment and path to file not supplied.".to_string()),
                    Some(path) => Config::load_from_file(path),
                }
            },
        }
    }

    /// Load the settings file from disk.
    fn load_from_file<P: AsRef<Path>>(path: P) -> Result<Config, String> {
        let file = File::open(path).or(Err("No such file"))?;
        let mut config: Config = from_reader(file).unwrap();
        Ok(config)
    }

    fn load_from_env(env: &str) -> Result<Config, String> {
        let contents = env::var(env).or(Err("Could not parse config from environment."))?;
        let mut config: Config =
            from_reader(contents.as_bytes()).or(Err("Could not parse config file."))?;
        Ok(config)
    }
}
