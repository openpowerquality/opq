use std::collections::HashMap;
use std::io::Write;
use std::time::Instant;

use bson::*;
use mongodb::coll::options::FindOptions;
use mongodb::coll::Collection;
use mongodb::db::ThreadedDatabase;
use mongodb::gridfs::Store;
use mongodb::gridfs::ThreadedStore;
use mongodb::Client;
use mongodb::ThreadedClient;

use protobuf::{parse_from_bytes, ProtobufError};

use zmq;

use crate::config::Settings;
use crate::constants::*;
use crate::event_ids::EventIdService;
use crate::mongo_ttl;
use crate::proto::opqbox3::{Cycle, Response, Response_oneof_response};
use std::sync::Arc;

pub struct MongoStorageService {
    client: mongodb::Client,
    ///ZMQ socket to the acquisition broker.
    acq_broker: zmq::Socket,
    event_broker: zmq::Socket,
    id_to_event: HashMap<String, (i32, std::time::Instant)>,
    ttl: u64,
    event_id_service: Arc<EventIdService>,
}

impl MongoStorageService {
    pub fn new(
        ctx: &zmq::Context,
        settings: &Settings,
        event_id_service: Arc<EventIdService>,
    ) -> MongoStorageService {
        let receiver = MongoStorageService {
            client: Client::connect(&settings.mongo_host, settings.mongo_port).unwrap(),
            acq_broker: ctx.socket(zmq::SUB).unwrap(),
            event_broker: ctx.socket(zmq::PUB).unwrap(),
            ttl: settings.ttl_cache_ttl,
            id_to_event: HashMap::new(),
            event_id_service,
        };
        receiver
            .acq_broker
            .connect(&settings.zmq_data_endpoint)
            .unwrap();
        receiver
            .acq_broker
            .set_subscribe(ZMQ_DATA_PREFIX.as_bytes())
            .unwrap();
        receiver
            .event_broker
            .bind(&settings.zmq_event_endpoint)
            .unwrap();

        receiver
    }

    pub fn run_loop(&mut self) {
        let box_event_db = self
            .client
            .db(MONGO_DATABASE)
            .collection(MONGO_BOX_EVENTS_COLLECTION);
        let event_db = self
            .client
            .db(MONGO_DATABASE)
            .collection(MONGO_EVENTS_COLLECTION);
        let fs = Store::with_db(self.client.db(MONGO_DATABASE).clone());
        //        self.next_event_number = self.event_id_service.inc_and_get();
        println!("Current highest event_id {}", self.event_id_service.peak());

        let mut ttl = mongo_ttl::CachedTtlProvider::new(self.ttl, &self.client);

        loop {
            let msg = self.acq_broker.recv_multipart(0).unwrap();
            if msg.len() < 2 {
                continue;
            }
            let (event_number, identity, update) =
                self.get_event_number(&String::from_utf8(msg[0].clone()).unwrap());
            let header_result: Result<Response, ProtobufError> = parse_from_bytes(&msg[1]);
            if let Err(_) = header_result {
                println!("Could not parse a data message from the box.");
                continue;
            };
            let header = header_result.unwrap();
            if let Response_oneof_response::get_data_response(resp) = header.response.unwrap() {
                if update {
                    MongoStorageService::update_event(&event_db, event_number, header.box_id);
                } else {
                    let event = doc! {
                        MONGO_EVENTS_ID_FIELD : event_number,
                        MONGO_EVENTS_DESCRIPTION_FIELD: "Makai id ".to_string() + &identity.clone(),
                        MONGO_EVENTS_TRIGGERED_FIELD: [header.box_id.to_string()],
                        MONGO_EVENTS_RECEIVED_FIELD: [header.box_id.to_string()],
                        MONGO_EVENTS_START_FIELD:  resp.start_ts,
                        MONGO_EVENTS_END_FIELD: resp.end_ts,
                        MONGO_EVENTS_EXPIRE_AT : mongo_ttl::timestamp_s() + ttl.get_events_ttl(),
                    };
                    match event_db.insert_one(event, None) {
                        Ok(_) => {}
                        Err(e) => println!("Could not insert event {}.", e),
                    }
                    self.event_broker
                        .send_multipart(
                            &[identity.as_bytes(), event_number.to_string().as_bytes()],
                            0,
                        )
                        .unwrap();
                }
                let fs_name = "event_".to_string()
                    + &event_number.to_string()
                    + "_"
                    + &header.box_id.to_string();

                let box_event = doc! {
                    MONGO_BOX_EVENTS_ID_FIELD : event_number,
                    MONGO_BOX_EVENTS_BOX_ID_FIELD : header.box_id.to_string(),
                    MONGO_BOX_EVENTS_EVENT_START_FIELD : resp.start_ts,
                    MONGO_BOX_EVENTS_EVENT_END_FIELD : resp.end_ts,
                    MONGO_BOX_EVENTS_LOCATION_FIELD : resp.end_ts,
                    MONGO_BOX_EVENTS_FS_FIELD : fs_name.clone(),
                    MONGO_BOX_EVENTS_LOCATION_FIELD : self.find_latest_location(header.box_id as u32),
                };

                match box_event_db.insert_one(box_event, None) {
                    Ok(_) => println!("New event {}.", event_number),
                    Err(e) => println!("Could not insert event {}.", e),
                }
                let mut data_file = fs.create(fs_name).unwrap();
                for cycle_num in 2..msg.len() {
                    let cycle_result: Result<Cycle, ProtobufError> =
                        parse_from_bytes(&msg[cycle_num]);
                    if let Err(_) = cycle_result {
                        println!("Could not parse a data message from the box.");
                        continue;
                    };
                    let cycle = cycle_result.unwrap();
                    let mut data_to_write = vec![];
                    for sample in cycle.datapoints {
                        let high = ((sample >> 8) & 0xFF) as u8;
                        let low = (sample & 0xFF) as u8;
                        data_to_write.push(low);
                        data_to_write.push(high);
                    }
                    data_file.write_all(&data_to_write).unwrap();
                }
            }
        }
    }

