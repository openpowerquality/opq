use crate::analysis::*;
use std::collections::HashMap;
use std::hash::{Hash, Hasher};

#[derive(Debug)]
pub struct Bound {
    pub key: String,
    pub min: f64,
    pub max: f64,
    lt_max: bool,
    no_upper: bool,
}

impl Bound {
    pub fn new(min: f64, max: f64, value_transform: Option<&dyn Fn(f64) -> f64>) -> Bound {
        let min = value_transform.map(|f| f(min)).unwrap_or(min);
        let max = value_transform.map(|f| f(max)).unwrap_or(max);
        Bound {
            key: format!("{},{}", min, max),
            min,
            max,
            lt_max: false,
            no_upper: false,
        }
    }

    pub fn set_lt_max(mut self) -> Self {
        self.lt_max = true;
        self
    }

    pub fn set_no_upper(mut self) -> Self {
        self.no_upper = true;
        self
    }

    pub fn contains(&self, v: f64) -> bool {
        if self.no_upper {
            v >= self.min
        } else if self.lt_max {
            v >= self.min && v < self.max
        } else {
            v >= self.min && v <= self.max
        }
    }
}

impl Hash for Bound {
    fn hash<H: Hasher>(&self, state: &mut H) {
        self.key.hash(state)
    }
}

impl PartialEq for Bound {
    fn eq(&self, other: &Self) -> bool {
        self.min == other.min && self.max == other.max
    }
}

impl Eq for Bound {}

impl From<&Vec<f64>> for Bound {
    fn from(v: &Vec<f64>) -> Self {
        Bound::new(v[0], v[1], None)
    }
}

#[derive(Debug)]
pub struct Range {
    pub bound: Bound,
    pub start_idx: usize,
    pub end_idx: usize,
    pub start_ts_ms: f64,
    pub end_ts_ms: f64,
}

impl Range {
    pub fn new(min_val: f64, max_val: f64, start_idx: usize, start_ts_ms: f64) -> Range {
        Range {
            bound: Bound::new(min_val, max_val, None),
            start_idx,
            end_idx: start_idx + 1,
            start_ts_ms,
            end_ts_ms: ms_plus_c(start_ts_ms, 1.0),
        }
    }

    pub fn update(&mut self, idx: usize) {
        self.end_idx = idx;
        self.end_ts_ms = ms_plus_c(self.start_ts_ms, self.range_c());
    }

    pub fn range_c(&self) -> f64 {
        (self.end_idx - self.start_idx) as f64
    }

    pub fn range_ms(&self) -> f64 {
        c_to_ms(self.range_c())
    }

    pub fn range_s(&self) -> f64 {
        c_to_s(self.range_c())
    }

    pub fn print(&self) {
        println!("{:#?}", self);
    }
}

pub fn bounded_ranges(start_ts_ms: f64, data: &Vec<f64>, bounds: &Vec<&Bound>) -> Vec<Range> {
    let mut range_map: HashMap<&Bound, Range> = HashMap::new();
    let mut range_results = vec![];

    for (i, v) in data.iter().enumerate() {
        for bound in bounds {
            if bound.contains(*v) {
                range_map.entry(bound).or_insert_with(|| {
                    Range::new(bound.min, bound.max, i, ms_plus_c(start_ts_ms, i as f64))
                });
            } else if let Some(mut range) = range_map.remove(bound) {
                range.update(i);
                range_results.push(range);
            }
            if i == data.len() - 1 {
                if let Some(mut range) = range_map.remove(bound) {
                    range.update(i + 1);
                    range_results.push(range);
                }
            }
        }
    }
    range_results
}

#[cfg(test)]
mod tests {
    use crate::analysis::*;
    use crate::arrays::{bounded_ranges, Bound, Range};

    // Range tests
    #[test]
    fn test_range_creation_from_0_idx() {
        let range = Range::new(-1.0, 1.0, 0, 0.0);
        assert_eq!(range.bound, Bound::new(-1.0, 1.0, None));
        assert_eq!(range.start_idx, 0);
        assert_eq!(range.end_idx, 1);
        assert_eq!(range.start_ts_ms, 0.0);
        assert_eq!(range.end_ts_ms, c_to_ms(1.0));
        assert_eq!(range.range_c(), 1.0);
        assert_eq!(range.range_ms(), c_to_ms(range.range_c()));
        assert_eq!(range.range_s(), c_to_s(range.range_c()));
    }

