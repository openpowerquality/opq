//! Makai is a event detection daemon used for identifying distributed events. Furthermore it will store triggering data to a mongo database.
extern crate zmq;
extern crate chrono;
extern crate libloading;
extern crate num;
extern crate protobuf;
extern crate pub_sub;
extern crate serde;

extern crate serde_derive;
extern crate serde_json;
extern crate time;
extern crate mongodb;

use std::thread;
use std::sync::Arc;
use std::env;

use triggering_service::config::Settings;
use triggering_service::trigger_receiver::TriggerReceiver;
use triggering_service::plugin_manager::PluginManager;
use triggering_service::proto::opqbox3::Measurement;
use triggering_service::mongo_storage_service::MongoStorageService;

//mod config;


fn main() {
    let args: Vec<String> = env::args().collect();
    let config_path = match args.len() {
        0...1 => "makai.json",
        _ => &args[1],
    };

    let settings = match Settings::load_from_file(config_path) {
        Ok(s) => {s},
        Err(e) => {println!("Could not load a settings file {}: {}", config_path, e); return},
    };


    let ctx = zmq::Context::new();

    let channel: pub_sub::PubSub<Arc<Measurement>> = pub_sub::PubSub::new();
    let zmq_reader = TriggerReceiver::new(channel.clone(), &ctx, &settings);
    let mut mongo_storage = MongoStorageService::new(&ctx, &settings);
    //let mongo = MongoMeasurements::new(&client, channel.subscribe(), &settings);

    let mut handles = vec![];
    handles.push(thread::spawn(move || {
        zmq_reader.run_loop();
    }));

    handles.push(thread::spawn(move || {
        mongo_storage.run_loop();
    }));

    //handles.push(thread::spawn(move || {
    //    mongo.run_loop();
    //}));
    let mut plugin_manager = PluginManager::new(&ctx, &settings);
    for document in settings.plugins {
        let filename = match document.get("path"){
            None => {println!("One of the plugins is missing a path field. How do I load it?"); continue},
            Some(s) => {s.as_str().unwrap().to_string()},
        };
        unsafe {
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
