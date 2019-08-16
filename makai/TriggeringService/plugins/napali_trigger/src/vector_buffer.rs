use std::collections::BTreeSet;
use std::collections::HashSet;
use std::iter::FromIterator;
use types::{MetricStatus, MetricVector};

#[derive(Default)]
pub struct VectorBuffer {
    pub history: BTreeSet<MetricVector>,
    pub start : u64,
    pub end : u64
}

impl VectorBuffer {
    pub fn insert(&mut self, vector: MetricVector) {
        if self.history.len() == 0 {
            self.start = vector.ts;
        }
        self.end = vector.ts;
        self.history.insert(vector);
    }

    pub fn get_trigger_list(&mut self) -> HashSet<u32> {
        HashSet::from_iter(self.history
                .iter()
                .filter(|vec| {
                    vec.status == MetricStatus::AboveThreshold
                        || vec.status == MetricStatus::Outside3STD
                })
                .map(|vec| vec.id)
                .clone(),)
    }

    pub fn clear(&mut self ){
        self.history.clear();
    }
}
