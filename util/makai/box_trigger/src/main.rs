#[macro_use] extern crate serde_derive;

mod proto;
mod box_command;
mod config;
mod util;
mod box_response;
mod box_list;

use std::env;
use std::thread;


use crate::box_command::{BoxCommand, CommandType};
use crate::box_response::BoxResponse;
use crate::config::Settings;

fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() < 3{
        println!("Usage: [config] [boxid]")
    }
    let settings = match Settings::load_from_file(args[1].clone()) {
        Ok(s) => {s},
        Err(e) => {
            println!("Could not load a settings file from the environment {}: {}", "MAKAI_SETTINGS", e);
            return
        },
    };
    let box_id = args[2].parse::<u32>().unwrap();

    let mut threads = vec![];

    let ctx = zmq::Context::new();
    let mut rsp_manager = BoxResponse::new(&settings, &ctx);
    threads.push(thread::spawn(move || {
        rsp_manager.run_loop();
    }));

    let mut cmd_manager = BoxCommand::new(&settings, &ctx);
    cmd_manager.send_command(box_id, CommandType::Trigger);
    for t in threads{
        t.join().unwrap();
    }
}
