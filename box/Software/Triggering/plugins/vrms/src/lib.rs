#[macro_use]
extern crate triggering_v3;

use triggering_v3::types::Window;
use std::collections::HashMap;
use std::num;

#[derive(Debug, Default)]
pub struct VRMS{
}

impl VRMS {
    fn new() -> VRMS{
        VRMS{
        }
    }
}

impl triggering_v3::plugin::TriggeringPlugin for VRMS {

    fn name(&self) -> &'static str  {
        "VRMS Plugin"
    }

    fn process_window(&mut self, msg: &mut Window) -> Option<HashMap < String, f32>> {
        let mut sum = msg.samples.iter().fold(0.0 as f32, |acc, &x| acc + x*x);
        sum = sum/(msg.samples.len() as f32);

        let mut ret = HashMap::new();
        ret.insert("rms".to_string(), sum.sqrt());
        Some(ret)
    }

    fn process_command(&mut self, cmd : &String){

    }

    fn init(&mut self) {
        println!("loaded a print pluggin!");
    }
}

declare_plugin!(VRMS, VRMS::new);
