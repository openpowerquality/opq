use pub_sub::Subscription;

use std::collections::HashMap;
use std::sync::Arc;

use mongodb;
use mongodb::Client;
use mongodb::ThreadedClient;
use mongodb::db::ThreadedDatabase;
use mongodb::coll::options::IndexOptions;

use bson::*;
use bson::Document;

use chrono::prelude::*;
use time::Duration;

use crate::constants::*;
use crate::proto::opqbox3::{Metric, Measurement};

use crate::config::Settings;
use crate::mongodb::coll::options::WriteModel;
use crate::mongo_ttl::CachedTtlProvider;


struct MetricStatistics {
    ///Maximum value.
    pub min: f32,
    ///Minimum value.
    pub max: f32,
    ///Accumulator for computing averages.
    average_accum: f32,
    ///Number of elements processed so far.
    count: u32,
}


impl MetricStatistics {
    ///Creates a new measurements statistical buffer.
    /// # Arguments
    /// * `new_value` - new value to process.
    pub fn new(new_metric: &Metric) -> MetricStatistics {
        MetricStatistics {
            min: new_metric.min,
            max: new_metric.max,
            average_accum: new_metric.average,
            count: 1,
        }
    }

    ///Updates the buffer with a new value.
    /// #Arguments
    /// * `new_value` - new value to process.
    pub fn update(&mut self, new_metric: &Metric) {
        if new_metric.min < self.min {
            self.min = new_metric.min;
        } else if new_metric.max > self.max {
            self.max = new_metric.max;
        }

        self.average_accum += new_metric.average;
        self.count += 1;
    }
    ///Computes the average.
    pub fn get_average(&mut self) -> f32 {
        self.average_accum / (self.count as f32)
    }
}


/// A Buffer for keeping track of the slow measurements.

///Decimator for a single device.
struct MeasurementDecimator {
    measurements: HashMap<&'static str, MetricStatistics>,
    pub last_insert: DateTime<Utc>,
}


impl MeasurementDecimator {
    ///Created a new decimator.
    pub fn new() -> MeasurementDecimator {
        MeasurementDecimator {
            measurements: HashMap::new(),
            last_insert: Utc::now()
//            cached_ttl_provider
        }
    }
    ///Clears the buffers.
    fn clear(&mut self) {
        self.measurements.clear();
        self.last_insert = Utc::now();
    }

    ///Processes the next message.
    /// # Arguments:
    /// * `msg`- A new triggering message from a box with matching id.
    pub fn process_message(&mut self, msg: &Measurement) {
        for (proto_name, mongo_name) in MONGO_FIELD_REMAP.iter() {
            if msg.metrics.contains_key(&proto_name.to_string()) {
                let new_metric = msg.metrics.get(&proto_name.to_string()).unwrap();
                match self.measurements.get_mut(mongo_name.clone()) {
                    None => { self.measurements.insert(mongo_name.clone(), MetricStatistics::new(new_metric)); }
                    Some(value) => { value.update(new_metric); }
                };
            }
        }
    }


    ///Generates a bson document based on the values returned, clears the internal statistics, and resets the clock.
    pub fn generate_document_and_reset(&mut self, expire_at: u64) -> Document {
        let mut ret = Document::new();
        for ( measurement, statistic ) in self.measurements.iter_mut(){

            ret.insert(
                measurement.to_string(),
                doc! {
                        MONGO_LONG_TERM_MEASUREMENTS_MIN_FIELD : statistic.min,
                        MONGO_LONG_TERM_MEASUREMENTS_MAX_FIELD : statistic.max,
                        MONGO_LONG_TERM_MEASUREMENTS_FILTERED_FIELD : statistic.get_average(),
                        MONGO_EXPIRE_FIELD : expire_at
                    },
            );
        }
        self.clear();
        ret
    }
}

