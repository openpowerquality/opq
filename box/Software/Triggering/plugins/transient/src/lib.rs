extern crate box_api;
extern crate num;

use box_api::types::Window;
use std::collections::HashMap;

mod fir;
use fir::FIR;

mod filter_coef;
use filter_coef::FILTER_TAPS;

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

pub struct Transient {
    state: Option<PluginState>,
    filter: FIR,
    samples_per_measurement: u8,
}

impl Transient {
    pub fn new() -> Transient {
        Transient {
            state: Some(PluginState::Initializing(0)),
            filter: FIR::new(FILTER_TAPS.to_vec(), 1),
            samples_per_measurement: 6,
        }
    }

    pub fn box_new() -> Box<box_api::plugin::TriggeringPlugin> {
        Box::new(Transient::new())
    }

    fn find_max(data : &Vec<f32>)-> f32{
        let mut max = data[0];
        for i in 1..data.len(){
            if max < data[i].abs() {
                max = data[i];
            }
        }
        max
    }
}

impl box_api::plugin::TriggeringPlugin for Transient {
    fn name(&self) -> &'static str {
        "Frequency Plugin"
    }

    fn process_window(&mut self, msg: &mut Window) -> Option<HashMap<String, f32>> {
        let mut ret = None;
        self.state = match self.state.take().unwrap() {
            PluginState::Initializing(window_count) => {
                let new_count = window_count + 1;
                self.filter.process(&msg.samples.to_vec());
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
                let mut filtered = self.filter.process(&msg.samples.to_vec());
                if window_count == 0 {
                    let max = Transient::find_max(&data);
                    ret = Some(map! {"trans".to_string() =>max});
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
