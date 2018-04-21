//! Makai is a event detection daemon used for identifying distributed events. Furthermore it will store triggering data to a mongo database.
//!

//extern crate protobuf;
extern crate zmq;

#[macro_use(doc)]
extern crate bson;

extern crate chrono;
extern crate libloading;
extern crate mongodb;
extern crate num;
extern crate protobuf;
extern crate pub_sub;
extern crate serde;
#[macro_use]
extern crate serde_derive;
extern crate serde_json;
extern crate time;

extern crate opqapi;
use opqapi::protocol::TriggerMessage;

use mongodb::{Client, ThreadedClient};
use std::thread;
use std::sync::Arc;
use std::env;
mod constants;

mod trigger_receiver;
use trigger_receiver::TriggerReceiver;
mod mongo;
use mongo::MongoMeasurements;
mod config;
use config::Settings;

mod event_requester;
mod overlapping_interval;
mod plugin_manager;
use plugin_manager::PluginManager;

fn main() {
    let args: Vec<String> = env::args().collect();
    let config_path = match args.len() {
        0...1 => "makai.json",
        _ => &args[1],
    };

    let settings = Settings::load_from_file(config_path).unwrap();

    //DB
    let client = Client::connect(&settings.mongo_host, settings.mongo_port)
        .expect("Failed to initialize standalone client.");

    let ctx = zmq::Context::new();

    let channel: pub_sub::PubSub<Arc<TriggerMessage>> = pub_sub::PubSub::new();
    let zmq_reader = TriggerReceiver::new(channel.clone(), &ctx, &settings);
    let mongo = MongoMeasurements::new(&client, channel.subscribe(), &settings);

    let mut handles = vec![];
    handles.push(thread::spawn(move || {
        zmq_reader.run_loop();
    }));

    handles.push(thread::spawn(move || {
        mongo.run_loop();
    }));
    let mut plugin_manager = PluginManager::new(&ctx, &settings);
    unsafe {
        for document in settings.plugins {
            let filename = document.get("path").unwrap().as_str().unwrap().to_string();
            let res = plugin_manager.load_plugin(document, channel.subscribe());
            match res {
                Ok(_) => println!("Loaded {}", filename),
                Err(err_str) => println!("Failed to load {}, {}", filename, err_str),
            }
        }
    }

    while let Some(handle) = handles.pop() {
        handle.join().unwrap();
    }
}
