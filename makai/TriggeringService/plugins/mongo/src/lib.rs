#[macro_use]
extern crate triggering_service;
use std::str;
use triggering_service::makai_plugin::MakaiPlugin;
use triggering_service::proto::opqbox3::Measurement;
use triggering_service::proto::opqbox3::Command;
use std::sync::Arc;

#[macro_use] extern crate serde_derive;
extern crate serde;
extern crate serde_json;

#[derive(Debug, Default)]
pub struct MongoPlugin{
}

impl MongoPlugin {
    fn new() -> MongoPlugin{
        MongoPlugin{
        }
    }
}

impl MakaiPlugin for MongoPlugin {

    fn name(&self) -> &'static str  {
        "Mongo Plugin"
    }

    fn process_measurement(&mut self, msg: Arc<Measurement>) -> Option<Vec<Command>> {
        None
    }

    fn on_plugin_load(&mut self, args : String) {
    }

    fn on_plugin_unload(&mut self) {
        println!("Mongo plugin unloaded.")
    }
}

declare_plugin!(MongoPlugin, MongoPlugin::new);
