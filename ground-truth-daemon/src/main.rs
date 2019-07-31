use base64;
use reqwest::Client;
use reqwest::header;

pub mod config;

fn main() {
    match config::Config::load() {
        Ok(conf) => {
            let mut default_headers = header::HeaderMap::new();
            default_headers.insert(header::AUTHORIZATION, encode_user(&conf.api_user, &conf.api_pass).parse().unwrap());
            let client = Client::builder()
                .default_headers(default_headers)
                .build().unwrap();

            let url = format!("http://{}:{}/v1/filters", &conf.api_host, &conf.api_port);
            let res = client.get(&url).send().unwrap();
            println!("{:?}", res);
        },
        Err(err) => {
            println!("Error loading config: {}", err);
        },
    }
}

fn encode_user(user: &str, pass: &str) -> String {
    let fmt = format!("{}:{}", user, pass);
    base64::encode(&fmt)
}
