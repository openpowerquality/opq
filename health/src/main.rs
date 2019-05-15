#[macro_use]
extern crate serde_derive;
extern crate bson;
extern crate chrono;
extern crate reqwest;
extern crate serde_json;
#[macro_use]
extern crate log;
extern crate env_logger;

use bson::*;
use bson::{Document, TimeStamp};
use chrono::Utc;
use mongodb::db::ThreadedDatabase;
use mongodb::{Client, ThreadedClient};
use std::result::Result;
use std::thread;
use std::time::{Duration, SystemTime, UNIX_EPOCH};

#[inline]
fn now() -> u64 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap()
        .as_secs()
}

#[derive(Default, Debug, Deserialize)]
struct HealthConfig {
    interval: u64,
    mongo_host: String,
    mongo_port: u16,
    services: Vec<Service>,
}

#[derive(Default, Debug, Deserialize)]
struct Service {
    name: String,
    url: String,
}

#[derive(Deserialize, Default, Debug)]
pub struct HealthStatus {
    name: String,
    ok: bool,
    timestamp: u64,
    info: Option<String>,
    subcomponents: Option<Vec<HealthStatus>>,
}

fn main() {
    env_logger::init();

    match parse_config_env() {
        Ok(config) => {
            let http_client = reqwest::Client::builder()
                .timeout(Duration::from_secs(2))
                .build()
                .expect("Unable to build client");
            let mongo_client = mongodb::Client::connect(&config.mongo_host, config.mongo_port)
                .expect("Could not create mongo client");
            loop {
                for service in &config.services {
                    query_service(&http_client, &mongo_client, service);
                }
                let health_health = generate_health_health();
                insert_health_doc(&mongo_client, &health_health);
                thread::sleep(Duration::from_secs(config.interval));
            }
        }
        Err(err) => log::error!(
            "Error loading configuration from the environment: {:?}",
            err
        ),
    }
}

const ENV_VAR: &str = "HEALTH_SETTINGS";
fn parse_config_env() -> Result<HealthConfig, String> {
    match std::env::var(ENV_VAR) {
        Ok(settings) => match serde_json::from_str(&settings) {
            Ok(health_config) => Ok(health_config),
            Err(err) => Err(err.to_string()),
        },
        Err(err) => Err(err.to_string()),
    }
}

fn query_service(http_client: &reqwest::Client, mongo_client: &Client, service: &Service) {
    match http_client.get(&(service.url)).send() {
        Ok(mut resp) => {
            if resp.status() == 200 {
                match resp.json::<HealthStatus>() {
                    Ok(health_status) => check_status(mongo_client, &health_status),
                    Err(err) => insert_health_doc(
                        mongo_client,
                        &generate_error_health_status(
                            service.name.clone(),
                            format!("Error parsing response: {:?}", err),
                        ),
                    ),
                }
            } else {
                insert_health_doc(
                    mongo_client,
                    &generate_error_health_status(
                        service.name.clone(),
                        format!("Error received a resp with code {}", resp.status()),
                    ),
                )
            }
        }
        Err(err) => insert_health_doc(
            mongo_client,
            &generate_error_health_status(service.name.clone(), err.to_string()),
        ),
    }
}

fn check_status(mongo_client: &Client, status: &HealthStatus) {
    insert_health_doc(mongo_client, status);
    if let Some(subcomponents) = &status.subcomponents {
        for component in subcomponents {
            check_status(mongo_client, component);
        }
    }
}

fn generate_health_doc(status: &HealthStatus) -> Document {
    // Special case for boxes
    let service = {
        match status.name.to_string().parse::<u64>() {
            Ok(_) => "BOX".to_string(),
            Err(_) => status.name.to_string(),
        }
    };
    let serviceID = {
        if service == "BOX" {
            status.name.to_string()
        } else {
            "".to_string()
        }
    };

    let info = {
        match &status.info {
            Some(info) => info.to_string(),
            None => "".to_string(),
        }
    };

    let doc = doc! {
    "service": service.to_uppercase(),
    "serviceID": serviceID.to_uppercase(),
    "status": get_status(status.ok, status.timestamp).to_uppercase(),
    "info": info,
    "timestamp": Utc::now()
    };
    doc
}

const OPQ_DB: &str = "opq";
const HEALTH_COLL: &str = "health";
fn insert_health_doc(mongo_client: &Client, status: &HealthStatus) {
    info!("{:?}", status);
    let coll = mongo_client.db(OPQ_DB).collection(HEALTH_COLL);
    if let Err(e) = coll.insert_one(generate_health_doc(status), None) {
        error!("Error inserting health doc: {:?}", e)
    }
}

fn get_status(up: bool, timestamp: u64) -> String {
    let now = now();
    if up && (now - timestamp < 20) {
        "UP".to_string()
    } else {
        "DOWN".to_string()
    }
}

// If an error is generated by this health client
fn generate_error_health_status(name: String, message: String) -> HealthStatus {
    HealthStatus {
        name,
        ok: false,
        timestamp: now(),
        info: Some(message),
        subcomponents: None,
    }
}

// Automatically write an up status for this service
fn generate_health_health() -> HealthStatus {
    HealthStatus {
        name: "HEALTH".to_string(),
        ok: true,
        timestamp: now(),
        info: None,
        subcomponents: None,
    }
}
