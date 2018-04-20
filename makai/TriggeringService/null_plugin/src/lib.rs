#[macro_use]
extern crate opqapi;

use std::str;
use opqapi::MakaiPlugin;
use opqapi::protocol::opq::{RequestEventMessage, TriggerMessage};
use std::sync::Arc;


#[derive(Debug, Default)]
pub struct NullPlugin{
    print : bool
}

impl NullPlugin {
    fn new() -> NullPlugin{
        NullPlugin{
            print : false,
        }
    }
}

impl MakaiPlugin for NullPlugin {

    fn name(&self) -> &'static str  {
        "Null Plugin"
    }

    fn on_plugin_load(&mut self, args : Vec<String>) {
        println!("Null plugin loaded with arguments {:?}", args);
        for arg in args{
            if arg == "print"{
                self.print = true;
            }
        }
    }

    fn on_plugin_unload(&mut self) {
        println!("Null plugin unloaded.")
    }

    fn process_measurement(&mut self, msg: Arc<TriggerMessage>) -> Option<RequestEventMessage> {
        if self.print{
            println!("{:?}", msg);
        }
        None
    }
}

declare_plugin!(NullPlugin, NullPlugin::new);