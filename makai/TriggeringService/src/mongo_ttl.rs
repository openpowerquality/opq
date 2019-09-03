use std::time::{SystemTime, UNIX_EPOCH};

use crate::constants::*;

use mongodb;
use mongodb::db::ThreadedDatabase;
use mongodb::Client;
use mongodb::ThreadedClient;

#[inline]
pub fn timestamp_s() -> u64 {
    let now = SystemTime::now();
    let since_epoch = now.duration_since(UNIX_EPOCH).expect("Time is hard");
    since_epoch.as_secs()
}

struct CachedTtlValue {
    ttl: u64,
    expire_at: u64,
}

impl CachedTtlValue {
    fn from(ttl: u64, expire_at: u64) -> CachedTtlValue {
        CachedTtlValue { ttl, expire_at }
    }
}

pub struct CachedTtlProvider {
    cache_for_seconds: u64,
    cached_measurements_ttl: Option<CachedTtlValue>,
    cached_trends_ttl: Option<CachedTtlValue>,
    cached_events_ttl: Option<CachedTtlValue>,
    laha_config_coll: mongodb::coll::Collection,
}

impl CachedTtlProvider {
    pub fn new(cache_for_seconds: u64, mongo_client: &Client) -> CachedTtlProvider {
        CachedTtlProvider {
            cache_for_seconds,
            cached_measurements_ttl: None,
            cached_trends_ttl: None,
            cached_events_ttl: None,
            laha_config_coll: mongo_client
                .db(MONGO_DATABASE)
                .collection(MONGO_LAHA_CONFIG_COLLECTION),
        }
    }

    fn cache_get(&self, cached_ttl_value: &Option<CachedTtlValue>) -> Option<u64> {
        match cached_ttl_value {
            Some(cached_ttl_value) => {
                if cached_ttl_value.expire_at > timestamp_s() {
                    Some(cached_ttl_value.ttl)
                } else {
                    None
                }
            }
            None => None,
        }
    }

    fn mongo_get_ttl(&self, ttl_key: &str) -> u64 {
        let laha_config_option = self
            .laha_config_coll
            .find_one(None, None)
            .expect("Error getting laha_config");
        let laha_config = laha_config_option.expect("laha_config is blank");
        let ordered_doc = laha_config
            .get_document(MONGO_LAHA_CONFIG_TTLS)
            .expect("Error getting ordered_doc");
        let ttl = ordered_doc.get_i32(ttl_key).expect("Error getting ttl");
        ttl as u64
    }

    pub fn get_measurements_ttl(&mut self) -> u64 {
        let ts = timestamp_s();
        match self.cache_get(&self.cached_measurements_ttl) {
            Some(cached_value) => ts + cached_value,
            None => {
                let ttl = self.mongo_get_ttl(MONGO_LAHA_CONFIG_MEASUREMENTS_TTL);
                self.cached_measurements_ttl =
                    Some(CachedTtlValue::from(ttl, ts + self.cache_for_seconds));
                ts + ttl
            }
        }
    }

    pub fn get_trends_ttl(&mut self) -> u64 {
        let ts = timestamp_s();
        match self.cache_get(&self.cached_trends_ttl) {
            Some(cached_value) => ts + cached_value,
            None => {
                let ttl = self.mongo_get_ttl(MONGO_LAHA_CONFIG_TRENDS_TTL);
                self.cached_trends_ttl =
                    Some(CachedTtlValue::from(ttl, ts + self.cache_for_seconds));
                ts + ttl
            }
        }
    }

    pub fn get_events_ttl(&mut self) -> u64 {
        let ts = timestamp_s();
        match self.cache_get(&self.cached_events_ttl) {
            Some(cached_value) => ts + cached_value,
            None => {
                let ttl = self.mongo_get_ttl(MONGO_LAHA_CONFIG_EVENTS_TTL);
                self.cached_events_ttl =
                    Some(CachedTtlValue::from(ttl, ts + self.cache_for_seconds));
                ts + ttl
            }
        }
    }
}
