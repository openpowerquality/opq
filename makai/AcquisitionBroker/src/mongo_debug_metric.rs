use crate::config;
use crate::constants::*;
use mongodb::db::ThreadedDatabase;
use mongodb::ThreadedClient;

pub struct MongoStorageService {
    coll: mongodb::coll::Collection,
}

impl MongoStorageService {
    pub fn new(settings: &config::Settings) -> MongoStorageService {
        let client = mongodb::Client::connect(&settings.mongo_host, settings.mongo_port).unwrap();
        MongoStorageService {
            coll: client.db(MONGO_DATABASE).collection(MAKAI_METRIC_DATABASE),
        }
    }
    pub fn store_metric_in_db(&self, sent: u32, recv: u32) {
        let doc = doc! {
            MAKAI_METRIC_HANDLE_FIELD : MAKAI_METRIC_HANDLE,
            MAKAI_METRIC_SENT_FIELD : sent,
            MAKAI_METRIC_RECV_FIELD : recv
        };
        self.coll.insert_one(doc, None).unwrap();
    }
}
