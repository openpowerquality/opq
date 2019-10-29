pub fn rust_ranges(data: Vec<f64>, ranges: Vec<Vec<f64>>) -> Vec<Vec<f64>> {
    let mut ranges_result: Vec<Vec<f64>> = vec![];
    for _ in 0..ranges.len() {
        ranges_result.push(vec![]);
    }

    for (i, v) in data.iter().enumerate() {
        for (r, range) in ranges.iter().enumerate() {
            let range_result = &mut ranges_result[r];
            let min_v = range[0];
            let max_v = range[1];

            if *v >= min_v && *v <= max_v {
                if range_result.len() % 2 == 0 {
                    range_result.push(i as f64);
                }
            } else {
                if range_result.len() % 2 == 1 {
                    range_result.push((i - 1) as f64);
                }
            }

            if i == data.len() - 1 && range_result.len() % 2 == 1 {
                range_result.push(i as f64);
            }
        }
    }

    ranges_result
}

#[cfg(test)]
mod tests {
    use crate::native::arrays::rust_ranges;

    fn is_empty(ranges: &Vec<Vec<f64>>) -> bool {
        for range in ranges {
            if !range.is_empty() {
                return false;
            }
        }
        true
    }

    #[test]
    fn empty_values() {
        assert!(is_empty(&rust_ranges(vec![], vec![vec![0.0, 0.0]])))
    }

    #[test]
    fn empty_ranges() {
        assert!(is_empty(&rust_ranges(vec![0.0, 1.0], vec![])))
    }

    #[test]
    fn all_outside() {
        let vs = vec![-1.0, 0.0, 1.0];
        let r = vec![vec![1.1, 2.0]];
        assert!(is_empty(&rust_ranges(vs, r)))
    }

    #[test]
    fn all_inside() {
        let vs = vec![-1.0, 0.0, 1.0];
        let r = vec![vec![-1.1, 1.1]];
        let ranges = rust_ranges(vs, r);
        let range = ranges.get(0).unwrap();

        assert_eq!(ranges.len(), 1);
        assert_eq!(range.len(), 2);
        assert_eq!(range[0], 0.0);
        assert_eq!(range[1], 2.0);
    }

    #[test]
    fn start() {
        let vs = vec![-2.0, -1.0, 0.0, 1.0, 2.0];
        let r = vec![vec![-2.1, -0.5]];
        let ranges = rust_ranges(vs, r);
        let range = ranges.get(0).unwrap();

        assert_eq!(ranges.len(), 1);
        assert_eq!(range.len(), 2);
        assert_eq!(range[0], 0.0);
        assert_eq!(range[1], 1.0);
    }

    #[test]
    fn middle() {
        let vs = vec![-2.0, -1.0, 0.0, 1.0, 2.0];
        let r = vec![vec![-1.1, 1.1]];
        let ranges = rust_ranges(vs, r);
        let range = ranges.get(0).unwrap();

        assert_eq!(ranges.len(), 1);
        assert_eq!(range.len(), 2);
        assert_eq!(range[0], 1.0);
        assert_eq!(range[1], 3.0);
    }

    #[test]
    fn end() {
        let vs = vec![-2.0, -1.0, 0.0, 1.0, 2.0];
        let r = vec![vec![0.5, 2.1]];
        let ranges = rust_ranges(vs, r);
        let range = ranges.get(0).unwrap();

        assert_eq!(ranges.len(), 1);
        assert_eq!(range.len(), 2);
        assert_eq!(range[0], 3.0);
        assert_eq!(range[1], 4.0);
    }

    #[test]
    fn two_ranges() {
        let vs = vec![-3.0, -2.0, -1.0, 0.0, 1.0, 2.0, 3.0];
        let r = vec![vec![-2.1, -0.5], vec![0.5, 2.1]];
        let ranges = rust_ranges(vs, r);

        assert_eq!(ranges.len(), 2);
        let low_range = ranges.get(0).unwrap();
        let high_range = ranges.get(1).unwrap();

        assert_eq!(low_range.len(), 2);
        assert_eq!(high_range.len(), 2);
        assert_eq!(low_range[0], 1.0);
        assert_eq!(low_range[1], 2.0);
        assert_eq!(high_range[0], 4.0);
        assert_eq!(high_range[1], 5.0);
    }

    #[test]
    fn two_results_one_range() {
        let vs = vec![-3.0, -2.0, -1.0, 0.0, 1.0, 2.0, 0.0, 0.0, 3.0];
        let r = vec![vec![-1.0, 1.0]];
        let ranges = rust_ranges(vs, r);

        assert_eq!(ranges.len(), 1);
        let range = ranges.get(0).unwrap();
        assert_eq!(range.len(), 4);
        assert_eq!(range[0], 2.0);
        assert_eq!(range[1], 4.0);
        assert_eq!(range[2], 6.0);
        assert_eq!(range[3], 7.0);
    }

    #[test]
    fn overlapping() {
        let vs = vec![-3.0, -2.0, -1.0, 0.0, 1.0, 2.0, 3.0];
        let r = vec![vec![-1.5, 0.5], vec![-0.5, 1.5]];
        let ranges = rust_ranges(vs, r);

        assert_eq!(ranges.len(), 2);
        let low_range = ranges.get(0).unwrap();
        let high_range = ranges.get(1).unwrap();

        assert_eq!(low_range.len(), 2);
        assert_eq!(high_range.len(), 2);
        assert_eq!(low_range[0], 2.0);
        assert_eq!(low_range[1], 3.0);
        assert_eq!(high_range[0], 3.0);
        assert_eq!(high_range[1], 4.0);
    }

    #[test]
    fn contains() {
        let vs = vec![-3.0, -2.0, -1.0, 0.0, 1.0, 2.0, 3.0];
        let r = vec![vec![-0.5, 0.5], vec![-1.0, 1.0]];
        let ranges = rust_ranges(vs, r);

        assert_eq!(ranges.len(), 2);
        let low_range = ranges.get(0).unwrap();
        let high_range = ranges.get(1).unwrap();

        assert_eq!(low_range.len(), 2);
        assert_eq!(high_range.len(), 2);
        assert_eq!(low_range[0], 3.0);
        assert_eq!(low_range[1], 3.0);
        assert_eq!(high_range[0], 2.0);
        assert_eq!(high_range[1], 4.0);
    }
}
