use log;
use reqwest::Client;

pub mod auth;
pub mod conf;
pub mod mongo;
pub mod resources;
pub mod scraper;

fn main() -> Result<(), String> {
    env_logger::init();
    log::info!("Starting ground_truth_daemon.");

    let config = conf::GroundTruthDaemonConfig::from_env()?;
    log::info!("Configuration loaded:\n{:?}", &config);

    let meters = resources::Meters::from_file(&config.features_db)?;
    log::info!("Meters DB loaded.");

    //    let feature_ids = meters.feature_ids(&config.features);
    //    log::info!("{} feature ids loaded.", feature_ids.len());

    let (_mongo_client, ground_truth_coll) = mongo::init(&config)?;
    log::info!("MongoClient loaded.");

    let client = Client::builder()
        .cookie_store(true)
        .build()
        .map_err(|e| format!("Error obtaining HTTP client: {:?}", e))?;
    log::info!("HTTP client loaded.");

    let credentials = auth::post_login(&client, &config.username, &config.password)?;
    log::info!("Acquired credentials.");

    log::info!("Beginning data scrape.");
    for feature in &config.features {
        let feature_ids = meters.feature_ids(feature);

        let end_ts_s = scraper::ts_s();
        let start_ts_s = end_ts_s - (config.collect_last_s as u64);
        log::info!(
            "Scraping data for feature={} feature_ids={:?}",
            feature,
            &feature_ids
        );
        match scraper::scrape_data(&client, &credentials, feature_ids, start_ts_s, end_ts_s) {
            Ok(data) => {
                let graph: scraper::Graph = serde_json::from_str(&data).unwrap();
                let data_points: Vec<scraper::DataPoint> = graph.into();

                if let Err(e) = mongo::store_data_points(&ground_truth_coll, &data_points) {
                    log::error!("Error storing data}: {}", e);
                }
            }
            Err(err) => log::error!("Error scraping data: {}", err),
        }
    }

    log::info!("Finished data scrape.");

    log::info!("Exiting ground_truth_daemon.");

    Ok(())
}
