use reqwest::Client;

pub mod auth;
pub mod conf;
pub mod resources;
pub mod scrape;

fn main() {
    let config = conf::GroundTruthDaemonConfig::from_env().unwrap();
    let client = Client::builder().cookie_store(true).build().unwrap();

    let meters = resources::Meters::from_file("resources.json");

    let credentials = auth::post_login(&client, &config.username, &config.password).unwrap();

    scrape::scrape_data(
        &client,
        &credentials,
        "87891b60-1d7e-4fdf-964e-0cfaa4a9842e".to_string(),
        1566262840,
        1566263325,
    )
}
