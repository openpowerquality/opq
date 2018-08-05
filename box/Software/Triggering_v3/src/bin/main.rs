extern crate protobuf;
extern crate zmq;
#[macro_use] extern crate log;
extern crate network_manager;
extern crate pnet;
extern crate serde_json;
extern crate uptime_lib;
extern crate triggering_v3;
extern crate syslog;

use std::env;
use std::sync::mpsc::channel;
use std::sync::Arc;
use triggering_v3::capture::start_capture;
use triggering_v3::cmd_processor::start_cmd_processor;
use triggering_v3::config::Config;
use triggering_v3::plugin_manager::run_plugins;

fn main() {

    syslog::init(syslog::Facility::LOG_USER,
                 log::LevelFilter::Info,
                 Some("Triggering V3")).expect("cannot initialize syslog");
    let args: Vec<String> = env::args().collect();
    let config_path = match args.len() {
        0...1 => "triggering.json",
        _ => &args[1],
    };
    let config = match Config::new(config_path){
        Ok(c) => {c},
        Err(e) => {error!("{}", e); return;},
    };
    info!("Box ID is {}, public key: {}", config.settings.box_id, config.settings.box_public_key);
    start_cmd_processor(Arc::clone(&config));
    let (sender, receiver) = channel();
    let processing = run_plugins(receiver, Arc::clone(&config));
    let capture = start_capture(sender, Arc::clone(&config));
    capture.join().unwrap();
    processing.join().unwrap();
}
