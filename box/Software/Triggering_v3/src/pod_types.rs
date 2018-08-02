use std::time::SystemTime;

pub const POINTS_PER_PACKET: usize = 200;

#[repr(C, packed)]
pub struct RawWindow {
    datapoints: [i16; POINTS_PER_PACKET],
    last_gps_counter: u16,
    current_counter: u16,
    flags: u32,
}

pub struct Window {
    raw_window: RawWindow,
    time_stamp_ms: SystemTime,
}

impl Window {
    pub fn new(raw_window: RawWindow) -> Window {
        Window {
            raw_window: raw_window,
            time_stamp_ms: SystemTime::now(),
        }
    }
}
