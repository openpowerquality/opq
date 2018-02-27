#[macro_use]
extern crate opqapi;

use std::str;
use opqapi::MakaiPlugin;
use opqapi::protocol::opq::{RequestEventMessage, TriggerMessage};
use std::sync::Arc;


#[derive(Debug, Default)]
pub struct NullPlugin;

impl MakaiPlugin for NullPlugin {
    fn name(&self) -> &'static str  {
        "Null Plugin"
    }

    fn on_plugin_load(&self) {
        println!("Null plugin loaded.");
    }

    fn on_plugin_unload(&self) {
        println!("Null plugin unloaded.")
    }
    fn process_measurement(&self, _: Arc<TriggerMessage>) -> Option<RequestEventMessage> {
        println!("Processed measurement");
        None
    }
}

declare_plugin!(NullPlugin, NullPlugin::default);