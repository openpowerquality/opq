extern crate bson;
extern crate mongodb;
extern crate chrono;
extern crate time;
extern crate pub_sub;

use std::collections::HashMap;

use mongodb::ThreadedClient;
use mongodb::db::ThreadedDatabase;
use mongodb::coll::options::IndexOptions;
use bson::*;
use bson::Document;

use chrono::prelude::*;
use time::Duration;

use constants::*;
use opq::*;

struct MeasurementStatistics {
    pub min: f32,
    pub max: f32,
    pub average_accum: f32,
    pub count: u32
}

impl MeasurementStatistics {
    pub fn new(new_value : f32) -> MeasurementStatistics{
        MeasurementStatistics{
            min: new_value,
            max: new_value,
            average_accum: new_value,
            count : 0
        }
    }

    pub fn update(&mut self, new_value: f32) {
        if new_value < self.min {
            self.min = new_value;
        } else if new_value > self.max {
            self.max = new_value;
        }
        self.average_accum += new_value;
        self.count += 1;
    }

    pub fn get_average(&mut self) -> f32 {
        self.average_accum/(self.count as f32)
    }
}

struct MeasurementDecimator {
    v_measurement: Option<MeasurementStatistics>,
    f_measurement: Option<MeasurementStatistics>,
    thd_measurement: Option<MeasurementStatistics>,
    pub last_insert: DateTime<Utc>,
}


impl MeasurementDecimator {
    pub fn new() -> MeasurementDecimator {
        MeasurementDecimator {
            v_measurement: None,
            f_measurement: None,
            thd_measurement: None,
            last_insert: Utc::now(),
        }
    }

    fn clear(&mut self) {
        self.v_measurement = None;
        self.f_measurement = None;
        self.thd_measurement = None;
        self.last_insert = Utc::now();
    }

    pub fn process_message(&mut self, msg: &TriggerMessage) {
        let rms = msg.get_rms();
        let f = msg.get_frequency();

        match self.v_measurement {
            None => self.v_measurement = Some(MeasurementStatistics::new(rms)),
            Some(ref mut v_m) => v_m.update(rms)
        }
        match self.f_measurement {
            None => { self.f_measurement = Some(MeasurementStatistics::new(rms) ) }
            Some(ref mut f_m) => f_m.update(f)
        }

        if msg.has_thd() {
            let thd = msg.get_thd();
            match self.thd_measurement {
                None => { self.thd_measurement = Some(MeasurementStatistics::new(rms)) }
                Some(ref mut thd_m) => thd_m.update(thd)
            }
        }
    }

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

pub struct MongoMeasurements {
    sub_chan: pub_sub::Subscription<TriggerMessage>,
    live_coll: mongodb::coll::Collection,
    slow_coll: mongodb::coll::Collection,
}

impl MongoMeasurements {
    pub fn new(client: &mongodb::Client, sub_chan: pub_sub::Subscription<TriggerMessage>) -> MongoMeasurements {
        let ret = MongoMeasurements {
            sub_chan: sub_chan,
            live_coll: client.db(MONGO_DATABASE).collection(MONGO_MEASUREMENT_COLLECTION),
            slow_coll: client.db(MONGO_DATABASE).collection(MONGO_LONG_TERM_MEASUREMENT_COLLECTION),
        };
        let mut index_opts = IndexOptions::new();
        index_opts.expire_after_seconds = Some(0);
        index_opts.background = Some(true);
        ret.live_coll.create_index(doc! {"expireAt" : 1}, Some(index_opts)).unwrap();
        ret
    }

    fn generate_document(msg: &TriggerMessage) -> Document {
        let expire_time: DateTime<Utc> = Utc::now() + Duration::seconds(MONGO_MEASUREMENTS_EXPIRE_TIME_SECONDS);
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

    pub fn run_loop(&self) {
        let mut map = HashMap::new();
        loop {
            let msg = self.sub_chan.recv().unwrap();
            let doc = MongoMeasurements::generate_document(&msg);
            self.live_coll.insert_one(doc, None).ok().expect("Could not insert");
            let box_stat = map.entry(msg.get_id()).or_insert(MeasurementDecimator::new());
            box_stat.process_message(&msg);
            if box_stat.last_insert + Duration::seconds(MONGO_LONG_TERM_MEASUREMENTS_UPDATE_INTERVAL) < Utc::now() {
                let mut doc = box_stat.generate_document_and_reset();
                doc.insert(MONGO_BOX_ID_FIELD, msg.get_id().to_string());
                doc.insert(MONGO_TIMESTAMP_FIELD, msg.get_time());
                self.slow_coll.insert_one(doc, None).ok().expect("Could not insert");
            }
        }
    }
}



