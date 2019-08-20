use log;
use reqwest::Client;

pub mod auth;
pub mod conf;
pub mod resources;
pub mod scraper;

fn main() -> Result<(), String> {
    env_logger::init();
    log::info!("Starting ground_truth_daemon.");

    let config = conf::GroundTruthDaemonConfig::from_env()?;
    log::info!("Configuration loaded.");

    let meters = resources::Meters::from_file(&config.features_db)?;
    log::info!("Meters DB loaded.");

    let feature_ids = meters.feature_ids(&config.features);
    log::info!("Feature Ids loaded.");

    let client = Client::builder()
        .cookie_store(true)
        .build()
        .map_err(|e| format!("Error obtaining HTTP client: {:?}", e))?;

    log::info!("HTTP client constructed.");

    let credentials = auth::post_login(&client, &config.username, &config.password)?;

    log::info!("Acquired credentials.");

    log::info!("Beginning data scrape.");
    let end_ts_s = scraper::ts_s();
    let start_ts_s = end_ts_s - (config.collect_last_s as u64);
    for feature_id in feature_ids {
        match scraper::scrape_data(
            &client,
            &credentials,
            feature_id.clone(),
            start_ts_s,
            end_ts_s,
        ) {
            Ok(data) => {
                let graph: scraper::Graph = serde_json::from_str(&data).unwrap();
                for graph_point in graph.graph {
                    let data_point: scraper::DataPoint = graph_point.into();
                    println!("{:?}", data_point);
                }
            }
            Err(err) => log::error!("Error scraping data for feature_id={}: {}", feature_id, err),
        }
    }
    //    let scrape_res = scraper::scrape_data(
    //        &client,
    //        &credentials,
    //        "87891b60-1d7e-4fdf-964e-0cfaa4a9842e".to_string(),
    //        1566262840,
    //        1566263325,
    //    )?;
    //    println!("{}", scrape_res);

    log::info!("Finished data scrape.");

    log::info!("Exiting ground_truth_daemon.");

    Ok(())
}
