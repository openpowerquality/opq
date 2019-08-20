use log;
use reqwest::Client;

pub mod auth;
pub mod conf;
pub mod resources;
pub mod scrape;

fn main() -> Result<(), String> {
    env_logger::init();
    log::info!("Starting ground_truth_daemon.");

    let config = conf::GroundTruthDaemonConfig::from_env()?;
    log::info!("Configuration loaded.");

    let meters = resources::Meters::from_file(&config.features_db)?;
    log::info!("Meters DB loaded.");

    let client = Client::builder()
        .cookie_store(true)
        .build()
        .map_err(|e| format!("Error obtaining HTTP client: {:?}", e))?;

    log::info!("HTTP client constructed.");

    let credentials = auth::post_login(&client, &config.username, &config.password)?;

    log::info!("Acquired credentials.");

    let scrape_res = scrape::scrape_data(
        &client,
        &credentials,
        "87891b60-1d7e-4fdf-964e-0cfaa4a9842e".to_string(),
        1566262840,
        1566263325,
    )?;

    log::info!("Exiting ground_truth_daemon.");

    Ok(())
}
