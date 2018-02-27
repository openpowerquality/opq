use pub_sub::Subscription;

use std::collections::HashMap;
use std::sync::Arc;

use mongodb;
use mongodb::ThreadedClient;
use mongodb::db::ThreadedDatabase;
use mongodb::coll::options::IndexOptions;
use bson::*;
use bson::Document;

use chrono::prelude::*;
use time::Duration;

use constants::*;
use opqapi::protocol::{TriggerMessage};
use config::Settings;

/// A Buffer for keeping track of the slow measurements.
struct MeasurementStatistics {
    ///Maximum value.
    pub min: f32,
    ///Minimum value.
    pub max: f32,
    ///Accumulator for computing averages.
    average_accum: f32,
    ///Number of elements processed so far.
    count: u32
}

impl MeasurementStatistics {
    ///Creates a new measurements statistical buffer.
    /// # Arguments
    /// * `new_value` - new value to process.
    pub fn new(new_value : f32) -> MeasurementStatistics{
        MeasurementStatistics{
            min: new_value,
            max: new_value,
            average_accum: new_value,
            count : 1
        }
    }

    ///Updates the buffer with a new value.
    /// #Arguments
    /// * `new_value` - new value to process.
    pub fn update(&mut self, new_value: f32) {
        if new_value < self.min {
            self.min = new_value;
        } else if new_value > self.max {
            self.max = new_value;
        }
        self.average_accum += new_value;
        self.count += 1;
    }
    ///Computes the average.
    pub fn get_average(&mut self) -> f32 {
        self.average_accum/(self.count as f32)
    }
}

///Decimator for a single device.
struct MeasurementDecimator {
    ///Voltage statistics.
    v_measurement: Option<MeasurementStatistics>,
    ///Frequency statistics.
    f_measurement: Option<MeasurementStatistics>,
    ///THD statistics.
    thd_measurement: Option<MeasurementStatistics>,
    ///Last time a bson document was generated.
    pub last_insert: DateTime<Utc>,
}


impl MeasurementDecimator {
    ///Created a new decimator.
    pub fn new() -> MeasurementDecimator {
        MeasurementDecimator {
            v_measurement: None,
            f_measurement: None,
            thd_measurement: None,
            last_insert: Utc::now(),
        }
    }

    ///Clears the buffers.
    fn clear(&mut self) {
        self.v_measurement = None;
        self.f_measurement = None;
        self.thd_measurement = None;
        self.last_insert = Utc::now();
    }

    ///Processes the next message.
    /// # Arguments:
    /// * `msg`- A new triggering message from a box with matching id.
    pub fn process_message(&mut self, msg: &TriggerMessage) {
        let rms = msg.get_rms();
        let f = msg.get_frequency();

        match self.v_measurement {
            None => self.v_measurement = Some(MeasurementStatistics::new(rms)),
            Some(ref mut v_m) => v_m.update(rms)
        }
        match self.f_measurement {
            None => { self.f_measurement = Some(MeasurementStatistics::new(f) ) }
            Some(ref mut f_m) => f_m.update(f)
        }

        if msg.has_thd() {
            let thd = msg.get_thd();
            match self.thd_measurement {
                None => { self.thd_measurement = Some(MeasurementStatistics::new(thd)) }
                Some(ref mut thd_m) => thd_m.update(thd)
            }
        }
    }

    ///Generates a bson document based on the values returned, clears the internal statistics, and resets the clock.
    pub fn generate_document_and_reset(&mut self) -> Document {
        let mut ret = Document::new();
        match self.v_measurement {
            None => {}
            Some(ref mut v_m) => {
                ret.insert(MONGO_LONG_TERM_MEASUREMENTS_VOLTAGE_FIELD,
                           doc! {
                                    MONGO_LONG_TERM_MEASUREMENTS_MIN_FIELD : v_m.min,
                                    MONGO_LONG_TERM_MEASUREMENTS_MAX_FIELD : v_m.max,
                                    MONGO_LONG_TERM_MEASUREMENTS_FILTERED_FIELD : v_m.get_average(),
                                },
                );
            }
        }

        match self.f_measurement {
            None => {}
            Some(ref mut f_m) => {
                ret.insert(MONGO_LONG_TERM_MEASUREMENTS_FREQUENCY_FIELD,
                           doc! {
                                    MONGO_LONG_TERM_MEASUREMENTS_MIN_FIELD : f_m.min,
                                    MONGO_LONG_TERM_MEASUREMENTS_MAX_FIELD : f_m.max,
                                    MONGO_LONG_TERM_MEASUREMENTS_FILTERED_FIELD : f_m.get_average(),
                                },
                );
            }
        }

        match self.thd_measurement {
            None => {}
            Some(ref mut thd_m) => {
                ret.insert(MONGO_LONG_TERM_MEASUREMENTS_THD_FIELD,
                           doc! {
                                    MONGO_LONG_TERM_MEASUREMENTS_MIN_FIELD : thd_m.min,
                                    MONGO_LONG_TERM_MEASUREMENTS_MAX_FIELD : thd_m.max,
                                    MONGO_LONG_TERM_MEASUREMENTS_FILTERED_FIELD : thd_m.get_average(),
                                },
                );
            }
        }

        self.clear();
        ret
    }
}

