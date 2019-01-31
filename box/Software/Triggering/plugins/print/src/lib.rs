#[macro_use]
extern crate box_api;

use box_api::types::Window;
use std::collections::HashMap;
#[derive(Debug, Default)]
pub struct PrintPlugin{
}

impl PrintPlugin {
    pub fn new() -> PrintPlugin{
        PrintPlugin{
        }
    }
}

impl box_api::plugin::TriggeringPlugin for PrintPlugin {

    fn name(&self) -> &'static str  {
        "Print Plugin"
    }

    fn process_window(&mut self, msg: &mut Window) -> Option<HashMap < String, f32>> {
        println!("{:?}", msg);
        None
    }

    fn process_command(&mut self, cmd : &String){

    }

    fn init(&mut self) {
        println!("loaded a print pluggin!");
    }
}

declare_plugin!(PrintPlugin, PrintPlugin::new);