    #[test]
    fn test_range_creation_from_1_idx() {
        let range = Range::new(-1.0, 1.0, 1, 0.0);
        assert_eq!(range.bound, Bound::new(-1.0, 1.0, None));
        assert_eq!(range.start_idx, 1);
        assert_eq!(range.end_idx, 2);
        assert_eq!(range.start_ts_ms, 0.0);
        assert_eq!(range.end_ts_ms, c_to_ms(1.0));
        assert_eq!(range.range_c(), 1.0);
        assert_eq!(range.range_ms(), c_to_ms(range.range_c()));
        assert_eq!(range.range_s(), c_to_s(range.range_c()));
    }

    #[test]
    fn test_range_creation_from_0_with_non_zero_start_time() {
        let range = Range::new(-1.0, 1.0, 0, 1.0);
        assert_eq!(range.bound, Bound::new(-1.0, 1.0, None));
        assert_eq!(range.start_idx, 0);
        assert_eq!(range.end_idx, 1);
        assert_eq!(range.start_ts_ms, 1.0);
        assert_eq!(
            range.end_ts_ms,
            ms_plus_c(range.start_ts_ms, range.range_c())
        );
        assert_eq!(range.range_c(), 1.0);
        assert_eq!(range.range_ms(), c_to_ms(range.range_c()));
        assert_eq!(range.range_s(), c_to_s(range.range_c()));
    }

    #[test]
    fn test_range_creation_from_1_with_non_zero_start_time() {
        let range = Range::new(-1.0, 1.0, 1, 1.0);
        assert_eq!(range.bound, Bound::new(-1.0, 1.0, None));
        assert_eq!(range.start_idx, 1);
        assert_eq!(range.end_idx, 2);
        assert_eq!(range.start_ts_ms, 1.0);
        assert_eq!(
            range.end_ts_ms,
            ms_plus_c(range.start_ts_ms, range.range_c())
        );
        assert_eq!(range.range_c(), 1.0);
        assert_eq!(range.range_ms(), c_to_ms(range.range_c()));
        assert_eq!(range.range_s(), c_to_s(range.range_c()));
    }

    #[test]
    fn test_range_update_single_from_idx_0() {
        let mut range = Range::new(-1.0, 1.0, 0, 0.0);
        range.update(2);
        assert_eq!(range.bound, Bound::new(-1.0, 1.0, None));
        assert_eq!(range.start_idx, 0);
        assert_eq!(range.end_idx, 2);
        assert_eq!(range.start_ts_ms, 0.0);
        assert_eq!(
            range.end_ts_ms,
            ms_plus_c(range.start_ts_ms, range.range_c())
        );
        assert_eq!(range.range_c(), 2.0);
        assert_eq!(range.range_ms(), c_to_ms(range.range_c()));
        assert_eq!(range.range_s(), c_to_s(range.range_c()));
    }

    #[test]
    fn test_range_update_single_from_idx_1() {
        let mut range = Range::new(-1.0, 1.0, 1, 0.0);
        range.update(3);
        assert_eq!(range.bound, Bound::new(-1.0, 1.0, None));
        assert_eq!(range.start_idx, 1);
        assert_eq!(range.end_idx, 3);
        assert_eq!(range.start_ts_ms, 0.0);
        assert_eq!(
            range.end_ts_ms,
            ms_plus_c(range.start_ts_ms, range.range_c())
        );
        assert_eq!(range.range_c(), 2.0);
        assert_eq!(range.range_ms(), c_to_ms(range.range_c()));
        assert_eq!(range.range_s(), c_to_s(range.range_c()));
    }

