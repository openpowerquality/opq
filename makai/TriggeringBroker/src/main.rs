#[macro_use]
extern crate serde_derive;
#[macro_use]
extern crate mongodb;

mod config;
mod key_parser;
mod constants;
mod mongo_debug_metric;

use std::env;
use std::fs;
use std::time::Instant;

use crate::config::Settings;
use crate::key_parser::parse_key_file;
use crate::mongo_debug_metric::MongoStorageService;

use zmq::Socket;

fn main() {
    let settings = if env::args().len() > 1 {
        let args: Vec<String> = env::args().collect();
        match Settings::load_from_file(args[1].clone()) {
            Ok(s) => s,
            Err(e) => {
                println!(
                    "Could not load a settings file from the filesystem {}: {}",
                    "MAKAI_SETTINGS", e
                );
                return;
            }
        }
    } else {
        match Settings::load_from_env(constants::ENVIRONMENT_SETTINGS_VAR) {
            Ok(s) => s,
            Err(e) => {
                println!(
                    "Could not load a settings file from the environment {}: {}",
                    constants::ENVIRONMENT_SETTINGS_VAR, e
                );
                return;
            }
        }
    };
    let contents = fs::read_to_string(&settings.server_cert)
        .expect("Could not read server key file");
    ;
    let (pub_key, sec_key) = parse_key_file(&contents);
    let pub_key = match pub_key {
        Some(val) => val,
        None => {
            println!("Could not parse the public key.");
            return;
        }
    };
    let sec_key = match sec_key {
        Some(val) => val,
        None => {
            println!("Could not parse the secret key.");
            return;
        }
    };
    println!("Using public key: {}", pub_key);

    let ctx = zmq::Context::new();
    let interface = ctx.socket(zmq::SUB).unwrap();
    let backend: Socket = ctx.socket(zmq::PUB).unwrap();
    interface.set_curve_server(true).unwrap();
    interface.set_curve_secretkey(&sec_key).unwrap();
    interface.set_curve_publickey(&pub_key).unwrap();
    interface.bind(&settings.interface).unwrap();
    interface.set_subscribe(b"").unwrap();
    backend.bind(&settings.backend).unwrap();

    let mut debug_metric = None;

    if settings.metric_update_sec > 0 {
        debug_metric = Some(MongoStorageService::new(&settings))
    }
    let mut last_update = Instant::now();
    let mut accum_bytes: u32 = 0;
    loop {
        let  msg = interface.recv_multipart(0).unwrap();
        let mut array = vec![];
        for p in msg.as_slice(){
            let b: &[u8] = p;
            array.push(b);
        }
        backend.send_multipart(&array, 0).unwrap();


        match &debug_metric {
            None => {}
            Some(dm) => {
                for part in msg.iter() {
                    accum_bytes += part.len() as u32;
                }
                if last_update.elapsed().as_secs() > settings.metric_update_sec {
                    dm.store_metric_in_db(accum_bytes);
                    last_update = Instant::now();
                    accum_bytes = 0;
                }
            }
        };
    }
}
