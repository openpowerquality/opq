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
use bson::TimeStamp;

#[derive(Default, Debug)]
struct Config {
    interval: u64,
    services: Vec<Service>,
}

#[derive(Default, Debug)]
struct Service {
    name: String,
    url: String,
}

struct HealthDoc {
    service: String,
    serviceID: String,
    status: String,
    info: String,
    timestamp: TimeStamp
}

fn main() {
    let config = parse_config_file("src/services.json");

    loop {
        for service in &config.services {
            check_service(service);
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

    return Config { interval, services };
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

fn check_service(service: &Service) {
    let client = reqwest::Client::builder()
        .timeout(Duration::from_secs(2))
        .build().expect("Unable to build client");

    let req_result = client.get(&(service.url)).send();

    if is_error(&req_result) {
        println!("{}: {} is DOWN", Utc::now(), service.name);
    } else {
        let response = req_result.unwrap();
        if response.status() == 200 {
            println!("{}: {} is UP", Utc::now(), service.name);
        } else {
            println!("{}: {} is DOWN", Utc::now(), service.name);
        }
    }
}

// Response may be a non-http error e.g. connection timeout, refused, etc.
fn is_error(response: &Result<Response, Error>) -> bool {
    match response {
        Err(e) => {
            // println!("{:?}", e);
            true
        }
        Ok(_) => false
    }
}