    #[test]
    fn test_range_update_single_from_idx_0_non_zero_time() {
        let mut range = Range::new(-1.0, 1.0, 0, 1.0);
        range.update(2);
        assert_eq!(range.bound, Bound::new(-1.0, 1.0, None));
        assert_eq!(range.start_idx, 0);
        assert_eq!(range.end_idx, 2);
        assert_eq!(range.start_ts_ms, 1.0);
        assert_eq!(
            range.end_ts_ms,
            ms_plus_c(range.start_ts_ms, range.range_c())
        );
        assert_eq!(range.range_c(), 2.0);
        assert_eq!(range.range_ms(), c_to_ms(range.range_c()));
        assert_eq!(range.range_s(), c_to_s(range.range_c()));
    }

    #[test]
    fn test_range_update_single_from_idx_1_non_zero_time() {
        let mut range = Range::new(-1.0, 1.0, 1, 1.0);
        range.update(3);
        assert_eq!(range.bound, Bound::new(-1.0, 1.0, None));
        assert_eq!(range.start_idx, 1);
        assert_eq!(range.end_idx, 3);
        assert_eq!(range.start_ts_ms, 1.0);
        assert_eq!(
            range.end_ts_ms,
            ms_plus_c(range.start_ts_ms, range.range_c())
        );
        assert_eq!(range.range_c(), 2.0);
        assert_eq!(range.range_ms(), c_to_ms(range.range_c()));
        assert_eq!(range.range_s(), c_to_s(range.range_c()));
    }

    #[test]
    fn test_range_update_multi_from_idx_0() {
        let mut range = Range::new(-1.0, 1.0, 0, 0.0);
        range.update(3);
        assert_eq!(range.bound, Bound::new(-1.0, 1.0, None));
        assert_eq!(range.start_idx, 0);
        assert_eq!(range.end_idx, 3);
        assert_eq!(range.start_ts_ms, 0.0);
        assert_eq!(
            range.end_ts_ms,
            ms_plus_c(range.start_ts_ms, range.range_c())
        );
        assert_eq!(range.range_c(), 3.0);
        assert_eq!(range.range_ms(), c_to_ms(range.range_c()));
        assert_eq!(range.range_s(), c_to_s(range.range_c()));
    }

    // Bounded ranges tests
    #[test]
    fn empty_values() {
        let vs = vec![];
        let r = vec![vec![1.1, 2.0]];
        let r: Vec<Bound> = r.iter().map(|a| a.into()).collect();
        let r: Vec<&Bound> = r.iter().map(|a| a).collect();
        assert!(bounded_ranges(0.0, &vs, &r).is_empty())
    }

    #[test]
    fn empty_ranges() {
        let vs = vec![0.0, 1.0];
        let r: Vec<Vec<f64>> = vec![];
        let r: Vec<Bound> = r.iter().map(|a| a.into()).collect();
        let r: Vec<&Bound> = r.iter().map(|a| a).collect();
        assert!(bounded_ranges(0.0, &vs, &r).is_empty())
    }

    #[test]
    fn all_outside() {
        let vs = vec![-1.0, 0.0, 1.0];
        let r = vec![vec![1.1, 2.0]];
        let r: Vec<Bound> = r.iter().map(|a| a.into()).collect();
        let r: Vec<&Bound> = r.iter().map(|a| a).collect();
        assert!(bounded_ranges(0.0, &vs, &r).is_empty())
    }
    #[test]
    fn all_inside() {
        let vs = vec![-1.0, 0.0, 1.0];
        let r = vec![vec![-1.1, 1.1]];
        let r: Vec<Bound> = r.iter().map(|a| a.into()).collect();
        let r: Vec<&Bound> = r.iter().map(|a| a).collect();
        let ranges = bounded_ranges(0.0, &vs, &r);
        let range = ranges.get(0).unwrap();

        assert_eq!(ranges.len(), 1);
        assert_eq!(range.bound, Bound::new(-1.1, 1.1, None));
        assert_eq!(range.start_idx, 0);
        assert_eq!(range.end_idx, 3);
        assert_eq!(range.start_ts_ms, 0.0);
        assert_eq!(
            range.end_ts_ms,
            ms_plus_c(range.start_ts_ms, range.range_c())
        );
        assert_eq!(range.range_c(), 3.0);
        assert_eq!(range.range_ms(), c_to_ms(range.range_c()));
        assert_eq!(range.range_s(), c_to_s(range.range_c()));
    }

