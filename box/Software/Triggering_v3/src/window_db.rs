use std::sync::Arc;
use std::sync::Mutex;
use std::time::SystemTime;
use std::vec::Vec;
use types::{RawWindow, Window};
use config::Config;

#[derive(Default)]
struct WindowDB {
    storage: Mutex<Vec<(SystemTime, RawWindow)>>,
    hwm : usize
}

impl WindowDB {
    pub fn new(config : Arc<Config>) -> Arc<WindowDB> {
        Arc::new(WindowDB {
            storage: Mutex::new(vec![]),
            hwm : config.windows_in_storage_buffer
        })
    }

    pub fn add_window(window : Window){

    }
}
