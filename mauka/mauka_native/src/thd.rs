use rustfft::num_complex::Complex32;
use rustfft::FFTplanner;
use rustfft::FFT;
use std::sync::Arc;

const SAMPLES_PER_CYCLE: usize = 200;
const CYCLES_PER_SEC: usize = 60;
const DEFAULT_WINDOW_COUNT: usize = 6;
const SAMPLING_RATE: usize = CYCLES_PER_SEC * SAMPLES_PER_CYCLE;
const SAMPLES_PER_WINDOW: usize = DEFAULT_WINDOW_COUNT * SAMPLES_PER_CYCLE;

pub fn percent_thd(samples: Vec<f32>) -> Vec<f32> {
    let samples: Vec<Complex32> = samples.iter().map(|s| Complex32::new(*s, 0.0)).collect();
    let mut planner = FFTplanner::new(false);
    let samples_len = samples.len();

    // Not enough samples to make up an entire window
    if samples_len < SAMPLES_PER_WINDOW {
        let thd = thd_window(samples, planner.plan_fft(samples_len));
        vec![thd]
    }
    // Enough samples to make up an entire window
    else {
        let fft = planner.plan_fft(DEFAULT_WINDOW_COUNT * SAMPLES_PER_CYCLE);
        let mut thds: Vec<f32> = vec![];
        let windows = samples_len / SAMPLES_PER_WINDOW;
        for i in 0..windows {
            let start_idx = i * SAMPLES_PER_WINDOW;
            let end_idx = start_idx + SAMPLES_PER_WINDOW;
            let window = samples[start_idx..end_idx].to_vec();
            thds.push(thd_window(window, fft.clone()));
        }

        // Now collect anything remaining
        let remaining_samples = samples_len % SAMPLES_PER_WINDOW;
        if remaining_samples > 0 {
            let remaining_window = samples[samples_len - remaining_samples..].to_vec();
            thds.push(thd_window(
                remaining_window,
                planner.plan_fft(remaining_samples),
            ));
        }

        thds
    }
}

fn thd_window(mut window: Vec<Complex32>, fft: Arc<dyn FFT<f32>>) -> f32 {
    let mut spectrum = vec![Complex32::new(0.0, 0.0); window.len()];

    fft.process(&mut window, &mut spectrum);

    let fft_resolution = 1.0 * (SAMPLING_RATE as f32) / (spectrum.len() as f32);
    let sixty_hz_bin = (CYCLES_PER_SEC as f32 / fft_resolution) as usize;

    let sixty_hz_power = spectrum[sixty_hz_bin].norm_sqr().sqrt();
    let mut harmonics = 0f32;

    for i in (sixty_hz_bin * 2..spectrum.len() / 2).step_by(sixty_hz_bin) {
        harmonics += spectrum[i].norm_sqr();
    }

    harmonics.sqrt() / sixty_hz_power
}
