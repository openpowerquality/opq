//! Makai is a event detection daemon used for identifying distributed events. Furthermore it will store triggering data to a mongo database.
//!

//extern crate protobuf;
extern crate zmq;

#[macro_use(doc)]
extern crate bson;

extern crate mongodb;
extern crate pub_sub;
extern crate chrono;
extern crate time;
extern crate num;
extern crate protobuf;
extern crate serde_json;
extern crate serde;
extern crate libloading;
#[macro_use]
extern crate serde_derive;

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
    let config_path = match args.len(){
        0...1 => "makai.json",
        _ => &args[1],
    };

    let settings = Settings::load_from_file(config_path).unwrap();

    //DB
    let client = Client::connect(&settings.mongo_host, settings.mongo_port)
            .expect("Failed to initialize standalone client.");

    let ctx = zmq::Context::new();

    let channel : pub_sub::PubSub<Arc<TriggerMessage> > = pub_sub::PubSub::new();
    let zmq_reader = TriggerReceiver::new(channel.clone(), &ctx, &settings);
    let mongo = MongoMeasurements::new(&client, channel.subscribe(), &settings);


    let mut handles = vec![];
    handles.push(thread::spawn(move || {
        zmq_reader.run_loop();
    }));

    handles.push(thread::spawn(move || {
        mongo.run_loop();
    }));
    let mut plugin_manager = PluginManager::new();
    unsafe {
        //start all of the plugins
        let _: Vec<_> = settings.plugins.iter().map(|ref x| plugin_manager.load_plugin(x, channel.subscribe())).collect();
    }

    while let Some(handle) = handles.pop() {
        handle.join().unwrap();
    }
}