///This object is responsible for processing measurement messages.
pub struct MongoMetricStorage {
    sub_chan: Subscription<Arc<Measurement>>,
    live_coll: mongodb::coll::Collection,
    slow_coll: mongodb::coll::Collection,
    box_coll: mongodb::coll::Collection,
    ///Mongo Expire time
    expire_time_sec: u64,
    ///Mongo Trends time
    trend_time_sec: u64,

    cached_ttl_provider: CachedTtlProvider
}

impl MongoMetricStorage {
    ///Creates a new mongo measurement store.
    /// # Arguments
    /// * `client` -  a reference to a mongodb client instance.
    /// * `sub_chan` -  a channel for receiving triggering messages.
    pub fn new(
        sub_chan: Subscription<Arc<Measurement>>,
        settings: &Settings,
    ) -> MongoMetricStorage {
        let client = Client::connect(&settings.mongo_host, settings.mongo_port).unwrap();
        let ret = MongoMetricStorage {
            sub_chan,
            live_coll: client
                .db(MONGO_DATABASE)
                .collection(MONGO_MEASUREMENT_COLLECTION),
            box_coll : client
                .db(MONGO_DATABASE)
                .collection(MONGO_OPQ_BOXES_COLLECTION),
            slow_coll: client
                .db(MONGO_DATABASE)
                .collection(MONGO_LONG_TERM_MEASUREMENT_COLLECTION),
            expire_time_sec: settings.mongo_measurement_expiration_seconds,
            trend_time_sec: settings.mongo_trends_update_interval_seconds,
            cached_ttl_provider: CachedTtlProvider::new(60, &client)
        };

        ret
    }

    ///Generate a new bson document for the live measurements.
    /// # Arguments
    /// * `msg` a new trigger message to process.
    fn generate_document(&mut self, msg: &Measurement) -> Document {
//        let expire_time: DateTime<Utc> =
//            Utc::now() + Duration::seconds(self.expire_time_sec as i64);
//        let bson_expire_time = Bson::from(expire_time);
        let mut doc = doc! {
            MONGO_BOX_ID_FIELD : msg.box_id.to_string(),
            MONGO_TIMESTAMP_FIELD : msg.timestamp_ms as u64,
            MONGO_EXPIRE_FIELD : self.cached_ttl_provider.get_measurements_ttl()
        };
        for (proto_name, mongo_name) in MONGO_FIELD_REMAP.iter() {
            if let Some(metric) = msg.metrics.get(proto_name.clone()) {
                doc.insert(mongo_name.to_string(), metric.average);
            };
        }


        doc
    }

    ///The mongo store loop. Run this in a thread.
    pub fn run_loop(&mut self) {
        let mut map = HashMap::new();
        let mut update_backlog :Vec<WriteModel> = vec!();
        let mut last_update =  Utc::now();

        loop {
            let msg = self.sub_chan.recv().unwrap();
            let doc = self.generate_document(&msg);

            update_backlog.push(mongodb::coll::options::WriteModel::InsertOne{ document: doc });
            if  Utc::now() - last_update > Duration::seconds(1) {
                self.live_coll.bulk_write(update_backlog, false);
                update_backlog = vec![];
                last_update = Utc::now();
            }


            let box_stat = map.entry(msg.box_id)
                .or_insert(MeasurementDecimator::new());


            box_stat.process_message(&msg);
            if box_stat.last_insert + Duration::seconds(self.trend_time_sec as i64) < Utc::now() {
                //Build the long term measurement header
                let mut doc = box_stat.generate_document_and_reset(self.cached_ttl_provider.get_trends_ttl());
                doc.insert(MONGO_BOX_ID_FIELD, msg.box_id.to_string());
                doc.insert(MONGO_TIMESTAMP_FIELD, msg.timestamp_ms);

                //Query mongo for box location
                let query  = doc!{
                  MONGO_OPQ_BOXES_BOX_ID_FIELD : msg.box_id.to_string(),
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
                    },
                };
                //Insert the long term measurement.
                self.slow_coll
                    .insert_one(doc, None)
                    .ok()
                    .expect("Could not insert");
            }
        }
    }
}