    #[test]
    fn start() {
        let vs = vec![-2.0, -1.0, 0.0, 1.0, 2.0];
        let r = vec![vec![-2.1, -0.5]];
        let r: Vec<Bound> = r.iter().map(|a| a.into()).collect();
        let r: Vec<&Bound> = r.iter().map(|a| a).collect();
        let ranges = bounded_ranges(0.0, &vs, &r);
        let range = ranges.get(0).unwrap();
        assert_eq!(ranges.len(), 1);
        assert_eq!(range.bound, Bound::new(-2.1, -0.5, None));
        assert_eq!(range.start_idx, 0);
        assert_eq!(range.end_idx, 2);
        assert_eq!(range.start_ts_ms, 0.0);
        assert_eq!(
            range.end_ts_ms,
            ms_plus_c(range.start_ts_ms, range.range_c())
        );
        assert_eq!(range.range_c(), 2.0);
        assert_eq!(range.range_ms(), c_to_ms(range.range_c()));
        assert_eq!(range.range_s(), c_to_s(range.range_c()));
    }

    #[test]
    fn middle() {
        let vs = vec![-2.0, -1.0, 0.0, 1.0, 2.0];
        let r = vec![vec![-1.1, 1.1]];
        let r: Vec<Bound> = r.iter().map(|a| a.into()).collect();
        let r: Vec<&Bound> = r.iter().map(|a| a).collect();
        let ranges = bounded_ranges(0.0, &vs, &r);
        let range = ranges.get(0).unwrap();
        assert_eq!(ranges.len(), 1);
        assert_eq!(range.bound, Bound::new(-1.1, 1.1, None));
        assert_eq!(range.start_idx, 1);
        assert_eq!(range.end_idx, 4);
        assert_eq!(range.start_ts_ms, c_to_ms(1.0));
        assert_eq!(
            range.end_ts_ms,
            ms_plus_c(range.start_ts_ms, range.range_c())
        );
        assert_eq!(range.range_c(), 3.0);
        assert_eq!(range.range_ms(), c_to_ms(range.range_c()));
        assert_eq!(range.range_s(), c_to_s(range.range_c()));
    }

    #[test]
    fn end() {
        let vs = vec![-2.0, -1.0, 0.0, 1.0, 2.0];
        let r = vec![vec![0.5, 2.1]];
        let r: Vec<Bound> = r.iter().map(|a| a.into()).collect();
        let r: Vec<&Bound> = r.iter().map(|a| a).collect();
        let ranges = bounded_ranges(0.0, &vs, &r);
        let range = ranges.get(0).unwrap();
        let range_len = 2.0;
        assert_eq!(ranges.len(), 1);
        assert_eq!(range.bound, Bound::new(0.5, 2.1, None));
        assert_eq!(range.start_idx, 3);
        assert_eq!(range.end_idx, 5);
        assert_eq!(range.start_ts_ms, c_to_ms(3.0));
        assert_eq!(
            range.end_ts_ms,
            ms_plus_c(range.start_ts_ms, range.range_c())
        );
        assert_eq!(range.range_c(), 2.0);
        assert_eq!(range.range_ms(), c_to_ms(range.range_c()));
        assert_eq!(range.range_s(), c_to_s(range.range_c()));
    }

    #[test]
    fn middle_with_ts() {
        let vs = vec![-2.0, -1.0, 0.0, 1.0, 2.0];
        let r = vec![vec![-1.1, 1.1]];
        let r: Vec<Bound> = r.iter().map(|a| a.into()).collect();
        let r: Vec<&Bound> = r.iter().map(|a| a).collect();
        let ranges = bounded_ranges(1.0, &vs, &r);
        let range = ranges.get(0).unwrap();
        assert_eq!(ranges.len(), 1);
        assert_eq!(range.bound, Bound::new(-1.1, 1.1, None));
        assert_eq!(range.start_idx, 1);
        assert_eq!(range.end_idx, 4);
        assert_eq!(range.start_ts_ms, ms_plus_c(1.0, 1.0));
        assert_eq!(
            range.end_ts_ms,
            ms_plus_c(range.start_ts_ms, range.range_c())
        );
        assert_eq!(range.range_c(), 3.0);
        assert_eq!(range.range_ms(), c_to_ms(range.range_c()));
        assert_eq!(range.range_s(), c_to_s(range.range_c()));
    }

