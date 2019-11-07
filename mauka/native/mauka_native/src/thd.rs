use crate::arrays;
use crate::arrays::Range;
use rustfft::num_complex::Complex32;
use rustfft::FFTplanner;
use rustfft::FFT;
use std::sync::Arc;

const SAMPLES_PER_CYCLE: usize = 200;
const CYCLES_PER_SEC: usize = 60;
const SAMPLING_RATE: usize = CYCLES_PER_SEC * SAMPLES_PER_CYCLE;
const SAMPLES_PER_WINDOW: usize = SAMPLES_PER_CYCLE;

#[derive(Debug, Clone, Default)]
pub struct ThdIncident {
    pub start_time_ms: f64,
    pub end_time_ms: f64,
}

impl From<&arrays::Range> for ThdIncident {
    fn from(range: &Range) -> Self {
        ThdIncident {
            start_time_ms: range.start_ts_ms,
            end_time_ms: range.end_ts_ms,
        }
    }
}

pub fn thd(start_time_ms: f64, thd_threshold_percent: f64, samples: Vec<f32>) -> Vec<ThdIncident> {
    let thds: Vec<f64> = percent_thd(samples).iter().map(|i| *i as f64).collect();
    let bound = arrays::Bound::new(thd_threshold_percent, 0.0, None).set_no_upper();
    let ranges = arrays::bounded_ranges(start_time_ms, &thds, &vec![&bound]);
    ranges.iter().map(|range| range.into()).collect()
}

fn percent_thd(samples: Vec<f32>) -> Vec<f32> {
    let samples_len = samples.len();

    // Not enough samples
    if samples_len < SAMPLES_PER_CYCLE {
        vec![]
    }
    // Enough samples to make up an entire window
    else {
        let samples: Vec<Complex32> = samples.iter().map(|s| Complex32::new(*s, 0.0)).collect();
        let mut planner = FFTplanner::new(false);
        let fft = planner.plan_fft(SAMPLES_PER_WINDOW);
        let mut thds: Vec<f32> = vec![];
        let windows = samples_len / SAMPLES_PER_WINDOW;
        for i in 0..windows {
            let start_idx = i * SAMPLES_PER_WINDOW;
            let end_idx = start_idx + SAMPLES_PER_WINDOW;
            let window = samples[start_idx..end_idx].to_vec();
            thds.push(thd_window(window, fft.clone()));
        }

        thds
    }
}

fn thd_window(mut window: Vec<Complex32>, fft: Arc<dyn FFT<f32>>) -> f32 {
    let mut spectrum = vec![Complex32::new(0.0, 0.0); window.len()];

    fft.process(&mut window, &mut spectrum);

    let fft_resolution = (SAMPLING_RATE as f32) / (spectrum.len() as f32);
    let sixty_hz_bin = (CYCLES_PER_SEC as f32 / fft_resolution) as usize;

    let sixty_hz_power = spectrum[sixty_hz_bin].norm_sqr().sqrt();
    let mut harmonics = 0f32;

    for i in (sixty_hz_bin * 2..spectrum.len() / 2).step_by(sixty_hz_bin) {
        harmonics += spectrum[i].norm_sqr();
    }

    harmonics.sqrt() / sixty_hz_power * 100.0
}

#[cfg(test)]
mod tests {
    use crate::test_utils::{add_signals, close_to, sin, square_wave, thd_signal};
    use crate::thd::{percent_thd, CYCLES_PER_SEC, SAMPLES_PER_WINDOW};

    // We can use the fact that a 50% duty cycle square wave generates THD at 48.3%
    // https://www.allaboutcircuits.com/technical-articles/the-importance-of-total-harmonic-distortion/
    #[test]
    fn percent_thd_one_window_sq() {
        let samples = square_wave(1.0, 60.0, 12_000.0, SAMPLES_PER_WINDOW);
        let thds = percent_thd(samples);
        assert_eq!(thds.len(), 1);
        assert!(close_to(thds[0], 48.3, 0.1));
    }

    #[test]
    fn percent_thd_two_windows_sq() {
        let samples = square_wave(1.0, 60.0, 12_000.0, SAMPLES_PER_WINDOW * 2);
        let thds = percent_thd(samples);
        assert_eq!(thds.len(), 2);
        assert!(close_to(thds[0], 48.3, 0.1));
        assert!(close_to(thds[1], 48.3, 0.1));
    }

    #[test]
    fn percent_thd_one_window_50() {
        let samples = thd_signal(50.0, SAMPLES_PER_WINDOW);
        let thds = percent_thd(samples);
        assert_eq!(thds.len(), 1);
        let thd = thds[0];
        assert!(close_to(thd, 50.0, 0.01));
    }

    #[test]
    fn percent_thd_one_window_6() {
        let samples = thd_signal(6.0, SAMPLES_PER_WINDOW);
        let thds = percent_thd(samples);
        assert_eq!(thds.len(), 1);
        let thd = thds[0];
        assert!(close_to(thd, 6.0, 0.01));
    }

    #[test]
    fn percent_thd_one_window_1() {
        let samples = thd_signal(1.0, SAMPLES_PER_WINDOW);
        let thds = percent_thd(samples);
        assert_eq!(thds.len(), 1);
        let thd = thds[0];
        assert!(close_to(thd, 1.0, 0.01));
    }

    #[test]
    fn percent_thd_two_window_6() {
        let samples = thd_signal(6.0, SAMPLES_PER_WINDOW * 2);
        let thds = percent_thd(samples);
        assert_eq!(thds.len(), 2);
        let thd = thds[0];
        assert!(close_to(thd, 6.0, 0.01));
        let thd = thds[1];
        assert!(close_to(thd, 6.0, 0.01));
    }
}
