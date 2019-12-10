#[macro_use] extern crate serde_derive;

mod proto;
mod box_command;
mod config;
mod util;
mod box_response;
mod box_list;

use std::env;
use std::thread;
use std::sync::{Arc, Mutex};
use std::collections::HashMap;
use std::time::{SystemTime};

use crate::box_command::{BoxCommand, CommandType};
use crate::box_response::BoxResponse;
use crate::config::Settings;


fn main() {
    let args: Vec<String> = env::args().collect();
    let settings = match Settings::load_from_file(args[1].clone()) {
        Ok(s) => {s},
        Err(e) => {
            println!("Could not load a settings file from the environment {}: {}", "MAKAI_SETTINGS", e);
            return
        },
    };

    let box_list = box_list::get_box_list(&settings);

    let mut threads = vec![];

    let ctx = zmq::Context::new();
    let ts_counter : Arc<Mutex<HashMap<u32, SystemTime>>> = Arc::new(Mutex::new(HashMap::new()));
    let mut rsp_manager = BoxResponse::new(&settings, &ct   x, ts_counter.clone());
    threads.push(thread::spawn(move || {
        rsp_manager.run_loop();
    }));

    let mut cmd_manager = BoxCommand::new(&settings, &ctx, ts_counter.clone());
    for id in box_list {
        cmd_manager.send_command(id, CommandType::Info);
    }

    let tout = std::time::Duration::from_millis(5000);
    thread::sleep(tout);

}
