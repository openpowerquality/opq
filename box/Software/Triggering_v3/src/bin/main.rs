extern crate protobuf;
extern crate zmq;
#[macro_use]
extern crate log;
extern crate crossbeam_channel;
extern crate network_manager;
extern crate pnet;
extern crate serde_json;
extern crate syslog;
extern crate triggering_v3;
extern crate uptime_lib;

use crossbeam_channel as channel;
use std::env;
use std::sync::Arc;
use triggering_v3::capture::start_capture;
use triggering_v3::cmd_processor::start_cmd_processor;
use triggering_v3::config::Config;
use triggering_v3::measurement_filter::run_filter;
use triggering_v3::plugin_manager::run_plugins;
fn main() {
    syslog::init(
        syslog::Facility::LOG_USER,
        log::LevelFilter::Info,
        Some("Triggering V3"),
    ).expect("cannot initialize syslog");

    let args: Vec<String> = env::args().collect();
    let config_path = match args.len() {
        0...1 => "triggering.json",
        _ => &args[1],
    };
    let config = match Config::new(config_path) {
        Ok(c) => c,
        Err(e) => {
            error!("{}", e);
            return;
        }
    };
    info!(
        "Box ID is {}, public key: {}",
        config.settings.box_id, config.settings.box_public_key
    );

    let (sender_capture_to_processing, receiver_capture_to_processing) = channel::bounded(100);
    let (sender_processing_to_filtering, receiver_processing_to_filtering) = channel::bounded(100);
    let (sender_cmd_to_processing, receiver_cmd_to_processing) = channel::bounded(100);

    let cmd_processor = start_cmd_processor(sender_cmd_to_processing, Arc::clone(&config));

    let capture = start_capture(sender_capture_to_processing, Arc::clone(&config));

    let processing = run_plugins(
        receiver_capture_to_processing,
        sender_processing_to_filtering,
        receiver_cmd_to_processing,
        Arc::clone(&config),
    );

    let filter = run_filter(receiver_processing_to_filtering, Arc::clone(&config));

    cmd_processor.join().unwrap();
    capture.join().unwrap();
    processing.join().unwrap();
    filter.join().unwrap()
}
