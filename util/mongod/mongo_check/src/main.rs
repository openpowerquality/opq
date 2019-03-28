extern crate mongodb;
#[macro_use]
extern crate rouille;
#[macro_use]
extern crate serde_derive;

use std::time::{SystemTime};
use mongodb::{Client, ThreadedClient, ClientOptions};

#[derive(Serialize)]
struct resp {
    ok: bool,
    name: String,
    timestamp: SystemTime
}

fn main() {

    rouille::start_server("localhost:28420", move |request| {
        router!(request,
            (GET) (/) => {
                let response = resp {
                    ok: mongo_is_up(),
                    name: String::from("mongo"),
                    timestamp: SystemTime::now()
                };
                rouille::Response::json(&response)
            },
            _ => rouille::Response::empty_404()
        )
    });
}

fn mongo_is_up() -> bool {
    let mut cl_opt = ClientOptions::new();
    cl_opt.server_selection_timeout_ms =  1000;

    let client = match Client::connect_with_options("localhost", 27017, cl_opt) {
        Ok(cl) => match cl.database_names() {
            Ok(_) => true,
            Err(_) => false
        },
        Err(_) => false
    };

    println!("Client is up: {}", client);

    client
}
