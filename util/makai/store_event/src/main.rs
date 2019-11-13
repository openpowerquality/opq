#[macro_use]
extern crate serde_derive;
#[macro_use]
extern crate bson;
extern crate failure;
#[macro_use]
extern crate failure_derive;

use mongodb::Client;
use mongodb::ThreadedClient;

use zmq;

use std::fs;
use std::{env, thread};

mod config;
use crate::config::Settings;
use std::time::Duration;

mod error_type;
mod store_event;

fn main() {
    let args: Vec<String> = env::args().collect();
    let settings = match Settings::load_from_file(args[1].clone()) {
        Ok(s) => s,
        Err(e) => {
            println!("Could not load a settings file {}", e);
            return;
        }
    };

    let ctx = zmq::Context::new();
    let ev_broker = ctx.socket(zmq::SUB).unwrap();
    ev_broker.connect(&settings.zmq_event_endpoint).unwrap();
    ev_broker.set_subscribe("".as_bytes()).unwrap();

    match fs::create_dir_all(&settings.path) {
        Ok(_) => println!("Created directory: {}", settings.path),
        Err(e) => {
            println!("Could not create directory {} : {}", settings.path, e);
            return;
        }
    }

    //Mongo bullshit
    let client = Client::connect(&settings.mongo_host, settings.mongo_port).unwrap();

    loop {
        let msg = match ev_broker.recv_multipart(0) {
            Ok(s) => s,
            Err(e) => {
                println!("Could not get an event number {}", e);
                return;
            }
        };
        if msg.len() < 2 {
            println!("Message needs more parts");
            return;
        }

        let ev_str = match String::from_utf8(msg[1].clone()) {
            Ok(s) => s,
            Err(e) => {
                println!("Could not parse an event number {}", e);
                return;
            }
        };

        let ev_id = match ev_str.parse::<u32>() {
            Ok(ev_id) => ev_id,
            Err(e) => {
                println!("Could not parse an event number {}", e);
                return;
            }
        };
        let path = settings.path.clone();
        let client_copy = client.clone();
        let delay = Duration::from_millis(settings.grace_ms);

        thread::spawn(move || {
            thread::sleep(delay);
            match store_event::store_event(ev_id, path, client_copy) {
                Ok(_) => (),
                Err(e) => println!("Uh OH: {}", e),
            };
        });
    }
}
