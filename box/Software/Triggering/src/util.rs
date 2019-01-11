use std::time::{SystemTime, UNIX_EPOCH};

pub fn systemtime_to_unix_timestamp(time: &SystemTime) -> u64 {
    let since_the_epoch = time.duration_since(UNIX_EPOCH).unwrap();
    since_the_epoch.as_secs() * 1000 + since_the_epoch.subsec_nanos() as u64 / 1_000_000
}

pub fn unix_timestamp() -> u64 {
    let since_the_epoch = SystemTime::now().duration_since(UNIX_EPOCH).unwrap();
    since_the_epoch.as_secs() * 1000 + since_the_epoch.subsec_nanos() as u64 / 1_000_000
}
