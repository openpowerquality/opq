use config::ThresholdTriggerPluginSettings;
use mongodb;
use mongodb::db::ThreadedDatabase;
use mongodb::{Document, ThreadedClient};

const OPQ_DB: &str = "opq";
const MAKAI_CONFIG_COLLECTION: &str = "makai_config";

#[derive(Debug, Serialize, Deserialize, Default)]
pub struct MakaiConfig {
    pub triggering: Triggering,
}

#[derive(Debug, Serialize, Deserialize, Clone, Default)]
pub struct Triggering {
    pub default_ref_f: f64,
    pub default_ref_v: f64,
    pub default_threshold_percent_f_low: f64,
    pub default_threshold_percent_f_high: f64,
    pub default_threshold_percent_v_low: f64,
    pub default_threshold_percent_v_high: f64,
    pub default_threshold_percent_thd_high: f64,
    pub triggering_overrides: Vec<TriggeringOverride>,
}

#[derive(Debug, Serialize, Deserialize, Clone, Default)]
pub struct TriggeringOverride {
    pub box_id: String,
    pub ref_f: f64,
    pub ref_v: f64,
    pub threshold_percent_f_low: f64,
    pub threshold_percent_f_high: f64,
    pub threshold_percent_v_low: f64,
    pub threshold_percent_v_high: f64,
    pub threshold_percent_thd_high: f64,
}

pub fn makai_config(settings: &ThresholdTriggerPluginSettings) -> Result<MakaiConfig, String> {
    println!("makai_config {:?}", settings);
    let client = mongodb::Client::connect(&settings.mongo_host, settings.mongo_port)
        .expect("Could not create mongo client");
    let db: mongodb::db::Database = client.db(OPQ_DB);

    let coll: mongodb::coll::Collection = db.collection(MAKAI_CONFIG_COLLECTION);
    let makai_config_doc: Option<Document> = coll.find_one(None, None).unwrap_or(None);

    match makai_config_doc {
        None => Err("Could not retrieve makai_config.".to_string()),
        Some(doc) => match bson::to_bson(&doc) {
            Ok(bson) => match bson::from_bson::<MakaiConfig>(bson) {
                Ok(makai_config) => Ok(makai_config),
                Err(err) => Err(err.to_string()),
            },
            Err(err) => Err(err.to_string()),
        },
    }
}
