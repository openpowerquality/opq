use crate::analysis::*;
use crate::arrays;
use crate::arrays::Bound;
use std::collections::HashMap;

pub fn classify_segments(start_time_ms: f64, data: &Vec<f64>) {
    let bounds = bound_map();
    classify_data(start_time_ms, data, &bounds.keys().collect());
}

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

fn bound_map() -> HashMap<Bound, Vec<(CycleRange, String)>> {
    let mut bmap: HashMap<Bound, Vec<(CycleRange, String)>> = HashMap::new();
    bmap.insert(
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
    bmap.insert(
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
    bmap.insert(
        Bound::new(0.8, 0.9, Some(&pu_to_rms)),
        vec![(
            CycleRange::from_s_s(60.0, 60.0 * 60.0 * 24.0)
                .set_gt_min()
                .set_no_upper(),
            "Undervoltage".to_string(),
        )],
    );
    bmap.insert(
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
    bmap.insert(
        Bound::new(1.1, 1.4, Some(&pu_to_rms)),
        vec![(
            CycleRange::from_c_s(30.0, 3.0),
            "Momentary:Swell".to_string(),
        )],
    );
    bmap.insert(
        Bound::new(1.1, 1.8, Some(&pu_to_rms)),
        vec![(
            CycleRange::new(0.5, 30.0),
            "Instantaneous:Swell".to_string(),
        )],
    );
    bmap
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

#[derive(Debug)]
struct Ieee1159VoltageIncident {
    pub start_time_ms: f64,
    pub end_time_ms: f64,
    pub start_idx: usize,
    pub end_idx: usize,
    pub incident_classification: String,
}

#[cfg(test)]
mod tests {
    use crate::analysis::*;
    use crate::arrays::{Bound, Range};
    use crate::ieee1159_voltage::{bound_map, classify_range, CycleRange};

    #[test]
    fn cycle_range_create_new() {
        let cr = CycleRange::new(0.0, 1.0);
        assert_eq!(cr.min_c, 0.0);
        assert_eq!(cr.max_c, 1.0);
        assert!(!cr.gt_min);
        assert!(!cr.no_upper);
    }

    #[test]
    fn cycle_range_from_ms_ms() {
        let cr = CycleRange::from_ms_ms(0.0, 1_000.0);
        assert_eq!(cr.min_c, 0.0);
        assert_eq!(cr.max_c, 60.0);
    }

    #[test]
    fn cycle_range_from_c_ms() {
        let cr = CycleRange::from_c_ms(0.0, 1_000.0);
        assert_eq!(cr.min_c, 0.0);
        assert_eq!(cr.max_c, 60.0);
    }

    #[test]
    fn cycle_range_contains() {
        let cr = CycleRange::new(2.0, 4.0);
        let range = Range {
            bound: Bound::new(0.0, 0.0, None),
            start_idx: 0,
            end_idx: 2,
            start_ts_ms: 0.0,
            end_ts_ms: c_to_ms(3.0),
        };
        assert!(cr.contains(&range));
        let range = Range {
            end_idx: 3,
            end_ts_ms: c_to_ms(3.0),
            ..range
        };
        assert!(cr.contains(&range));
        let range = Range {
            end_idx: 4,
            end_ts_ms: c_to_ms(4.0),
            ..range
        };
        assert!(cr.contains(&range));
    }

    #[test]
    fn cycle_range_dn_contain() {
        let cr = CycleRange::new(2.0, 4.0);
        let range = Range {
            bound: Bound::new(0.0, 0.0, None),
            start_idx: 0,
            end_idx: 1,
            start_ts_ms: 0.0,
            end_ts_ms: c_to_ms(1.0),
        };
        assert!(!cr.contains(&range));
        let range = Range {
            end_idx: 5,
            end_ts_ms: c_to_ms(5.0),
            ..range
        };
        assert!(!cr.contains(&range));
    }

    #[test]
    fn cycle_range_contains_gt_min() {
        let cr = CycleRange::new(2.0, 4.0).set_gt_min();
        let range = Range {
            bound: Bound::new(0.0, 0.0, None),
            start_idx: 0,
            end_idx: 3,
            start_ts_ms: 0.0,
            end_ts_ms: c_to_ms(3.0),
        };
        assert!(cr.contains(&range));
        let range = Range {
            end_idx: 3,
            end_ts_ms: c_to_ms(3.0),
            ..range
        };
        assert!(cr.contains(&range));
        let range = Range {
            end_idx: 4,
            end_ts_ms: c_to_ms(4.0),
            ..range
        };
        assert!(cr.contains(&range));
    }

    #[test]
    fn cycle_range_dn_contain_gt_min() {
        let cr = CycleRange::new(2.0, 4.0).set_gt_min();
        let range = Range {
            bound: Bound::new(0.0, 0.0, None),
            start_idx: 0,
            end_idx: 1,
            start_ts_ms: 0.0,
            end_ts_ms: c_to_ms(1.0),
        };
        assert!(!cr.contains(&range));
        let range = Range {
            end_idx: 2,
            end_ts_ms: c_to_ms(2.0),
            ..range
        };
        assert!(!cr.contains(&range));
    }

    #[test]
    fn cycle_range_contains_no_upper() {
        let cr = CycleRange::new(2.0, 4.0).set_no_upper();
        let range = Range {
            bound: Bound::new(0.0, 0.0, None),
            start_idx: 0,
            end_idx: 2,
            start_ts_ms: 0.0,
            end_ts_ms: c_to_ms(2.0),
        };
        assert!(cr.contains(&range));
        let range = Range {
            end_idx: 1_000_000,
            end_ts_ms: c_to_ms(1_000_000.0),
            ..range
        };
        assert!(cr.contains(&range));
    }

    #[test]
    fn cycle_range_dn_contain_no_upper() {
        let cr = CycleRange::new(2.0, 4.0).set_no_upper();
        let range = Range {
            bound: Bound::new(0.0, 0.0, None),
            start_idx: 0,
            end_idx: 1,
            start_ts_ms: 0.0,
            end_ts_ms: c_to_ms(2.0),
        };
        assert!(!cr.contains(&range));
    }

    #[test]
    fn cycle_range_from_s_s() {
        let cr = CycleRange::from_s_s(0.0, 1.0);
        assert_eq!(cr.min_c, 0.0);
        assert_eq!(cr.max_c, 60.0);
    }

    #[test]
    fn classify_range_instantaneous_sag() {
        let bmap = bound_map();
        let range = Range {
            bound: Bound::new(0.1, 0.9, Some(&pu_to_rms)),
            start_idx: 1,
            end_idx: 2,
            start_ts_ms: 0.0,
            end_ts_ms: c_to_ms(1.0),
        };

        let res = classify_range(&range, &bmap);
        assert_eq!(res.len(), 1);
        let incident = res.get(0).unwrap();
        assert_eq!(incident.start_idx, 1);
        assert_eq!(incident.end_idx, 2);
        assert_eq!(incident.start_time_ms, 0.0);
        assert_eq!(incident.end_time_ms, c_to_ms(1.0));
        assert_eq!(&incident.incident_classification, "Instantaneous:Sag");

        let range = Range {
            start_idx: 0,
            end_idx: 29,
            start_ts_ms: 0.0,
            end_ts_ms: c_to_ms(29.0),
            ..range
        };

        let res = classify_range(&range, &bmap);
        assert_eq!(res.len(), 1);
        let incident = res.get(0).unwrap();
        assert_eq!(incident.start_idx, 0);
        assert_eq!(incident.end_idx, 29);
        assert_eq!(incident.start_time_ms, 0.0);
        assert_eq!(incident.end_time_ms, c_to_ms(29.0));
        assert_eq!(&incident.incident_classification, "Instantaneous:Sag");
    }

    #[test]
    fn classify_range_instantaneous_swell() {
        let bmap = bound_map();
        let range = Range {
            bound: Bound::new(1.1, 1.8, Some(&pu_to_rms)),
            start_idx: 0,
            end_idx: 1,
            start_ts_ms: 0.0,
            end_ts_ms: c_to_ms(1.0),
        };

        let res = classify_range(&range, &bmap);
        assert_eq!(res.len(), 1);
        let incident = res.get(0).unwrap();
        assert_eq!(&incident.incident_classification, "Instantaneous:Swell");

        let range = Range {
            end_idx: 29,
            end_ts_ms: c_to_ms(29.0),
            ..range
        };

        let res = classify_range(&range, &bmap);
        assert_eq!(res.len(), 1);
        let incident = res.get(0).unwrap();
        assert_eq!(&incident.incident_classification, "Instantaneous:Swell");
    }

    #[test]
    fn classify_momentary_interruption() {
        let bmap = bound_map();
        let range = Range {
            bound: Bound::new(0.0, 0.1, Some(&pu_to_rms)),
            start_idx: 0,
            end_idx: 1,
            start_ts_ms: 0.0,
            end_ts_ms: c_to_ms(1.0),
        };
        let res = classify_range(&range, &bmap);
        assert_eq!(res.len(), 1);
        let incident = res.get(0).unwrap();
        assert_eq!(&incident.incident_classification, "Momentary:Interruption");
        let range = Range {
            end_idx: (s_to_c(3.0) - 1.0) as usize,
            end_ts_ms: c_to_ms(s_to_c(3.0) - 1.0),
            ..range
        };
        let res = classify_range(&range, &bmap);
        assert_eq!(res.len(), 1);
        let incident = res.get(0).unwrap();
        assert_eq!(&incident.incident_classification, "Momentary:Interruption");
    }

    #[test]
    fn classify_momentary_sag() {
        let bmap = bound_map();
        let range = Range {
            bound: Bound::new(0.1, 0.9, Some(&pu_to_rms)),
            start_idx: 0,
            end_idx: 30,
            start_ts_ms: 0.0,
            end_ts_ms: c_to_ms(30.0),
        };
        let res = classify_range(&range, &bmap);
        assert_eq!(res.len(), 2);
        let incident = res.get(1).unwrap();
        assert_eq!(&incident.incident_classification, "Momentary:Sag");
        let range = Range {
            end_idx: (s_to_c(3.0)) as usize,
            end_ts_ms: c_to_ms(s_to_c(3.0)),
            ..range
        };
        let res = classify_range(&range, &bmap);
        assert_eq!(res.len(), 1);
        let incident = res.get(0).unwrap();
        assert_eq!(&incident.incident_classification, "Momentary:Sag");
    }

    #[test]
    fn classify_momentary_swell() {
        let bmap = bound_map();
        let range = Range {
            bound: Bound::new(1.1, 1.8, Some(&pu_to_rms)),
            start_idx: 0,
            end_idx: 30,
            start_ts_ms: 0.0,
            end_ts_ms: c_to_ms(30.0),
        };
        let res = classify_range(&range, &bmap);
        assert_eq!(res.len(), 1);
        let incident = res.get(0).unwrap();
        assert_eq!(&incident.incident_classification, "Momentary:Swell");
        let range = Range {
            end_idx: (s_to_c(3.0)) as usize,
            end_ts_ms: c_to_ms(s_to_c(3.0)),
            ..range
        };
        let res = classify_range(&range, &bmap);
        assert_eq!(res.len(), 1);
        let incident = res.get(0).unwrap();
        assert_eq!(&incident.incident_classification, "Momentary:Swell");
    }
}
