extern crate reqwest;
extern crate serde_json;
extern crate chrono;
extern crate bson;
#[macro_use]
extern crate log;
extern crate log4rs;

use log::LevelFilter;
use log4rs::append::file::FileAppender;
use log4rs::encode::pattern::PatternEncoder;
use log4rs::config::{Appender, Config, Root};

use std::time::{Duration, SystemTime, UNIX_EPOCH};
use std::result::Result;
use reqwest::{Response, Error};

use std::fs::File;
use std::io::{BufReader, Read};


use serde_json::Value;

use std::thread;

use chrono::Utc;
use bson::*;
use bson::{Document, TimeStamp};

use mongodb::{Client, ThreadedClient, ClientOptions};
use mongodb::db::ThreadedDatabase;

#[macro_use]
extern crate serde_derive;

#[derive(Default, Debug)]
struct HealthConfig {
    interval: u64,
    mongodb: String,
    services: Vec<Service>,
}

#[derive(Default, Debug)]
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

struct HealthDoc {
    service: String,
    serviceID: String,
    status: String,
    info: String,
    timestamp: TimeStamp,
}

// TODO - set this from the config file
static MONGODB_URI: &str = "mongodb://mongo:27017";

fn main() {
    init_logging();

    let config = parse_config_file("src/services.json");

    loop {
        for service in &config.services {
            query_service(service, &config);
        }
        let health_health = generate_health_health();
        insert_health_doc(&config.mongodb, &health_health);
        thread::sleep(Duration::from_secs((config.interval)));
    }
}

fn parse_config_file(filepath: &str) -> HealthConfig {
    let file = read_file(filepath);

    let json: Value = serde_json::from_str(&file)
        .expect("Unable to parse file as json");

    let interval = json["interval"].as_u64()
        .expect("Error parsing interval");

    let mongodb = json["mongodb"].to_string();

    // This is an array of serde_json values
    let j_services = json["services"].as_array()
        .expect("Error parsing services");

    let mut services: Vec<Service> = Vec::new();
    for s in j_services {
        let service = Service {
            name: s["name"].as_str()
                .expect("Error parsing service name")
                .to_string(),
            url: s["url"].as_str()
                .expect("Error parsing service url")
                .to_string(),
        };
        services.push(service);
    }

    return HealthConfig { interval, mongodb, services };
}

fn read_file(filepath: &str) -> String {
    let file = File::open(filepath)
        .expect("Could not open file");
    let mut buffered_reader = BufReader::new(file);
    let mut contents = String::new();
    let _number_of_bytes: usize = match buffered_reader.read_to_string(&mut contents) {
        Ok(number_of_bytes) => number_of_bytes,
        Err(_err) => 0
    };

    contents
}

fn query_service(service: &Service, config: &HealthConfig) {
    let client = reqwest::Client::builder()
        .timeout(Duration::from_secs(2))
        .build().expect("Unable to build client");

    let req_result = client.get(&(service.url)).send();

    // Check for client/server errors
    let req_error = http_send_err(&req_result);

    if req_error != "" {
        insert_health_doc(&config.mongodb, &generate_error_health_status(service.name.to_string(), req_error.to_string()));
        return;
    }

    // This is a safe unwrap - will not be an error here
    let mut response = req_result.unwrap();
    if response.status() == 200 {
        match response.json() {
            Ok(status) => {
                let stat: HealthStatus = status;
                check_status(&stat, config);
            }
            Err(_) => {
                insert_health_doc(&config.mongodb, &generate_error_health_status(service.name.to_string(), "Unable to parse response".to_string()));
            }
        };
    } else {
        insert_health_doc(&config.mongodb, &generate_error_health_status(service.name.to_string(), response.status().to_string()));
    }
}

// Response may be a non-http error e.g. connection timeout, refused, etc.
fn http_send_err(response: &Result<Response, Error>) -> String {
    match response {
        Ok(_) => "".to_string(),
        Err(e) => e.to_string()
    }
}

fn check_status(status: &HealthStatus, config: &HealthConfig) {
    insert_health_doc(&config.mongodb, status);
    match &status.subcomponents {
        Some(subcomponents) => {
            for component in subcomponents {
                check_status(component, config);
            }
        }
        None => ()
    }
}

fn generate_health_doc(status: &HealthStatus) -> Document {
    // Special case for boxes
    let service: String = {
        match status.name.to_string().parse::<u64>() {
            Ok(_) => "BOX".to_string(),
            Err(_) => status.name.to_string()
        }
    };
    let serviceID: String = {
        if service == "BOX" {
            status.name.to_string()
        } else {
            "".to_string()
        }
    };

    let info: String = {
        match &status.info {
            Some(info) => info.to_string(),
            None => "".to_string()
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

fn insert_health_doc(mongodb: &str, status: &HealthStatus) {
    info!("{:?}", status);
    let mut options = ClientOptions::new();
    options.server_selection_timeout_ms = 1000;
    let mongo = String::from(mongodb);
    // info!("{:?}", mongo);
    let client = match Client::with_uri_and_options(MONGODB_URI, options) {
        Ok(cl) => cl,
        Err(e) => {
            error!("{:?}", e);
            return;
        }
    };
    let coll = client.db("opq").collection("health");
    match coll.insert_one(generate_health_doc(status), None) {
        Ok(_) => (),
        Err(e) => error!("{:?}", e),
    }
}

fn get_status(up: bool, timestamp: u64) -> String {
    let now = SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_secs();
    if up && (now - timestamp < 20){
        return "UP".to_string();
    } else {
        return "DOWN".to_string();
    }
}

// If an error is generated by this health client
fn generate_error_health_status(name: String, message: String) -> HealthStatus {
    let status: HealthStatus = HealthStatus {
        name,
        ok: false,
        timestamp: SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_secs(),
        info: Some(message),
        subcomponents: None,
    };
    status
}

fn init_logging() {
    let logfile = FileAppender::builder()
        .encoder(Box::new(PatternEncoder::new("{d(%Y-%m-%d %H:%M:%S %Z)(utc)}: {l} - {m}\n")))
        .build("/var/log/health/health.log").unwrap();

    let config = Config::builder()
        .appender(Appender::builder().build("logfile", Box::new(logfile)))
        .build(Root::builder()
            .appender("logfile")
            .build(LevelFilter::Info)).unwrap();

    log4rs::init_config(config).unwrap();
}

// Automatically write an up status for this service
fn generate_health_health()-> HealthStatus {
    let status: HealthStatus = HealthStatus {
        name: "HEALTH".to_string(),
        ok: true,
        timestamp: SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_secs(),
        info: None,
        subcomponents: None,
    };
    status
}