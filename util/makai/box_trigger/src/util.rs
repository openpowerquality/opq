use time;

pub fn timestamp() -> u64 {
    let timespec = time::get_time();
    let mills: u64 = (timespec.sec * 1000 + (timespec.nsec as i64/ 1000 / 1000)) as u64;
    mills
}
