use log;
use reqwest::Client;
use std::thread::sleep;
use std::time::Duration;

pub mod auth;
pub mod conf;

pub mod resources;
pub mod scraper;
mod storage_server;

fn main() -> Result<(), String> {
    env_logger::init();
    log::info!("Starting ground_truth_daemon.");

    let config = conf::GroundTruthDaemonConfig::from_env()?;
    log::info!("Configuration loaded:\n{:?}", &config);

    let meters = resources::Meters::from_file(&config.features_db)?;
    log::info!("Meters DB loaded.");

    //    let feature_ids = meters.feature_ids(&config.features);
    //    log::info!("{} feature ids loaded.", feature_ids.len());

    log::info!("MongoClient loaded.");

    let client = Client::builder()
        .cookie_store(true)
        .build()
        .map_err(|e| format!("Error obtaining HTTP client: {:?}", e))?;
    log::info!("HTTP client loaded.");

    let credentials = auth::post_login(&client, &config.username, &config.password)?;
    log::info!("Acquired credentials.");
    let mut storage_service = crate::storage_server::StorageService::new(config.path.clone());
    log::info!("Beginning data scrape.");
    let total_features = config.features.len();
    let mut feature_cnt: usize = 1;
    for feature in &config.features {
        let feature_ids = meters.feature_ids(feature);
        let total_feature_ids = feature_ids.len();
        let mut feature_id_cnt: usize = 1;
        for feature_id in feature_ids {
            log::debug!(
                "feature {}/{} sensor {}/{}",
                feature_cnt,
                total_features,
                feature_id_cnt,
                total_feature_ids
            );
            sleep(Duration::from_secs(1));
            let end_ts_s = if config.is_ranged() {
                config.end_range_s()
            } else {
                scraper::ts_s()
            };

            let start_ts_s = if config.is_ranged() {
                config.start_range_s()
            } else {
                end_ts_s - (config.collect_last_s as u64)
            };

            log::info!(
                "Scraping data for feature={} feature_ids={:?}",
                feature,
                &feature_id
            );
            match scraper::scrape_data(
                &client,
                &credentials,
                vec![feature_id],
                start_ts_s,
                end_ts_s,
            ) {
                Ok(data) => {
                    let maybe_graph: Result<scraper::Graph, serde_json::error::Error> =
                        serde_json::from_str(&data);

                    match maybe_graph {
                        Ok(graph) => {
                            let data_points: Vec<scraper::DataPoint> = graph.into();
                            storage_service.store_datapoint(data_points);
                        }
                        Err(err) => log::error!("Could not parse data from {}: {:?}", data, err),
                    }
                }
                Err(err) => log::error!("Error scraping data: {}", err),
            }
            feature_id_cnt += 1;
        }
        feature_cnt += 1;
    }

    log::info!("Finished data scrape.");

    log::info!("Exiting ground_truth_daemon.");

    Ok(())
}
