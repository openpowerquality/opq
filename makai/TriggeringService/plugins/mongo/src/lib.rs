#[macro_use]
extern crate triggering_service;
use std::str;
use triggering_service::makai_plugin::MakaiPlugin;
use triggering_service::proto::opqbox3::Measurement;
use triggering_service::proto::opqbox3::Command;
use std::sync::Arc;

//#[macro_use(bson, doc)]
//extern crate mongodb;
use mongodb::{Bson, bson, doc};
use mongodb::{Client, ThreadedClient};
use mongodb::db::ThreadedDatabase;

//extern crate bson;
//use bson::Document;
//use chrono::prelude::*;
//use std::time::Duration;
use chrono::{DateTime, Utc, Duration};

//extern crate triggering_service::constants::*;

mod constants;
use constants::*;

#[macro_use] extern crate serde_derive;
extern crate serde;
extern crate serde_json;

#[derive(Serialize, Deserialize, Default, Debug)]
struct MongoPluginSettings{
    pub host : &'static str,
    pub port : u16,
    pub measurement_expiration_seconds : i64
}

#[derive(Debug, Default)]
pub struct MongoPlugin{
    settings: MongoPluginSettings,
    client: Client,
    live_coll: mongodb::coll::Collection,
    slow_coll: mongodb::coll::Collection
}

impl MongoPlugin {
    fn new() -> MongoPlugin{
        MongoPlugin{
            //settings : MongoPluginSettings::default(),
            //client : Client::connect("localhost", 27017).expect("adfa")
        }
    }
}

impl MakaiPlugin for MongoPlugin {

    fn name(&self) -> &'static str  {
        "Mongo Plugin"
    }

    fn process_measurement(&mut self, msg: Arc<Measurement>) -> Option<Vec<Command>> {
        // Get voltage, frequency and thd...
        let metrics = msg.get_metrics();
        let volt = metrics.get("rms").expect("Unable to retrieve voltage.");
        let freq = metrics.get("f").expect("Unable to retrieve frequency.");
        let thd = metrics.get("thd").expect("Unable to retrieve frequency.");
        let expire_time: DateTime<Utc> =
            Utc::now() + Duration::seconds(self.settings.measurement_expiration_seconds as i64);
        let bson_expire_time = Bson::from(expire_time);

        // Insert live measurement
        let mut doc = doc! {
            MONGO_BOX_ID_FIELD : msg.box_id.to_string(),
            MONGO_TIMESTAMP_FIELD : msg.timestamp_ms as u64,
            MONGO_MEASUREMENTS_VOLTAGE_FIELD : volt.get_average() as f32,
            MONGO_MEASUREMENTS_FREQUENCY_FIELD : freq.get_average() as f32,
            MONGO_MEASUREMENTS_THD_FIELD: thd.get_average() as f32,
            MONGO_EXPIRE_FIELD : bson_expire_time
        };
        self.live_coll.insert_one(doc.clone(), None).ok().expect("Failed to insert measurement.");

        // let latest = self.slow_coll.find().sort({time_stamp_ms:-1}).limit(1);
        // if (latest.time_stamp_ms + self.settings.trends_update_interval_seconds < )

        /* Check if trends need to be inserted and then updated code below:
        //Query mongo for box location
        let query  = doc!{
        MONGO_OPQ_BOXES_BOX_ID_FIELD : msg.get_id().to_string(),
        };
        let query_result = self.box_coll.find_one(Some(query), None).unwrap();
        //Fill in the location for the long term measurement if it is present.
        match query_result{
            None => {
                doc.insert(MONGO_LONG_TERM_MEASUREMENTS_LOCATION_FIELD, MONGO_LONG_TERM_MEASUREMENTS_DEFAULT_LOCATION);
            },
            Some(query) => {
                match query.get(MONGO_OPQ_BOXES_LOCATION_FIELD){
                    None => {
                        doc.insert(MONGO_LONG_TERM_MEASUREMENTS_LOCATION_FIELD, MONGO_LONG_TERM_MEASUREMENTS_DEFAULT_LOCATION);
                    },
                    Some(location) => {doc.insert(MONGO_LONG_TERM_MEASUREMENTS_LOCATION_FIELD, location.clone());},
                }
            }
        };
        //Insert the long term measurement.
        self.slow_coll
            .insert_one(doc, None)
            .ok()
            .expect("Could not insert");
        */

        None
    }

    fn on_plugin_load(&mut self, args : String) {
        let set = serde_json::from_str(&args);
        self.settings = match set{
            Ok(s) => {s},
            Err(e) => {println!("Bad settings file for plugin {}: {:?}", self.name(), e); MongoPluginSettings::default()}
        };

        self.client = Client::connect(self.settings.host, self.settings.port).expect("Failed to initialize client.");
        self.live_coll = self.client.db(MONGO_DATABASE).collection(MONGO_MEASUREMENT_COLLECTION);
        self.slow_coll = self.client.db(MONGO_DATABASE).collection(MONGO_LONG_TERM_MEASUREMENT_COLLECTION);
    }

    fn on_plugin_unload(&mut self) {
        println!("Mongo plugin unloaded.");
    }
}

declare_plugin!(MongoPlugin, MongoPlugin::new);
