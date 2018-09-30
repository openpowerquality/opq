use std::sync::Arc;
use std::sync::Mutex;
use std::time::SystemTime;
use std::collections::VecDeque;
use types::{RawWindow, Window};
use config::State;

#[derive(Default)]
pub struct WindowDB {
    storage: Mutex<VecDeque<(SystemTime, RawWindow)>>,
    hwm : usize
}

impl WindowDB {
    pub fn new(config : Arc<State>) -> Arc<WindowDB> {
        Arc::new(WindowDB {
            storage: Mutex::new(VecDeque::new()),
            hwm : config.settings.windows_in_storage_buffer
        })
    }

    pub fn add_window(&self, window : Window){
        let mut db = self.storage.lock().unwrap();
        db.push_back((window.time_stamp_ms, window.raw_window));
        if db.len() > self.hwm {
            db.pop_front();
        }
    }

    pub fn get_window_range(&self, start :SystemTime, end : SystemTime) -> Vec<(SystemTime, RawWindow)>{
        let mut ret = vec![];
        for (time, window) in self.storage.lock().unwrap().iter(){
            if time > &start && time < &end {
                ret.push((time.clone(), window.clone()));
            }
        }
        ret
    }
}