    #[test]
    fn two_ranges() {
        let vs = vec![-3.0, -2.0, -1.0, 0.0, 1.0, 2.0, 3.0];
        let r = vec![vec![-2.1, -0.5], vec![0.5, 2.1]];
        let r: Vec<Bound> = r.iter().map(|a| a.into()).collect();
        let r: Vec<&Bound> = r.iter().map(|a| a).collect();
        let ranges = bounded_ranges(0.0, &vs, &r);
        assert_eq!(ranges.len(), 2);

        let lower_range = ranges.get(0).unwrap();
        assert_eq!(lower_range.bound, Bound::new(-2.1, -0.5, None));
        assert_eq!(lower_range.start_idx, 1);
        assert_eq!(lower_range.end_idx, 3);
        assert_eq!(lower_range.start_ts_ms, c_to_ms(1.0));
        assert_eq!(
            lower_range.end_ts_ms,
            ms_plus_c(lower_range.start_ts_ms, lower_range.range_c())
        );
        assert_eq!(lower_range.range_c(), 2.0);
        assert_eq!(lower_range.range_ms(), c_to_ms(lower_range.range_c()));
        assert_eq!(lower_range.range_s(), c_to_s(lower_range.range_c()));

        let upper_range = ranges.get(1).unwrap();
        assert_eq!(upper_range.bound, Bound::new(0.5, 2.1, None));
        assert_eq!(upper_range.start_idx, 4);
        assert_eq!(upper_range.end_idx, 6);
        assert_eq!(upper_range.start_ts_ms, c_to_ms(4.0));
        assert_eq!(
            upper_range.end_ts_ms,
            ms_plus_c(upper_range.start_ts_ms, upper_range.range_c())
        );
        assert_eq!(upper_range.range_c(), 2.0);
        assert_eq!(upper_range.range_ms(), c_to_ms(upper_range.range_c()));
        assert_eq!(upper_range.range_s(), c_to_s(upper_range.range_c()));
    }

    #[test]
    fn two_results_one_range() {
        let vs = vec![-3.0, -2.0, -1.0, 0.0, 1.0, 2.0, 0.0, 0.0, 3.0];
        let r = vec![vec![-1.0, 1.0]];
        let r: Vec<Bound> = r.iter().map(|a| a.into()).collect();
        let r: Vec<&Bound> = r.iter().map(|a| a).collect();
        let ranges = bounded_ranges(0.0, &vs, &r);
        assert_eq!(ranges.len(), 2);

        let lower_range = ranges.get(0).unwrap();
        assert_eq!(lower_range.bound, Bound::new(-1.0, 1.0, None));
        assert_eq!(lower_range.start_idx, 2);
        assert_eq!(lower_range.end_idx, 5);
        assert_eq!(lower_range.start_ts_ms, c_to_ms(2.0));
        assert_eq!(
            lower_range.end_ts_ms,
            ms_plus_c(lower_range.start_ts_ms, lower_range.range_c())
        );
        assert_eq!(lower_range.range_c(), 3.0);
        assert_eq!(lower_range.range_ms(), c_to_ms(lower_range.range_c()));
        assert_eq!(lower_range.range_s(), c_to_s(lower_range.range_c()));

        let upper_range = ranges.get(1).unwrap();
        assert_eq!(lower_range.bound, Bound::new(-1.0, 1.0, None));
        assert_eq!(upper_range.start_idx, 6);
        assert_eq!(upper_range.end_idx, 8);
        assert_eq!(upper_range.start_ts_ms, c_to_ms(6.0));
        assert_eq!(
            upper_range.end_ts_ms,
            ms_plus_c(upper_range.start_ts_ms, upper_range.range_c())
        );
        assert_eq!(upper_range.range_c(), 2.0);
        assert_eq!(upper_range.range_ms(), c_to_ms(upper_range.range_c()));
        assert_eq!(upper_range.range_s(), c_to_s(upper_range.range_c()));
    }

