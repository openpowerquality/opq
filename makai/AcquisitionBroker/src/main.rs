#[macro_use]
extern crate serde_derive;
#[macro_use]
extern crate mongodb;
#[macro_use]
extern crate lazy_static;

mod config;
mod key_parser;
mod constants;
mod mongo_debug_metric;
mod app_to_box;
mod box_to_app;
mod proto;

use std::env;
use std::fs;
use std::thread;
use std::sync::Arc;

use crate::config::Settings;
use crate::key_parser::parse_key_file;
use crate::app_to_box::app_to_box;
use crate::box_to_app::box_to_app;

fn main() {
    let mut settings = if env::args().len() > 1 {
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
    match pub_key {
        Some(val) => settings.pub_key = Some(val),
        None => {
            println!("Could not parse the public key.");
            return;
        }
    };
    match sec_key {
        Some(val) => settings.sec_key = Some(val),
        None => {
            println!("Could not parse the secret key.");
            return;
        }
    };
    println!("Using public key: {}", settings.pub_key.clone().unwrap());

    let ctx = Arc::new(zmq::Context::new());
    let ctx_clone = ctx.clone();
    let set_clone = settings.clone();
    let _atb = thread::spawn( || {
        app_to_box(ctx_clone, set_clone);
    });
    let ctx_clone = ctx.clone();
    let set_clone = settings.clone();
    let _bta = thread::spawn( || {
        box_to_app(ctx_clone, set_clone);
    });
    _bta.join().unwrap();
}
