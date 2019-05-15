#[macro_use]
extern crate serde_derive;

use std::env;

mod config;
mod constants;
mod mongo_event_storage;
mod mongo_ttl;
mod proto;

use crate::config::Settings;
use crate::mongo_event_storage::MongoStorageService;

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
                    constants::ENVIRONMENT_SETTINGS_VAR,
                    e
                );
                return;
            }
        }
    };
    let ctx = zmq::Context::new();
    let mut mongo_event_storage = MongoStorageService::new(&ctx, &settings);
    mongo_event_storage.run_loop();
}
