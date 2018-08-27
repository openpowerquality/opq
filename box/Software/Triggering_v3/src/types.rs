use std::collections::HashMap;
use std::fmt;
use std::time::SystemTime;

pub const POINTS_PER_PACKET: usize = 200;

#[repr(C, packed)]
pub struct RawWindow {
    datapoints: [i16; POINTS_PER_PACKET],
    last_gps_counter: u16,
    current_counter: u16,
    flags: u32,
}

impl fmt::Debug for RawWindow {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        unsafe {
            for i in self.datapoints.iter() {
                write!(f, "{}, ", i).unwrap();
            }
        }
        Ok(())
    }
}

#[derive(Debug)]
pub struct Window {
    pub raw_window: RawWindow,
    pub time_stamp_ms: SystemTime,
    pub results: HashMap<String, f32>,
}

impl Window {
    pub fn new(raw_window: RawWindow) -> Window {
        Window {
            raw_window: raw_window,
            time_stamp_ms: SystemTime::now(),
            results: HashMap::new(),
        }
    }
}
