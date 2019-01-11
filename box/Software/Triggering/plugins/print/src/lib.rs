#[macro_use]
extern crate triggering_v3;

use triggering_v3::types::Window;
use std::collections::HashMap;
#[derive(Debug, Default)]
pub struct PrintPlugin{
}

impl PrintPlugin {
    fn new() -> PrintPlugin{
        PrintPlugin{
        }
    }
}

impl triggering_v3::plugin::TriggeringPlugin for PrintPlugin {

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
