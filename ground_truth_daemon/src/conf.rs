use serde::Deserialize;
use serde_json;
use std::collections::HashSet;

const SETTINGS_KEY: &str = "GROUND_TRUTH_DAEMON_SETTINGS";

#[derive(Deserialize, Debug)]
pub struct GroundTruthDaemonConfig {
    pub username: String,
    pub password: String,
    pub features: HashSet<String>,
    pub collect_last_s: usize,
    pub collect_range: Vec<u64>,
    pub features_db: String,
    pub mongo_host: String,
    pub mongo_port: u16,
    pub path : String
}

impl GroundTruthDaemonConfig {
    pub fn from_env() -> Result<GroundTruthDaemonConfig, String> {
        match std::env::var(SETTINGS_KEY) {
            Ok(val) => match serde_json::from_str(&val) {
                Ok(res) => Ok(res),
                Err(err) => Err(format!("Error loading config from env: {:?}", err)),
            },
            Err(err) => Err(format!("Error loading config from env: {:?}", err)),
        }
    }

    pub fn is_ranged(&self) -> bool {
        self.collect_range.len() == 2
    }

    pub fn start_range_s(&self) -> u64 {
        self.collect_range[0]
    }

    pub fn end_range_s(&self) -> u64 {
        self.collect_range[1]
    }
}
