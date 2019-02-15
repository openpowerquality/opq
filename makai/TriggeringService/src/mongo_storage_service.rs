use pub_sub::Subscription;

use std::collections::HashMap;
use std::sync::Arc;

use mongodb::Client;
use mongodb::ThreadedClient;
use mongodb::db::ThreadedDatabase;
use mongodb::coll::options::IndexOptions;
use mongodb::coll::options::WriteModel;
use mongodb::coll::options::FindOptions;


use bson::*;
use bson::Document;

use protobuf::{parse_from_bytes,ProtobufError};

use chrono::prelude::*;
use time::Duration;
use zmq;

use crate::constants::*;
use crate::config::Settings;
use crate::proto::opqbox3::{Response,Response_oneof_response} ;


pub struct MongoStorageService{
    client: mongodb::Client,
    ///ZMQ socket to the acquisition broker.
    acq_broker: zmq::Socket,
    identity : String,
}

impl MongoStorageService {
    pub fn new(ctx: &zmq::Context, settings: &Settings) -> MongoStorageService {
        let mut reciever =MongoStorageService{
            client: Client::connect(&settings.mongo_host, settings.mongo_port).unwrap(),
            acq_broker: ctx.socket(zmq::SUB).unwrap(),
            identity : settings.identity.clone().unwrap(),
        };
        reciever
            .acq_broker
            .connect(&settings.zmq_data_endpoint)
            .unwrap();
        reciever.acq_broker.set_subscribe(reciever.identity.as_bytes()).unwrap();;
        reciever
    }

    pub fn run_loop(&mut self){
        let box_event_db = self.client.db(MONGO_DATABASE).collection(MONGO_BOX_EVENTS_COLLECTION);
        let mut event_number = self.find_largest_event_number() + 1;
        println!("Starting from event number {}", event_number);
        loop {
            let msg = self.acq_broker.recv_multipart(0).unwrap();

            let header_result: Result<Response, ProtobufError> = parse_from_bytes(&msg[1]);
            if let Err(_) = header_result {
                println!("Could not parse a data message from the box.");
                continue
            };
            let header = header_result.unwrap();
            if let Response_oneof_response::get_data_response(resp) = header.response.unwrap(){
                let fs_name = "event_".to_string() + &event_number.to_string() + &header.box_id.to_string();

                let box_event = doc!{
                    MONGO_BOX_EVENTS_ID_FIELD : event_number,
                    MONGO_BOX_EVENTS_BOX_ID_FIELD : header.box_id,
                    MONGO_BOX_EVENTS_EVENT_START_FIELD : resp.start_ts,
                    MONGO_BOX_EVENTS_EVENT_END_FIELD : resp.end_ts,
                    MONGO_BOX_EVENTS_LOCATION_FIELD : resp.end_ts,
                    MONGO_BOX_EVENTS_FS_FIELD :fs_name,
                };

                match  box_event_db.insert_one(box_event, None){
                    Ok(_) => {println!("New event {}.", event_number)},
                    Err(E) => {println!("Could not insert event {}.", E)}
                }


                event_number += 1;
            }


        }
    }

    fn find_largest_event_number(&mut self) -> u64{
        let event_db = self.client.db(MONGO_DATABASE).collection(MONGO_BOX_EVENTS_COLLECTION);

        let mut event_number : u64 =0;

        let sort = doc!(
            MONGO_BOX_EVENTS_ID_FIELD : -1,
        );
        let filter = doc!{
            MONGO_BOX_EVENTS_ID_FIELD : 1
        };
        let mut opt = FindOptions::new();
        opt.sort = Some(sort);
        opt.projection = Some(filter);

        let item = event_db.find_one(None, Some(opt));
        let event_number  = match item {
            Ok(Some(doc)) => match doc.get(MONGO_BOX_EVENTS_ID_FIELD) {
                Some(&Bson::I32(ref num)) => num.clone() as u64,
                _ => 0 as u64,
            },
            Ok(None)  =>0 as u64,
            Err(_) => 0 as u64,
        } ;
        event_number
    }

    fn find_latest_location()

}

