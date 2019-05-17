use std::thread;

use crate::{HealthConfig, HealthStatus};
use iron::{mime, status, Handler, Iron, IronError, Request, Response};
use mongodb;
use mongodb::db::ThreadedDatabase;
use mongodb::{Client, ThreadedClient};

const OPQ_DB: &str = "opq";
const HEALTH_COLL: &str = "health";

fn mongo_client(mongo_host: &str, mongo_port: u16) -> Option<Client> {
    let mongo_client: mongodb::error::Result<Client> = Client::connect(mongo_host, mongo_port);
    match mongo_client {
        Ok(client) => Some(client),
        Err(_) => None,
    }
}

struct RequestHandler {
    mongo_host: String,
    mongo_port: u16,
}

impl RequestHandler {
    fn new(mongo_host: String, mongo_port: u16) -> RequestHandler {
        RequestHandler {
            mongo_host,
            mongo_port,
        }
    }

    fn mongo_status(&self) -> bool {
        match mongo_client(&self.mongo_host, self.mongo_port) {
            None => false,
            Some(client) => match client.db(OPQ_DB).collection_names(None) {
                Ok(collection_names) => collection_names.contains(&HEALTH_COLL.to_string()),
                Err(_) => false,
            },
        }
    }
}

impl Handler for RequestHandler {
    fn handle(&self, _: &mut Request) -> Result<Response, IronError> {
        let is_mongo_up = self.mongo_status();
        let health_status = HealthStatus::from_status("mongo".to_string(), is_mongo_up);
        let json = serde_json::to_string(&health_status).expect("Error constructing json");
        let content_type = "application/json".parse::<mime::Mime>().unwrap();
        Ok(Response::with((content_type, status::Ok, json)))
    }
}

pub fn start_mongo_service_checker(health_config: HealthConfig) {
    let builder = thread::Builder::new().name("mongo_service_checker".to_string());
    let join_handle = builder
        .spawn(move || {
            let handler = RequestHandler::new(health_config.mongo_host, health_config.mongo_port);
            let server = Iron::new(handler)
                .http(health_config.mongo_service_checker_addr)
                .expect("Error starting mongo server checker server");
        })
        .expect("Error spawning thread for mongo_service_checker");
}
