extern crate protobuf;
extern crate zmq;

#[macro_use]
extern crate serde_derive;
extern crate serde_json;
extern crate pnet;
extern crate network_manager;
extern crate uptime_lib;

mod capture;
mod cmd_processor;
mod config;
mod opqbox3;
mod pod_types;

use capture::start_capture;
use cmd_processor::start_cmd_processor;
use std::env;
use std::sync::mpsc::channel;

use std::fs;
use std::io::Read;
use std::path::Path;

fn main() {
    let args: Vec<String> = env::args().collect();
    let config_path = match args.len() {
        0...1 => "triggering.json",
        _ => &args[1],
    };
    let settings = match config::Settings::load_from_file(config_path) {
        Ok(s) => s,
        Err(e) => {
            println!("Could not load a settings file {}: {}", config_path, e);
            return;
        }
    };
    start_cmd_processor(&settings);
    let (sender, receiver) = channel();
    let capture = start_capture(sender, "/dev/random".to_string());
    capture.join().unwrap();
}

