#[macro_use]
extern crate triggering_v3;
extern crate rustfft;
use rustfft::num_complex::Complex32;
use rustfft::FFTplanner;
use rustfft::FFT;
use std::collections::HashMap;
use std::sync::Arc;
use triggering_v3::types::Window;

const SAMPLES_PER_CYCLE: usize = 200;
const CYCLES_PER_SEC: usize = 60;
const DEFAULT_WINDOW_COUNT: usize = 6;
const SAMPLING_RATE: usize = CYCLES_PER_SEC * SAMPLES_PER_CYCLE;

macro_rules! map(
    { $($key:expr => $value:expr),+ } => {
        {
            let mut m = ::std::collections::HashMap::new();
            $(
                m.insert($key, $value);
            )+
            m
        }
     };
);

pub struct THD {
    window_count: usize,
    current_count: usize,
    fft_planer: FFTplanner<f32>,
    fft: Arc<FFT<f32>>,
    samples: Vec<Complex32>,
}

impl THD {
    fn new() -> THD {
        let mut planner = FFTplanner::new(false);
        let mut fft = planner.plan_fft(DEFAULT_WINDOW_COUNT * SAMPLES_PER_CYCLE);
        THD {
            window_count: DEFAULT_WINDOW_COUNT,
            current_count: 0,
            fft_planer: planner,
            fft: fft,
            samples: vec![],
        }
    }
}

impl triggering_v3::plugin::TriggeringPlugin for THD {
    fn name(&self) -> &'static str {
        "THD Plugin"
    }

    fn process_window(&mut self, msg: &mut Window) -> Option<HashMap<String, f32>> {
        let mut ret = None;

        for sample in msg.samples.iter() {
            self.samples.push(Complex32::new(*sample, 0.0));
        }
        self.current_count += 1;

        if self.current_count >= self.window_count {
            let mut spectrum = vec![Complex32::new(0.0, 0.0); self.samples.len()];
            self.fft.process(&mut self.samples, &mut spectrum);

            let fft_resolution = 1.0 * (SAMPLING_RATE as f32) / (spectrum.len() as f32);
            let sixty_hz_bin = (CYCLES_PER_SEC as f32 / fft_resolution) as usize;

            let sixty_hz_power = spectrum[sixty_hz_bin].norm_sqr().sqrt();
            //spectrum[sixty_hz_bin] = Complex32::new(0.0,0.0);
            let mut harmonics: f32 = 0.0;

            for i in (sixty_hz_bin * 2..spectrum.len() / 2).step_by(sixty_hz_bin) {
                harmonics += spectrum[i].norm_sqr();
            }
            harmonics = harmonics.sqrt();
            ret = Some(map! {"thd".to_string() => harmonics/sixty_hz_power});
            self.current_count = 0;
            self.samples.clear();
        }
        ret
    }

    fn process_command(&mut self, cmd: &String) {}

    fn init(&mut self) {
        println!("loaded a THD plugin!");
    }
}

declare_plugin!(THD, THD::new);

#[cfg(test)]
mod tests {
    use super::*;
    use std::f64;
    use triggering_v3::plugin::TriggeringPlugin;
    use triggering_v3::types::RawWindow;
    use triggering_v3::types::Window;
    #[test]
    fn test_thd_tenth() {
        let mut thd = THD::new();
        for i in 0..DEFAULT_WINDOW_COUNT {
            let mut rw = RawWindow {
                datapoints: [0; 200],
                last_gps_counter: 0,
                current_counter: 0,
                flags: 0,
            };
            for j in 0..200 {
                rw.datapoints[j] = (15000.0 * (2.0 * 3.1415 * (j as f64) / 200.0).sin()
                    + (1500.0 * (4.0 * 3.1415 * (j as f64) / 200.0).sin()))
                    as i16;
            }
            let mut w = Window::new(rw, 100.0);
            let mut wp = &mut w;
            let ret = thd.process_window(wp);
            if let Some(map) = ret {
                assert!((map["thd"] - 0.1).abs() < 0.01);
            }
        }
    }

    #[test]
    fn test_thd_half() {
        let mut thd = THD::new();
        for i in 0..DEFAULT_WINDOW_COUNT {
            let mut rw = RawWindow {
                datapoints: [0; 200],
                last_gps_counter: 0,
                current_counter: 0,
                flags: 0,
            };
            for j in 0..200 {
                rw.datapoints[j] = (10000.0 * (2.0 * 3.1415 * (j as f64) / 200.0).sin()
                    + (5000.0 * (4.0 * 3.1415 * (j as f64) / 200.0).sin()))
                    as i16;
            }
            let mut w = Window::new(rw, 100.0);
            let mut wp = &mut w;
            let ret = thd.process_window(wp);
            if let Some(map) = ret {
                assert!((map["thd"] - 0.5).abs() < 0.01);
            }
        }
    }

}
