use std::cmp::Ordering;
use std::sync::Arc;
use triggering_service::proto::opqbox3::Measurement;
use std::time::{SystemTime, UNIX_EPOCH};

#[derive(Ord, PartialOrd, Eq, PartialEq, Copy, Clone, Debug)]
pub enum MetricStatus {
    AboveThreshold = 3,
    Outside3STD = 2,
    BelowThreshold = 1,
    Empty = 0,
}

#[derive(Clone, Debug)]
pub struct MetricVector {
    pub status: MetricStatus,
    pub id: u32,
    pub ts: u64,
}

impl Ord for MetricVector {
    fn cmp(&self, other: &Self) -> Ordering {
        (self.ts).cmp(&(&other.ts))
    }
}
impl PartialOrd for MetricVector {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}

impl PartialEq for MetricVector {
    fn eq(&self, other: &Self) -> bool {
        (self.ts) == (other.ts)
    }
}

impl Eq for MetricVector {}

#[derive(Serialize, Deserialize, Default, Debug)]
pub struct NapaliPluginSettings {
    //Decay for the mean and rms
    pub alpha: f32,

    //limits
    pub f_min: f32,
    pub f_max: f32,
    pub rms_min: f32,
    pub rms_max: f32,
    pub thd_max: f32,
    pub trans_max: f32,

    //Grace time before considering an event over.
    pub grace_time_ms : u64,
    //trigger_local
    pub trigger_local : bool,
    //debug
    pub debug : bool,
}

#[derive(Debug)]
pub struct ThresholdLimit {
    pub min: f32,
    pub max: f32,
}

pub trait BoxMetric {
    fn new_metric(&mut self, measurement: Arc<Measurement>) -> MetricStatus;
}


pub fn timestamp() -> u64{
    let start = SystemTime::now();
    let since_the_epoch = start.duration_since(UNIX_EPOCH)
        .expect("Time went backwards");
    since_the_epoch.as_secs() * 1000 +
        since_the_epoch.subsec_nanos() as u64 / 1_000_000

}