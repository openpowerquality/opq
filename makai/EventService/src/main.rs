#[macro_use]
extern crate serde_derive;

use std::env;

use crate::config::Settings;
use crate::mongo_event_storage::MongoStorageService;

use env_logger;
use std::sync::Arc;

mod config;
mod constants;
mod event_ids;
mod mongo_event_storage;
mod mongo_ttl;
mod proto;

fn main() {
    env_logger::init();

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

    let event_id_service = event_ids::EventIdService::with_settings(&settings);
    let event_id_service = Arc::new(event_id_service);

    let ctx = zmq::Context::new();

    let event_id_broker = event_ids::EventIdBroker::new(event_id_service.clone(), &ctx, &settings);
    event_id_broker.run_service();

    let mut mongo_event_storage =
        MongoStorageService::new(&ctx, &settings, event_id_service.clone());
    mongo_event_storage.run_loop();
}
