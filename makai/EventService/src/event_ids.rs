use crate::config::Settings;
use std::sync::Mutex;

pub struct EventIdService {
    event_id: Mutex<i32>,
}

impl EventIdService {
    pub fn new(settings: &Settings) -> EventIdService {
        unimplemented!()
    }

    pub fn next_event_id(mut self) -> i32 {
        let mut data = self.event_id.lock().unwrap();
        *data += 1;
    }
}
