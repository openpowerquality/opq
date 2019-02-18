use std::collections::HashMap;

#[derive(Default)]
pub struct Statistics{
    pub box_status : HashMap<u32, OpqBox>,
    pub trigger_now : bool
}

#[derive(Serialize, Default, Copy, Clone)]
pub struct OpqBox{
    pub id : u32,
    pub last_timestamp : u64,
    pub ok : bool
}

#[derive(Serialize, Deserialize, Default, Debug, Clone)]
pub struct HealthPluginSettings{
    pub address : String,
}