use mongodb::ThreadedClient;
use mongodb::db::ThreadedDatabase;
use mongodb::coll::options::FindOptions;
use bson::*;

static MONGO_DATABASE: &str = "opq";
static MONGO_BOXES_COLLECTION: &str = "opq_boxes";
static MONGO_OPQ_BOXES_BOX_ID_FIELD: &str = "box_id";

use crate::config::Settings;

pub fn get_box_list(settings : &Settings) -> Vec<u32>{
    let mut ret = vec!();
    let client =  mongodb::Client::connect(&settings.mongo_host, settings.mongo_port).unwrap();
    let col = client.db(MONGO_DATABASE).collection(MONGO_BOXES_COLLECTION);
    let filter = doc!{
            MONGO_OPQ_BOXES_BOX_ID_FIELD : 1,
        };
    let mut opt = FindOptions::new();
    opt.projection = Some(filter);
    let cursor = col.find(None, Some(opt)).unwrap();
    for result in cursor {
        if let Ok(item) = result {
            if let Some(&Bson::String(ref id)) = item.get(MONGO_OPQ_BOXES_BOX_ID_FIELD) {
                ret.push(id.parse().unwrap());
            }
        }
    }
    ret
}