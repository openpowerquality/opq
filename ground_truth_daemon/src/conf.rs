use serde::Deserialize;
use serde_json;

const SETTINGS_KEY: &str = "GROUND_TRUTH_DAEMON_SETTINGS";

#[derive(Deserialize, Debug)]
pub struct GroundTruthDaemonConfig {
    pub username: String,
    pub password: String,
    pub features: Vec<String>,
    pub collect_last_s: usize,
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
}
