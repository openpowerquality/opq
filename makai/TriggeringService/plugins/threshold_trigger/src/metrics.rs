use fsm::StateEntry;

pub struct ThresholdTriggerMetric {
    pub box_id: String,
    pub last_recv: u64,
    pub f: f64,
    pub v: f64,
    pub thd: f64,
    pub state_entries: Vec<StateEntry>,
}



