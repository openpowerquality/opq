//! Makai is a event detection daemon used for identifying distributed events. Furthermore it will store triggering data to a mongo database.
//!

extern crate protobuf;
extern crate zmq;

#[macro_use(doc)]
extern crate bson;
extern crate mongodb;
extern crate pub_sub;
extern crate chrono;
extern crate time;

extern crate num;


use mongodb::{Client, ThreadedClient};
use std::thread;

mod constants;
mod opq;
use opq::TriggerMessage;

mod zmqreader;
use zmqreader::ZmqReader;

mod mongo;
use mongo::MongoMeasurements;

fn main() {
    //DB
    let client = Client::connect("localhost", 27017)
            .expect("Failed to initialize standalone client.");

    let ctx = zmq::Context::new();

    let channel : pub_sub::PubSub<TriggerMessage> = pub_sub::PubSub::new();
    let zmq_reader = ZmqReader::new(channel.clone(), &ctx);
    let mongo = MongoMeasurements::new(&client, channel.subscribe());


    let mut handles = vec![];
    handles.push(thread::spawn(move || {
        zmq_reader.run_loop();
    }));

    handles.push(thread::spawn(move || {
        mongo.run_loop();
    }));


    while let Some(handle) = handles.pop() {
        handle.join().unwrap();
    }
}
