use std::collections::HashMap;
use std::fmt;
use std::time::SystemTime;
use std::time::UNIX_EPOCH;

use crate::opqbox3::Cycle;

fn systemtime_to_unix_timestamp(time: &SystemTime) -> u64 {
    let since_the_epoch = time.duration_since(UNIX_EPOCH).unwrap();
    since_the_epoch.as_secs() * 1000 + since_the_epoch.subsec_nanos() as u64 / 1_000_000
}


pub const POINTS_PER_PACKET: usize = 200;

#[derive(Copy, Clone)]
#[repr(C, packed)]
pub struct RawWindow {
    pub datapoints: [i16; POINTS_PER_PACKET],
    pub last_gps_counter: u16,
    pub current_counter: u16,
    pub flags: u32,
}

impl RawWindow {
    pub fn encode_to_cycle(self, timestamp: &SystemTime) -> Cycle {
        let mut cycle = Cycle::new();
        unsafe {
            for i in self.datapoints.into_iter() {
                cycle.datapoints.push(*i as i32);
            }
        }
        cycle.set_timestamp_ms(systemtime_to_unix_timestamp(timestamp));
        cycle
    }
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

pub struct Window {
    pub raw_window: RawWindow,
    pub samples : [f32 ; POINTS_PER_PACKET],
    pub time_stamp_ms: SystemTime,
    pub results: HashMap<String, f32>,
}

impl fmt::Debug for Window {
    fn fmt(&self, formatter: &mut fmt::Formatter) -> fmt::Result {
        self.samples[..].fmt(formatter)
    }
}

impl Window {
    pub fn new(raw_window: RawWindow, cal_constant: f32) -> Window {
        let mut samples = [0.0; POINTS_PER_PACKET];
        for i in 0..POINTS_PER_PACKET{
            samples[i] = (raw_window.datapoints[i] as f32)/cal_constant;
        }
        Window {
            raw_window: raw_window,
            time_stamp_ms: SystemTime::now(),
            samples: samples,
            results: HashMap::new(),
        }
    }
}
