#[derive(Serialize, Deserialize, Default, Debug, Clone)]
pub struct ThresholdTriggerPluginSettings {
    pub mongo_host: String,
    pub mongo_port: u16,
    pub debug: bool,
    pub debug_devices: Vec<u32>,
}