///This object is responsible for processing measurement messages.
pub struct MongoMeasurements {
    sub_chan: Subscription<Arc<TriggerMessage>>,
    live_coll: mongodb::coll::Collection,
    slow_coll: mongodb::coll::Collection,
    ///Mongo Expire time
    expire_time_sec: u64,
    ///Mongo Trends time
    trend_time_sec: u64
}

impl MongoMeasurements {

    ///Creates a new mongo measurement store.
    /// # Arguments
    /// * `client` -  a reference to a mongodb client instance.
    /// * `sub_chan` -  a channel for receiving triggering messages.
    pub fn new(client: &mongodb::Client, sub_chan: Subscription<Arc<TriggerMessage>>, settings : &Settings) -> MongoMeasurements {
        let ret = MongoMeasurements {
            sub_chan,
            live_coll: client.db(MONGO_DATABASE).collection(MONGO_MEASUREMENT_COLLECTION),
            slow_coll: client.db(MONGO_DATABASE).collection(MONGO_LONG_TERM_MEASUREMENT_COLLECTION),
            expire_time_sec : settings.mongo_measurement_expiration_seconds,
            trend_time_sec : settings.mongo_trends_update_interval_seconds
        };
        let mut index_opts = IndexOptions::new();
        index_opts.expire_after_seconds = Some(0);
        index_opts.background = Some(true);
        ret.live_coll.create_index(doc! {"expireAt" : 1}, Some(index_opts)).unwrap();
        ret
    }

    ///Generate a new bson document for the live measurements.
    /// # Arguments
    /// * `msg` a new trigger message to process.
    fn generate_document(&self, msg: &TriggerMessage) -> Document {
        let expire_time: DateTime<Utc> = Utc::now() + Duration::seconds(self.expire_time_sec as i64);
        let bson_expire_time = Bson::from(expire_time);


        let mut doc = doc! {
                MONGO_BOX_ID_FIELD : msg.get_id().to_string(),
                MONGO_TIMESTAMP_FIELD : msg.get_time() as u64,
                MONGO_MEASUREMENTS_VOLTAGE_FIELD : msg.get_rms() as f32,
                MONGO_MEASUREMENTS_FREQUENCY_FIELD : msg.get_frequency() as f32,
                MONGO_EXPIRE_FIELD : bson_expire_time
            };
        if msg.has_thd() {
            doc.insert(MONGO_MEASUREMENTS_THD_FIELD, msg.get_thd());
        }
        doc
    }

    ///The mongo store loop. Run this in a thread.
    pub fn run_loop(&self) {
        let mut map = HashMap::new();
        loop {
            let msg = self.sub_chan.recv().unwrap();
            let doc = self.generate_document(&msg);
            self.live_coll.insert_one(doc, None).ok().expect("Could not insert");
            let box_stat = map.entry(msg.get_id()).or_insert(MeasurementDecimator::new());
            box_stat.process_message(&msg);
            if box_stat.last_insert + Duration::seconds(self.trend_time_sec as i64) < Utc::now() {
                let mut doc = box_stat.generate_document_and_reset();
                doc.insert(MONGO_BOX_ID_FIELD, msg.get_id().to_string());
                doc.insert(MONGO_TIMESTAMP_FIELD, msg.get_time());
                self.slow_coll.insert_one(doc, None).ok().expect("Could not insert");
            }
        }
    }
}



