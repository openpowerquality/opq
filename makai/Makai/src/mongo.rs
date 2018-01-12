extern crate bson;
extern crate mongodb;
extern crate chrono;
extern crate time;
extern crate pub_sub;

use mongodb::{ThreadedClient};
use mongodb::db::ThreadedDatabase;
use mongodb::coll::options::IndexOptions;

use bson::*;
use chrono::prelude::*;
use time::Duration;


use constants::*;
use opq::*;

pub struct MongoMeasurements{
    sub_chan : pub_sub::Subscription<TriggerMessage>,
    coll : mongodb::coll::Collection
}

impl MongoMeasurements {
    pub fn new(client : &mongodb::Client, sub_chan : pub_sub::Subscription<TriggerMessage>) -> MongoMeasurements{
        let ret = MongoMeasurements{sub_chan : sub_chan,
            coll : client.db(OPQ_DATABASE).collection(OPQ_MEASUREMENTS_COLLECTION)};
        let mut index_opts = IndexOptions::new();
        index_opts.expire_after_seconds = Some(0);
        index_opts.background = Some(true);
        ret.coll.create_index(doc!{"expireAt" : 1}, Some(index_opts)).unwrap();
        ret

    }

    pub fn run_loop(&self){
        loop{
            let trigger_message = self.sub_chan.recv().unwrap();
            let expire_time : DateTime<Utc> = Utc::now() + Duration::seconds(OPQ_MEASUREMENTS_EXPIRE_TIME_SECONDS);
            let bson_expire_time = Bson::from(expire_time);


            let mut doc =doc!{
                "box_id": trigger_message.get_id().to_string(),
                "timestamp_ms" : trigger_message.get_time() as u64,
                "voltage" : trigger_message.get_rms() as f32,
                "frequeny" : trigger_message.get_frequency() as f32,
                "expireAt": bson_expire_time
            };
            if trigger_message.has_thd(){
                doc.insert("thd", trigger_message.get_thd());
            }
            self.coll.insert_one(doc, None).ok().expect("Could not insert");
        }
    }
}



