extern crate reqwest;
extern crate serde_json;
extern crate chrono;
extern crate bson;

use std::time::Duration;
use std::result::Result;
use reqwest::{Response, Error};
//use std::collections::HashMap;

// File reading stuff
use std::fs::File;
use std::io::BufReader;
use std::io::Read;

// json stuff
use serde_json::Value;

use std::thread;

use chrono::{DateTime, Utc};
use bson::*;
use bson::Document;
use bson::TimeStamp;

use mongodb;
use mongodb::Client;
use mongodb::ThreadedClient;
use mongodb::ClientOptions;
use mongodb::db::ThreadedDatabase;

#[macro_use]
extern crate serde_derive;

#[derive(Default, Debug)]
struct Config {
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
    subcomponents: Vec<HealthStatus>,
}

struct HealthDoc {
    service: String,
    serviceID: String,
    status: String,
    info: String,
    timestamp: TimeStamp,
}

fn main() {
    let config = parse_config_file("src/services.json");

    loop {
        for service in &config.services {
            check_service(service, &config.mongodb);
        }
        thread::sleep_ms((config.interval * 1000) as u32);
    }
}

fn parse_config_file(filepath: &str) -> Config {
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

    return Config { interval, mongodb, services };
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

fn check_service(service: &Service, mongodb: &str) {
    let client = reqwest::Client::builder()
        .timeout(Duration::from_secs(2))
        .build().expect("Unable to build client");

    let req_result = client.get(&(service.url)).send();

    // Check for client/server errors
    let req_error = http_send_err(&req_result);

    if req_error != "" {
        println!("{} {} is DOWN Error: {}", Utc::now(), service.name, req_error);
    } else {
        let mut response = req_result.unwrap();
        if response.status() == 200 {
            // println!("{} {} is UP", Utc::now(), service.name);
            match response.json() {
                Ok(status) => insert_health_doc(status, mongodb),
                Err(_) => println!("Unable to parse response")
            };
        } else {
            println!("{} {} is DOWN Error: {}", Utc::now(), service.name, response.status());
        }
    }
}

// Response may be a non-http error e.g. connection timeout, refused, etc.
// Why is it so hard to get the error?
fn http_send_err(response: &Result<Response, Error>) -> &str {
    let mut error = "";
    match response {
        Err(e) => {
            // println!("{:?}", e.get_ref().unwrap());
            match e.get_ref() {
                Some(nested_e) => match nested_e.cause() {
                    Some(nested_e) => {
                        // println!("{:?}", nested_e.description());
                        error = nested_e.description()
                    }
                    _ => error = "Unable to parse error"
                },
                _ => error = "Unable to parse error"
            }
            error
        }
        Ok(_) => ""
    }
}

fn insert_health_doc(status: HealthStatus, mongodb: &str) {
    let mut options = ClientOptions::new();
    options.server_selection_timeout_ms = 1000;
    let client = Client::with_uri_and_options(mongodb, options)
        .expect("Can't connect to mongo");
    let coll = client.db("opq").collection("healthv2");
    let mut doc = doc! {
        "service": status.name,
        "serviceID": "".to_string(),
        "status": get_status(status.ok),
        "info": "".to_string(),
        "timestamp": Utc::now()
        };
    coll.insert_one(doc, None).unwrap();
}

fn get_status(up: bool) -> String {
    if up {
        return "UP".to_string()
    } else {
        return "DOWN".to_string()
    }
}

