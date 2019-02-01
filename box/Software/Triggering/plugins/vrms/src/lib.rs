#[macro_use]
extern crate box_api;

use box_api::types::Window;
use std::collections::HashMap;
use std::num;

#[derive(Debug, Default)]
pub struct VRMS{
}

impl VRMS {
    pub fn new() -> VRMS{
        VRMS{
        }
    }
    pub fn box_new() -> Box<box_api::plugin::TriggeringPlugin>{
        Box::new(VRMS::new())
    }

}

impl box_api::plugin::TriggeringPlugin for VRMS {

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

