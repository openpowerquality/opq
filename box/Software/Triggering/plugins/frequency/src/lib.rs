#[macro_use]
extern crate box_api;
extern crate num;

use std::collections::HashMap;
use box_api::types::Window;

mod fir;
use fir::FIR;

mod filter_coef;
use filter_coef::{DOWNSAMPLING_FILTER_TAPS, LOW_PASS_FILTER_TAPS};

const SAMPLES_PER_CYCLE : usize = 200;
const CYCLES_PER_SEC : usize = 60;
const DECIMATION_FACTOR : usize = 10;

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
    state: PluginState,
    downsampling: FIR<f32>,
    lowpass: FIR<f32>,
    samples_per_measurement: u8,
}

impl Frequency {
    fn new() -> Frequency {
        Frequency {
            state: (PluginState::Initializing(0)),
            downsampling: FIR::new(&DOWNSAMPLING_FILTER_TAPS.to_vec(), DECIMATION_FACTOR , 1),
            lowpass: FIR::new(&LOW_PASS_FILTER_TAPS.to_vec(), 1, 1),
            samples_per_measurement: 6,
        }
    }
}

impl box_api::plugin::TriggeringPlugin for Frequency {
    fn name(&self) -> &'static str {
        "Frequency Plugin"
    }

    fn process_window(&mut self, msg: &mut Window) -> Option<HashMap<String, f32>> {
        let mut ret = None;
        self.state = match self.state {
            PluginState::Initializing(window_count) => {
                let new_count = window_count + 1;
                let lp = self.downsampling.process(&msg.samples.to_vec());
                self.lowpass.process(&lp);
                if new_count == 0xFF {
                    PluginState::Accumulating(self.samples_per_measurement, Vec::new())
                } else {
                    PluginState::Initializing(new_count)
                }
            }
            PluginState::Accumulating(window_count, ref mut data) => {
                let mut filtered = self
                    .lowpass
                    .process(&self.downsampling.process(&msg.samples.to_vec()));
                if window_count == 0 {
                    let f = calculate_frequency(data);
                    ret = Some(map!{"f".to_string() =>f});
                    PluginState::Accumulating(self.samples_per_measurement, filtered)
                } else {
                    data.append(&mut filtered);
                    PluginState::Accumulating(window_count - 1, data.to_vec())
                }
            }
        };
        ret
    }

    fn process_command(&mut self, cmd: &String) {}

    fn init(&mut self) {
        println!("loaded a frequency plugin!");
    }
}

fn calculate_frequency(data : & Vec<f32>) -> f32{
    let mut zero_crossings : Vec<f32> = Vec::new();
    for i in 1..data.len(){
        let last = data[i-1];
        let next = data[i];
        if (last <= 0.0 && next > 0.0) || (last >=0.0 && next < 0.0){
            zero_crossings.push(((i)  as f32) - (next) / (next - last))
        }
    }
    let mut accumulator: f32 = 0.0;
    for i in 1..zero_crossings.len() {
        accumulator += zero_crossings[i] - zero_crossings[i - 1];
    }
    accumulator /= (zero_crossings.len() - 1 ) as f32;
    (SAMPLES_PER_CYCLE as f32) *
          (CYCLES_PER_SEC as f32)/
          (DECIMATION_FACTOR as f32) /
        accumulator/ (2.0)
}

declare_plugin!(Frequency, Frequency::new);


#[cfg(test)]
mod tests {
    use super::*;
    use triggering_v3::types::RawWindow;
    use triggering_v3::types::Window;
    use triggering_v3::plugin::TriggeringPlugin;
    use std::f64;
    #[test]
    fn test_freq() {
        let mut f = Frequency::new();
        for i in 0..1000 {
            let mut rw = RawWindow {
                datapoints: [0; 200],
                last_gps_counter: 0,
                current_counter: 0,
                flags: 0,
            };
            for j in 0..200 {
                rw.datapoints[j] = (30000.0 * (2.0 * 3.1415 * (j as f64) / 200.0).sin()) as i16;
            }
            let mut w = Window::new(rw, 100.0);
            let mut wp = &mut w;
            let ret =  f.process_window(wp);
            match ret{
                None => {},
                Some(map) => {assert!((map["f"] - 60.0 ).abs() < 0.00001)},
            }
        }

    }
}

