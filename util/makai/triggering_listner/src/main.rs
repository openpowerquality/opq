#[macro_use] extern crate serde_derive;

mod proto;

mod config;

use std::env;
use zmq;
use protobuf::{parse_from_bytes,ProtobufError};
use crate::proto::opqbox3::{Measurement};

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

    let ctx = zmq::Context::new();
    let trg_broker =  ctx.socket(zmq::SUB).unwrap();
    trg_broker.connect(&settings.zmq_trigger_endpoint).unwrap();
    trg_broker.set_subscribe("".as_bytes()).unwrap();
    loop{
        let parts = trg_broker.recv_multipart(0).unwrap();
        if parts.len() < 2 {
            continue;
        }
        let result : Result<Measurement, ProtobufError> = parse_from_bytes(&parts[1]);
        if let Ok(measurement) = result {
            //println!("{} : {} {} {}", measurement.box_id, measurement.metrics.get("rms").unwrap().average, measurement.metrics.get("f").unwrap().average, measurement.metrics.get("thd").unwrap().average);
			println!("{} : {} {} {}", measurement.box_id, measurement.metrics.get("f").unwrap().min, measurement.metrics.get("f").unwrap().average, measurement.metrics.get("f").unwrap().max);
        }

    }
}