    fn update_event(event_db: &Collection, event_number: i32, box_id: i32) {
        let event = doc! {
            MONGO_EVENTS_ID_FIELD : event_number,
        };
        let update = doc! {
                    "$push" : doc!{
                        MONGO_EVENTS_TRIGGERED_FIELD : box_id.to_string(),
                    }
        };
        match event_db.update_one(event, update, None) {
            Ok(_) => {}
            Err(e) => println!("Could not update event {}.", e),
        }
        let event = doc! {
            MONGO_EVENTS_ID_FIELD : event_number,
        };
        let update = doc! {
                    "$push" : doc!{
                        MONGO_EVENTS_RECEIVED_FIELD : box_id.to_string(),
                    }
        };
        match event_db.update_one(event, update, None) {
            Ok(_) => {}
            Err(e) => println!("Could not update event {}.", e),
        }
    }

    //    fn find_largest_event_number(&mut self) -> i32 {
    //        let event_db = self
    //            .client
    //            .db(MONGO_DATABASE)
    //            .collection(MONGO_EVENTS_COLLECTION);
    //
    //        let sort = doc!(
    //            MONGO_BOX_EVENTS_ID_FIELD : -1,
    //        );
    //        let filter = doc! {
    //            MONGO_BOX_EVENTS_ID_FIELD : 1
    //        };
    //        let mut opt = FindOptions::new();
    //        opt.sort = Some(sort);
    //        opt.projection = Some(filter);
    //
    //        let query_result = event_db.find_one(None, Some(opt));
    //        match query_result {
    //            Ok(Some(doc)) => match doc.get(MONGO_EVENTS_ID_FIELD) {
    //                Some(&Bson::I32(ref num)) => num.clone() as i32,
    //                _ => 0 as i32,
    //            },
    //            Ok(None) => 0 as i32,
    //            Err(_) => 0 as i32,
    //        }
    //    }

    fn find_latest_location(&mut self, box_id: u32) -> String {
        let box_col = self
            .client
            .db(MONGO_DATABASE)
            .collection(MONGO_OPQ_BOXES_COLLECTION);
        //Query mongo for box location
        let query = doc! {
          MONGO_OPQ_BOXES_BOX_ID_FIELD : box_id.to_string(),
        };

        let filter = doc! {
            MONGO_OPQ_BOXES_LOCATION_FIELD : 1,
        };

        let mut opt = FindOptions::new();
        opt.projection = Some(filter);

        let query_result = box_col.find_one(Some(query), Some(opt));
        match query_result {
            Ok(Some(doc)) => match doc.get(MONGO_OPQ_BOXES_LOCATION_FIELD) {
                Some(&Bson::String(ref location)) => location.clone(),
                _ => String::new(),
            },
            Ok(None) => String::new(),
            Err(_) => String::new(),
        }
    }

    fn get_event_number(&mut self, topic: &String) -> (i32, String, bool) {
        let (event_token, identity) = match parse_topic(&topic) {
            Ok((id, identity)) => (id, identity),
            Err(_) => ("".to_string(), "".to_string()),
        };

        let (id, update) = if self.id_to_event.contains_key(&event_token) {
            let (id, _) = self.id_to_event.get(&event_token).unwrap();
            (id.clone(), true)
        } else {
            let id = self.event_id_service.inc_and_get();
            //            self.next_event_number += 1;
            self.id_to_event.insert(event_token, (id, Instant::now()));
            (id, false)
        };
        self.id_to_event = self
            .id_to_event
            .clone()
            .into_iter()
            .filter(|(ref _token, (_id, time))| {
                time.elapsed().as_secs() < EVENT_TOKEN_EXPIRE_SECONDS as u64
            })
            .collect();

        return (id, identity, update);
    }
}

fn parse_topic(topic: &String) -> Result<(String, String), String> {
    let pieces: Vec<&str> = topic.split(ZMQ_FIELD_SEPARATOR).collect();
    if pieces.len() < 3 {
        return Err("Could not parse topic".to_string());
    }
    Ok((pieces[1].to_string(), pieces[2].to_string()))
}
