use std::collections::HashMap;
use std::sync::Mutex;
use std::time::Instant;

pub static ENVIRONMENT_SETTINGS_VAR: &str = "ACQUISITION_BROKER_SETTINGS";

pub static MONGO_DATABASE: &str = "opq";
pub static MAKAI_METRIC_DATABASE: &str = "makai_metrics";
pub static MAKAI_METRIC_HANDLE_FIELD: &str = "name";
pub static MAKAI_METRIC_SENT_FIELD: &str = "sent";
pub static MAKAI_METRIC_RECV_FIELD: &str = "recv";

pub static MAKAI_METRIC_HANDLE: &str = "ab";

pub struct AppState {
    pub id_map: HashMap<u32, (String, Instant)>,
    pub last_sent: Instant,
    pub sent: usize,
    pub recv: usize,
}

impl AppState {
    pub fn new() -> AppState {
        AppState {
            id_map: HashMap::new(),
            last_sent: Instant::now(),
            sent: 0,
            recv: 0,
        }
    }
}

lazy_static! {
    pub static ref ID_MAP: Mutex<AppState> = Mutex::new(AppState::new());
}
