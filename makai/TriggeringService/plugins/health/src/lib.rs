#[macro_use]
extern crate triggering_service;
use std::str;
use triggering_service::makai_plugin::MakaiPlugin;
use triggering_service::proto::opqbox3::Measurement;
use triggering_service::proto::opqbox3::Command;
use triggering_service::proto::opqbox3::GetDataCommand;
use triggering_service::proto::opqbox3::Command_oneof_command;
use std::sync::Arc;
use std::thread;
use std::sync::Mutex;

#[macro_use] extern crate serde_derive;
extern crate serde;
extern crate serde_json;
#[macro_use] extern crate rouille;

mod types;
mod http_endpoint;

use types::{HealthPluginSettings, Statistics, OpqBox};

#[derive(Default)]
pub struct HealthPlugin{
    settings : HealthPluginSettings,
    stats : Arc<Mutex<Statistics>>,
    http_thread : Option<thread::JoinHandle<()>>,
}

impl MakaiPlugin for HealthPlugin {

    fn name(&self) -> &'static str  {
        "Health Plugin"
    }

    fn process_measurement(&mut self, msg: Arc<Measurement>) -> Option<Vec<Command>> {
        let mut stats = self.stats.lock().unwrap();
        let opq_box = OpqBox {
            id: msg.box_id,
            last_timestamp: msg.timestamp_ms,
            ok: true,
        };
        stats.box_status.insert(msg.box_id, opq_box );
        if stats.trigger_now {
            stats.trigger_now = false;
            let mut trg = Command::new();
            trg.box_id  = msg.box_id as i32;
            trg.timestamp_ms = 0;
            let mut get_data = GetDataCommand::new();
            get_data.start_ms = msg.timestamp_ms - 1000;
            get_data.end_ms = msg.timestamp_ms - 500;
            get_data.wait = false;
            trg.command = Some(Command_oneof_command::data_command(get_data));
            println!("Forced Trigger");
            return Some(vec![trg]);
        }
        None
    }

    fn on_plugin_load(&mut self, args : String) {
        let set = serde_json::from_str(&args);
        self.settings = match set{
            Ok(s) => {s},
            Err(e) => {println!("Bad setting file for plugin {}: {:?}", self.name(), e); HealthPluginSettings::default()},
        };

        let stats = self.stats.clone();
        let settings = self.settings.clone();

        self.http_thread = Some(thread::spawn(move || {
            http_endpoint::start_server(stats, settings);
        }));

    }

    fn on_plugin_unload(&mut self) {
        println!("Health plugin unloaded.")
    }
}

declare_plugin!(HealthPlugin, HealthPlugin::default);