    #[test]
    fn overlapping() {
        let vs = vec![-3.0, -2.0, -1.0, 0.0, 1.0, 2.0, 3.0];
        let r = vec![vec![-1.5, 0.5], vec![-0.5, 1.5]];
        let r: Vec<Bound> = r.iter().map(|a| a.into()).collect();
        let r: Vec<&Bound> = r.iter().map(|a| a).collect();
        let ranges = bounded_ranges(0.0, &vs, &r);
        assert_eq!(ranges.len(), 2);

        let lower_range = ranges.get(0).unwrap();
        assert_eq!(lower_range.bound, Bound::new(-1.5, 0.5, None));
        assert_eq!(lower_range.start_idx, 2);
        assert_eq!(lower_range.end_idx, 4);
        assert_eq!(lower_range.start_ts_ms, c_to_ms(2.0));
        assert_eq!(
            lower_range.end_ts_ms,
            ms_plus_c(lower_range.start_ts_ms, lower_range.range_c())
        );
        assert_eq!(lower_range.range_c(), 2.0);
        assert_eq!(lower_range.range_ms(), c_to_ms(lower_range.range_c()));
        assert_eq!(lower_range.range_s(), c_to_s(lower_range.range_c()));

        let upper_range = ranges.get(1).unwrap();
        assert_eq!(upper_range.bound, Bound::new(-0.5, 1.5, None));
        assert_eq!(upper_range.start_idx, 3);
        assert_eq!(upper_range.end_idx, 5);
        assert_eq!(upper_range.start_ts_ms, c_to_ms(3.0));
        assert_eq!(
            upper_range.end_ts_ms,
            ms_plus_c(upper_range.start_ts_ms, upper_range.range_c())
        );
        assert_eq!(upper_range.range_c(), 2.0);
        assert_eq!(upper_range.range_ms(), c_to_ms(upper_range.range_c()));
        assert_eq!(upper_range.range_s(), c_to_s(upper_range.range_c()));
    }

    #[test]
    fn contains() {
        let vs = vec![-3.0, -2.0, -1.0, 0.0, 1.0, 2.0, 3.0];
        let r = vec![vec![-0.5, 0.5], vec![-1.0, 1.0]];
        let r: Vec<Bound> = r.iter().map(|a| a.into()).collect();
        let r: Vec<&Bound> = r.iter().map(|a| a).collect();
        let ranges = bounded_ranges(0.0, &vs, &r);
        assert_eq!(ranges.len(), 2);

        let lower_range = ranges.get(0).unwrap();
        assert_eq!(lower_range.bound, Bound::new(-0.5, 0.5, None));
        assert_eq!(lower_range.start_idx, 3);
        assert_eq!(lower_range.end_idx, 4);
        assert_eq!(lower_range.start_ts_ms, c_to_ms(3.0));
        assert_eq!(
            lower_range.end_ts_ms,
            ms_plus_c(lower_range.start_ts_ms, lower_range.range_c())
        );
        assert_eq!(lower_range.range_c(), 1.0);
        assert_eq!(lower_range.range_ms(), c_to_ms(lower_range.range_c()));
        assert_eq!(lower_range.range_s(), c_to_s(lower_range.range_c()));

        let upper_range = ranges.get(1).unwrap();
        assert_eq!(upper_range.bound, Bound::new(-1.0, 1.0, None));
        assert_eq!(upper_range.start_idx, 2);
        assert_eq!(upper_range.end_idx, 5);
        assert_eq!(upper_range.start_ts_ms, c_to_ms(2.0));
        assert_eq!(
            upper_range.end_ts_ms,
            ms_plus_c(upper_range.start_ts_ms, upper_range.range_c())
        );
        assert_eq!(upper_range.range_c(), 3.0);
        assert_eq!(upper_range.range_ms(), c_to_ms(upper_range.range_c()));
        assert_eq!(upper_range.range_s(), c_to_s(upper_range.range_c()));
    }
}
