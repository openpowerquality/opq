use crate::analysis::*;
use std::f32::consts::PI;

pub fn generate_vrms_waveform(pu: f64, c: usize) -> Vec<f64> {
    generate_vrms_waveform_detailed(pu, c, 120.0, 60, 60)
}

pub fn generate_vrms_waveform_detailed(
    pu: f64,
    c: usize,
    nominal: f64,
    start_c: usize,
    end_c: usize,
) -> Vec<f64> {
    // Start every waveform with nominal
    let mut wf: Vec<f64> = (0..start_c).map(|_| nominal).collect();

    // Add the deviation
    wf.append(&mut (0..c).map(|_| pu_to_rms(pu)).collect());

    // Finish with nominal
    wf.append(&mut (0..end_c).map(|_| nominal).collect());

    wf
}

const TWO_PI: f32 = 2.0 * PI;
const CYCLES_PER_SECOND: f32 = 60.0;
const SAMPLES_PER_SECOND: f32 = 12_000.0;
const SAMPLES_PER_CYCLE: f32 = 200.0;

pub fn sin(amplitude: f32, cycles_per_s: f32, samples_per_s: f32, samples: usize) -> Vec<f32> {
    (0..samples)
        .map(|i| amplitude * (cycles_per_s * TWO_PI * i as f32 / samples_per_s).sin())
        .collect()
}

pub fn opq_sin(samples: usize) -> Vec<f32> {
    sin(23520.0, CYCLES_PER_SECOND, SAMPLES_PER_SECOND, samples)
}

pub fn square_wave(
    amplitutde: f32,
    cycles_per_s: f32,
    samples_per_s: f32,
    samples: usize,
) -> Vec<f32> {
    let samples = sin(amplitutde, cycles_per_s, samples_per_s, samples);
    samples
        .iter()
        .map(|i| if i.signum() > 0.0 { amplitutde } else { 0.0 })
        .collect()
}

pub fn close_to(v: f32, to: f32, err: f32) -> bool {
    (v - to).abs() < err
}

pub fn add_signals(a: &Vec<f32>, b: &Vec<f32>) -> Vec<f32> {
    assert!(a.len() == b.len());

    let mut res = vec![];

    for i in 0..a.len() {
        res.push(a[i] + b[i]);
    }

    res
}

pub fn thd_signal(percent_thd: f32, samples: usize) -> Vec<f32> {
    let samples_60 = sin(1.0, 60.0, 12_000.0, samples);
    let amp_120 = 1.0 * (percent_thd / 100.0);
    let samples_120 = sin(amp_120, 120.0, 12_000.0, samples);

    add_signals(&samples_60, &samples_120)
}

#[cfg(test)]
mod tests {
    use crate::test_utils::generate_vrms_waveform;

    #[test]
    fn test_gen_wf() {
        let wf = generate_vrms_waveform(0.1, 60);
        assert!(&wf[0..59].iter().all(|v| (*v - 120.0f64).abs() < 0.01));
        assert!(&wf[60..119].iter().all(|v| (*v - 12.0).abs() < 0.01));
        assert!(&wf[120..].iter().all(|v| (*v - 120.0).abs() < 0.01));
    }
}
