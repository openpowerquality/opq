use crate::analysis::*;
use crate::arrays;
use crate::arrays::Bound;
use std::collections::HashMap;

#[derive(Debug)]
pub struct CycleRange {
    gt_min: bool,
    no_upper: bool,
    pub min_c: f64,
    pub max_c: f64,
}

impl CycleRange {
    pub fn new(min_c: f64, max_c: f64) -> CycleRange {
        CycleRange {
            min_c,
            max_c,
            gt_min: false,
            no_upper: false,
        }
    }

    pub fn from_ms_ms(min_ms: f64, max_ms: f64) -> CycleRange {
        CycleRange::new(ms_to_c(min_ms), ms_to_c(max_ms))
    }

    pub fn from_c_ms(min_c: f64, max_ms: f64) -> CycleRange {
        CycleRange::new(min_c, ms_to_c(max_ms))
    }

    pub fn from_c_s(min_c: f64, max_s: f64) -> CycleRange {
        CycleRange::new(min_c, s_to_c(max_s))
    }

    pub fn from_s_s(min_s: f64, max_s: f64) -> CycleRange {
        CycleRange::new(s_to_c(min_s), s_to_c(max_s))
    }

    pub fn contains(&self, range: &arrays::Range) -> bool {
        if self.gt_min {
            if self.no_upper {
                range.range_c() > self.min_c
            } else {
                range.range_c() > self.min_c && range.range_c() <= self.max_c
            }
        } else {
            if self.no_upper {
                range.range_c() >= self.min_c
            } else {
                range.range_c() >= self.min_c && range.range_c() <= self.max_c
            }
        }
    }

    pub fn set_gt_min(mut self) -> Self {
        self.gt_min = true;
        self
    }

    pub fn set_no_upper(mut self) -> Self {
        self.no_upper = true;
        self
    }
}

pub fn classify_segments(start_time_ms: f64, data: &Vec<f64>) {
    let mut bound_map: HashMap<Bound, Vec<(CycleRange, String)>> = HashMap::new();
    bound_map.insert(
        Bound::new(0.0, 0.1, Some(&pu_to_rms)),
        vec![
            (
                CycleRange::from_c_s(0.5, 3.0),
                "Momentary:Interruption".to_string(),
            ),
            (
                CycleRange::from_s_s(3.0, 60.0).set_gt_min(),
                "Temporary:Interruption".to_string(),
            ),
        ],
    );
    bound_map.insert(
        Bound::new(0.1, 0.9, Some(&pu_to_rms)),
        vec![
            (CycleRange::new(0.5, 30.0), "Instantaneous:Sag".to_string()),
            (CycleRange::from_c_s(30.0, 3.0), "Momentary:Sag".to_string()),
            (
                CycleRange::from_s_s(3.0, 60.0).set_gt_min(),
                "Temporary:Sag".to_string(),
            ),
        ],
    );
    bound_map.insert(
        Bound::new(0.8, 0.9, Some(&pu_to_rms)),
        vec![(
            CycleRange::from_s_s(60.0, 60.0 * 60.0 * 24.0)
                .set_gt_min()
                .set_no_upper(),
            "Undervoltage".to_string(),
        )],
    );
    bound_map.insert(
        Bound::new(1.1, 1.2, Some(&pu_to_rms)),
        vec![
            (
                CycleRange::from_s_s(3.0, 60.0).set_gt_min(),
                "Temporary:Swell".to_string(),
            ),
            (
                CycleRange::from_s_s(60.0, 60.0 * 60.0 * 24.0)
                    .set_gt_min()
                    .set_no_upper(),
                "Overvoltage".to_string(),
            ),
        ],
    );
    bound_map.insert(
        Bound::new(1.1, 1.4, Some(&pu_to_rms)),
        vec![(
            CycleRange::from_c_s(30.0, 3.0),
            "Momentary:Swell".to_string(),
        )],
    );
    bound_map.insert(
        Bound::new(1.1, 1.8, Some(&pu_to_rms)),
        vec![(
            CycleRange::new(0.5, 30.0),
            "Instantaneous:Swell".to_string(),
        )],
    );

    classify_data(start_time_ms, data, &bound_map.keys().collect());
}

fn classify_data(segment_start_ms: f64, data: &Vec<f64>, bounds: &Vec<&Bound>) {
    let ranges = arrays::bounded_ranges(segment_start_ms, data, bounds);
    classify_ranges(&ranges);
}

fn classify_ranges(ranges: &Vec<arrays::Range>) {}

fn classify_range(
    range: &arrays::Range,
    bound_map: &HashMap<Bound, Vec<(CycleRange, String)>>,
) -> Vec<Ieee1159VoltageIncident> {
    match bound_map.get(&range.bound) {
        None => vec![],
        Some(cycle_ranges) => {
            let mut res = vec![];
            for (cycle_range, incident_classification) in cycle_ranges {
                if cycle_range.contains(range) {
                    res.push(Ieee1159VoltageIncident {
                        start_time_ms: range.start_ts_ms,
                        end_time_ms: range.end_ts_ms,
                        start_idx: range.start_idx,
                        end_idx: range.end_idx,
                        incident_classification: incident_classification.clone(),
                    })
                }
            }
            res
        }
    }
}

struct Ieee1159VoltageIncident {
    pub start_time_ms: f64,
    pub end_time_ms: f64,
    pub start_idx: usize,
    pub end_idx: usize,
    pub incident_classification: String,
}
