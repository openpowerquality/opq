#[macro_use] extern crate serde_derive;
#[macro_use] extern crate bson;
extern crate failure;
#[macro_use] extern crate failure_derive;

use tokio::{prelude::*, runtime::Runtime, timer::Delay}; // 0.1.15

use futures::{stream, Future, Stream, Sink};
use futures::future::lazy;

use zmq;

use std::env;
use std::fs;
use std::thread;

mod config;
use crate::config::Settings;

mod store_event;

mod error_type;


fn main() {
    let args: Vec<String> = env::args().collect();
    let settings = match Settings::load_from_file(args[1].clone()) {
        Ok(s) => {s},
        Err(e) => {
            println!("Could not load a settings file {}", e);
            return
        },
    };


    let ctx = zmq::Context::new();
    let ev_broker =  ctx.socket(zmq::SUB).unwrap();
    ev_broker.connect(&settings.zmq_event_endpoint).unwrap();
    ev_broker.set_subscribe("".as_bytes()).unwrap();

    match fs::create_dir_all(&settings.path){
        Ok(_) => {println!("Created directory: {}", settings.path)},
        Err(e) => {println!("Could not create directory {} : {}", settings.path, e); return},
    }

    //Start the tread pool:
    let mut runtime = Runtime::new().expect("Unable to create the runtime");

    let handle = runtime.executor();


    loop{
        let ev_str = match ev_broker.recv_string(0){
            Ok(s) => { match s{
                Ok(str) => {str},
                Err(_) => {println!("Not a valid event number "); return;},
            }},
            Err(e) => {println!("Could not get an event number {}", e); return;},
        };

        let ev_id = match ev_str.parse::<u32>(){
            Ok(ev_id) => {ev_id},
            Err(e) => {println!("Could not parse an event number {}", e); return;},
        };

        handle.spawn(lazy(move |_| {
            println!("Oi");
        }));


    }

}
