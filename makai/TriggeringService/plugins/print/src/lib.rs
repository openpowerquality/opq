#[macro_use]
extern crate opqapi;

use std::str;
use opqapi::MakaiPlugin;
use opqapi::protocol::opq::{RequestEventMessage, TriggerMessage};
use std::sync::Arc;


#[derive(Debug, Default)]
pub struct PrintPlugin{
    print : bool
}

impl PrintPlugin {
    fn new() -> PrintPlugin{
        PrintPlugin{
            print : true,
        }
    }
}

impl MakaiPlugin for PrintPlugin {

    fn name(&self) -> &'static str  {
        "Print Plugin"
    }

    fn on_plugin_load(&mut self, args : String) {
        println!("Print plugin loaded with arguments {:?}", args);
    }

    fn on_plugin_unload(&mut self) {
        println!("Print plugin unloaded.")
    }

    fn process_measurement(&mut self, msg: Arc<TriggerMessage>) -> Option<RequestEventMessage> {
        if self.print{
            println!("{:?}", msg);
        }
        None
    }
}

declare_plugin!(PrintPlugin, PrintPlugin::new);
