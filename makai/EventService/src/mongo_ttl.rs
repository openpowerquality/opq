use std::time::{SystemTime, UNIX_EPOCH};

use crate::constants::*;

use mongodb;
use mongodb::db::ThreadedDatabase;
use mongodb::Client;
use mongodb::ThreadedClient;

#[inline]
fn timestamp_s() -> u64 {
    let now = SystemTime::now();
    let since_epoch = now.duration_since(UNIX_EPOCH).expect("Time is hard");
    return since_epoch.as_secs();
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
    cached_events_ttl: Option<CachedTtlValue>,
    laha_config_coll: mongodb::coll::Collection,
}

impl CachedTtlProvider {
    pub fn new(cache_for_seconds: u64, mongo_client: &Client) -> CachedTtlProvider {
        CachedTtlProvider {
            cache_for_seconds,
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
        let ordered_doc = laha_config.get_document(MONGO_LAHA_CONFIG_TTLS).unwrap();
        let ttl = ordered_doc.get_f64(ttl_key).unwrap();
        return ttl as u64;
    }


    pub fn get_events_ttl(&mut self) -> u64 {
        match self.cache_get(&self.cached_events_ttl) {
            Some(cached_value) => cached_value,
            None => {
                let ttl = self.mongo_get_ttl(MONGO_LAHA_CONFIG_EVENTS_TTL);
                let expire_at = timestamp_s() + self.cache_for_seconds;
                self.cached_events_ttl = Some(CachedTtlValue::from(ttl, expire_at));
                expire_at
            }
        }
    }
}
