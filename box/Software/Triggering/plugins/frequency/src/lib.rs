extern crate box_api;
extern crate num;

use box_api::types::Window;
use std::collections::HashMap;

mod fir;
use fir::FIR;

mod filter_coef;
use filter_coef::{DOWNSAMPLING_FILTER_TAPS, LOW_PASS_FILTER_TAPS};

const SAMPLES_PER_CYCLE: usize = 200;
const CYCLES_PER_SEC: usize = 60;
const DECIMATION_FACTOR: usize = 10;

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

enum PluginState {
    Initializing(u8),
    Accumulating(u8, Vec<f32>),
}

pub struct Frequency {
    state: Option<PluginState>,
    downsampling: FIR,
    lowpass: FIR,
    samples_per_measurement: u8,
}

impl Frequency {
    pub fn new() -> Frequency {
        Frequency {
            state: Some(PluginState::Initializing(0)),
            downsampling: FIR::new(DOWNSAMPLING_FILTER_TAPS.to_vec(), DECIMATION_FACTOR),
            lowpass: FIR::new(LOW_PASS_FILTER_TAPS.to_vec(), 1),
            samples_per_measurement: 6,
        }
    }

    pub fn box_new() -> Box<box_api::plugin::TriggeringPlugin> {
        Box::new(Frequency::new())
    }
}

impl box_api::plugin::TriggeringPlugin for Frequency {
    fn name(&self) -> &'static str {
        "Frequency Plugin"
    }

    fn process_window(&mut self, msg: &mut Window) -> Option<HashMap<String, f32>> {
        let mut ret = None;
        self.state = match self.state.take().unwrap() {
            PluginState::Initializing(window_count) => {
                let new_count = window_count + 1;
                let lp = self.downsampling.process(&msg.samples.to_vec());
                self.lowpass.process(&lp);
                if new_count == 0xFF {
                    Some(PluginState::Accumulating(
                        self.samples_per_measurement,
                        Vec::new(),
                    ))
                } else {
                    Some(PluginState::Initializing(new_count))
                }
            }
            PluginState::Accumulating(window_count, mut data) => {
                let mut filtered = self
                    .lowpass
                    .process(&self.downsampling.process(&msg.samples.to_vec()));
                if window_count == 0 {
                    let f = calculate_frequency(&data);
                    ret = Some(map! {"f".to_string() =>f});
                    Some(PluginState::Accumulating(
                        self.samples_per_measurement,
                        filtered,
                    ))
                } else {
                    data.append(&mut filtered);
                    Some(PluginState::Accumulating(window_count - 1, data))
                }
            }
        };
        ret
    }

    fn process_command(&mut self, _cmd: &String) {}

    fn init(&mut self) {
        println!("loaded a frequency plugin!");
    }
}

fn calculate_frequency(data: &Vec<f32>) -> f32 {
    let mut zero_crossings: Vec<f32> = Vec::new();
    for i in 1..data.len() {
        let last = data[i - 1];
        let next = data[i];
        if (last <= 0.0 && next >= 0.0) || (last >= 0.0 && next <= 0.0) {
            zero_crossings.push(((i) as f32) - next / (next - last));
        }
    }
    let mut accumulator: f32 = 0.0;
    for i in 1..zero_crossings.len() {
        accumulator += zero_crossings[i] - zero_crossings[i - 1];
    }
    accumulator /= (zero_crossings.len() - 1) as f32;
    (SAMPLES_PER_CYCLE as f32) * (CYCLES_PER_SEC as f32)
        / (DECIMATION_FACTOR as f32)
        / accumulator
        / (2.0)
}

#[cfg(test)]
mod tests {
    use super::*;
    use box_api::plugin::TriggeringPlugin;
    use box_api::types::RawWindow;
    use box_api::types::Window;
    use std::f64;
    use std::f64::consts::PI;
    #[test]
    fn test_freq() {
        let mut target_frequency = 60.1;
        let mut f = Frequency::new();
        let mut time: f64 = 0.0;
        for _ in 0..300 {
            let mut rw = RawWindow {
                datapoints: [0; 200],
                last_gps_counter: 0,
                current_counter: 0,
                flags: 0,
            };
            for j in 0..200 {
                time += 1.0;
                rw.datapoints[j] = (30000.0
                    * (2.0 * PI * time
                        / (((CYCLES_PER_SEC * SAMPLES_PER_CYCLE) as f64) / target_frequency))
                        .sin()) as i16;
            }
            let mut w = Window::new(rw, 100.0);
            //let  wp = &mut w;
            let ret = f.process_window(&mut w);

            match ret {
                None => {}
                Some(map) => {
                    println!("{}", map["f"]);
                    assert!((map["f"] - target_frequency as f32).abs() < 0.01)
                }
            }
        }
        target_frequency = 59.9;
        for _ in 0..2*6 {
            let mut rw = RawWindow {
                datapoints: [0; 200],
                last_gps_counter: 0,
                current_counter: 0,
                flags: 0,
            };
            for j in 0..200 {
                time += 1.0;
                rw.datapoints[j] = (30000.0
                    * (2.0 * PI * time
                        / (((CYCLES_PER_SEC * SAMPLES_PER_CYCLE) as f64) / target_frequency))
                        .sin()) as i16;
            }
            let mut w = Window::new(rw, 100.0);

            let ret = f.process_window(&mut w);
            match ret {
                None => {}
                Some(map) => {
                    println!("{}", map["f"]);
                }
            }
        }

        for _ in 0..10*6 {
            let mut rw = RawWindow {
                datapoints: [0; 200],
                last_gps_counter: 0,
                current_counter: 0,
                flags: 0,
            };
            for j in 0..200 {
                time += 1.0;
                rw.datapoints[j] = (30000.0
                    * (2.0 * PI * time
                    / (((CYCLES_PER_SEC * SAMPLES_PER_CYCLE) as f64) / target_frequency))
                    .sin()) as i16;
            }
            let mut w = Window::new(rw, 100.0);
            //let  wp = &mut w;
            let ret = f.process_window(&mut w);

            match ret {
                None => {}
                Some(map) => {
                    println!("{}", map["f"]);
                    assert!((map["f"] - target_frequency as f32).abs() < 0.01)
                }
            }
        }

    }
}
