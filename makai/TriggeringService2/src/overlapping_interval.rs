use std::collections::BTreeMap;
use std::cmp::Ord;
use std::clone::Clone;

///This object is responsible for keeping track of previously requested raw data.
///If a the timestamp of a request compleatly overlaps with previous events, event will be logged,
///but no data will be requested. Otherwise, it's business as usuall.
pub struct OverlappingIntervals<T> {
    ///Binary tree map for efficient insertions and searches.
    intervals: BTreeMap<T, T>,
}

impl<T: Ord + Clone> OverlappingIntervals<T> {
    ///Creates a new `OverlappingIntervals` object.
    pub fn new() -> OverlappingIntervals<T> {
        OverlappingIntervals {
            intervals: BTreeMap::new(),
        }
    }
    ///Insert a new time interval. Will return false if the data has already been requested. True otherwise.
    pub fn insert_and_check(&mut self, start: T, end: T) -> bool {
        let mut new_interval_start = start;
        let mut new_interval_end = end;

        let mut intervals_to_remove = Vec::new();

        let mut overlapping = false;

        for (interval_start, interval_end) in self.intervals.iter() {
            if interval_end >= &new_interval_end && interval_start <= &new_interval_start {
                overlapping = true;
            } else if interval_end < &new_interval_end && interval_start > &new_interval_start {
                overlapping = true;
                intervals_to_remove.push(interval_start.clone());
            } else if interval_start < &new_interval_start && interval_end >= &new_interval_start {
                new_interval_start = interval_start.clone();
                intervals_to_remove.push(interval_start.clone());
                overlapping = true;
            } else if interval_end > &new_interval_end && interval_start <= &new_interval_end {
                new_interval_end = interval_end.clone();
                overlapping = true;
                intervals_to_remove.push(interval_start.clone());
            }
        }

        for ref key in intervals_to_remove.iter() {
            self.intervals.remove(key);
        }
        if intervals_to_remove.len() > 0 || !overlapping {
            self.intervals.insert(new_interval_start, new_interval_end);
            return true;
        }
        false
    }

    ///Clears the cache of event times up to `nuw_min`.
    pub fn clear_to(&mut self, new_min: T) {
        let mut intervals_to_remove = Vec::new();
        for (interval_start, _) in self.intervals.iter() {
            if interval_start < &new_min {
                intervals_to_remove.push(interval_start.clone());
            }
        }

        for ref key in intervals_to_remove.iter() {
            self.intervals.remove(key);
        }
    }
}


mod tests {
    use super::*;
    #[test]
    fn overlap_test() {
        let mut i = OverlappingIntervals::new();

        assert_eq!(i.insert_and_check(1, 2), true);
        assert_eq!(i.insert_and_check(3, 5), true);
        assert_eq!(i.insert_and_check(0, 10), true);
        assert_eq!(i.insert_and_check(-2, 9), true);
        assert_eq!(i.insert_and_check(11, 21), true);
        assert_eq!(i.insert_and_check(0, 2), false);
        assert_eq!(i.insert_and_check(20, 31), true);
    }
}