const C_PER_S: f64 = 60.0;
const C_PER_MS: f64 = 0.06;
const MS_PER_S: f64 = 1_000.0;

#[inline]
pub fn s_to_ms(s: f64) -> f64 {
    s * MS_PER_S
}

#[inline]
pub fn s_to_c(s: f64) -> f64 {
    s * C_PER_S
}

#[inline]
pub fn ms_to_s(ms: f64) -> f64 {
    ms / MS_PER_S
}

#[inline]
pub fn ms_to_c(ms: f64) -> f64 {
    ms * C_PER_MS
}

#[inline]
pub fn c_to_s(c: f64) -> f64 {
    c / C_PER_S
}

#[inline]
pub fn c_to_ms(c: f64) -> f64 {
    c / C_PER_MS
}

#[inline]
pub fn ms_plus_c(ms: f64, c: f64) -> f64 {
    ms + c_to_ms(c)
}

#[inline]
pub fn percent_nominal_to_rms(percent_nominal: f64) -> f64 {
    (percent_nominal * 120.0) / 100.0
}

#[inline]
pub fn pu_to_rms(pu: f64) -> f64 {
    120.0 * pu
}

#[cfg(test)]
mod tests {
    use crate::analysis::*;

    #[test]
    fn test_s_to_ms() {
        assert_eq!(s_to_ms(1.0), 1_000.0);
    }

    #[test]
    fn test_s_to_c() {
        assert_eq!(s_to_c(1.0), 60.0);
    }

    #[test]
    fn test_ms_to_s() {
        assert_eq!(ms_to_s(1_000.0), 1.0);
        assert_eq!(ms_to_s(500.0), 0.5);
    }

    #[test]
    fn test_ms_to_c() {
        assert_eq!(ms_to_c(1_000.0), 60.0)
    }

    #[test]
    fn test_c_to_s() {
        assert_eq!(c_to_s(60.0), 1.0)
    }

    #[test]
    fn test_c_to_ms() {
        assert_eq!(c_to_ms(60.0), 1_000.0)
    }

    #[test]
    fn test_ms_plus_c() {
        assert_eq!(ms_plus_c(0.0, 60.0), 1_000.0)
    }

    #[test]
    fn test_percent_nominal_to_rms() {
        assert_eq!(percent_nominal_to_rms(100.0), 120.0)
    }

    #[test]
    fn test_pu_to_rms() {
        assert_eq!(pu_to_rms(1.0), 120.0);
        assert_eq!(pu_to_rms(0.1), 12.0);
        assert_eq!(pu_to_rms(1.1), 132.0);
    }
}
