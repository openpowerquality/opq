use std::collections::HashMap;
pub static SERVICE_NAME: &str = "makai";
#[derive(Default)]
pub struct Statistics {
    pub box_status: HashMap<u32, OpqBox>,
    pub trigger_now: bool,
}

#[derive(Serialize, Default)]
pub struct MakaiStatus {
    pub name: String,
    pub ok: bool,
    pub timestamp: u64,
    pub subcomponents: Vec<OpqBox>,
}

#[derive(Serialize, Default, Clone)]
pub struct OpqBox {
    pub name: String,
    pub timestamp: u64,
    pub ok: bool,
}

#[derive(Serialize, Deserialize, Default, Debug, Clone)]
pub struct HealthPluginSettings {
    pub address: String,
}
