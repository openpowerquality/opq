use regex::Regex;
use reqwest::Client;
use scraper::{Html, Selector};
use serde::Serialize;

pub fn post_login(client: &Client, user: &str, pass: &str) -> Result<Credentials, String> {
    let mut res = client
        .post("https://energydata.hawaii.edu/Auth/Login")
        .form(&LoginForm::new(user.to_owned(), pass.to_owned()))
        .send()
        .map_err(|e| e.to_string())?;

    let body = res.text().map_err(|e| e.to_string())?;
    let clean_body = prepare_body(&body);
    extract_credentials(&clean_body)
}

#[derive(Serialize)]
struct LoginForm {
    #[serde(rename = "UserName")]
    pub username: String,
    #[serde(rename = "Password")]
    pub password: String,
}

impl LoginForm {
    pub fn new(username: String, password: String) -> LoginForm {
        LoginForm { username, password }
    }
}

fn prepare_body(body: &str) -> Vec<String> {
    let it = body
        .split("\r\n")
        .filter(|line| !line.is_empty())
        .map(|line| line.trim());

    let mut body_vec: Vec<String> = Vec::new();

    for line in it {
        body_vec.push(line.to_string());
    }

    body_vec
}

#[derive(Debug)]
pub struct Credentials {
    pub request_verification_token: String,
    pub connection_id: String,
    pub client_id: String,
    pub server_id: String,
    pub site_id: String,
}

fn extract_credentials(body: &Vec<String>) -> Result<Credentials, String> {
    let re = Regex::new(r"'([^' ]+)'").map_err(|e| e.to_string())?;
    let credentials = Credentials {
        request_verification_token: extract_request_verification_token(body)?,
        connection_id: re_extract(&re, body, "Avise.Config.UrlManager.url")?,
        client_id: re_extract(&re, body, "Avise.Config.UrlManager.SingleClientId")?,
        server_id: re_extract(&re, body, "Avise.Config.UrlManager.SingleServerId")?,
        site_id: "17abfe2a-3ae5-471b-965c-3e88e42f28d8".to_string(),
    };

    Ok(credentials)
}

fn extract_request_verification_token(body: &Vec<String>) -> Result<String, String> {
    match body
        .iter()
        .find(|line| line.contains("__RequestVerificationToken"))
    {
        None => Err("Error extracting request verification token.".to_owned()),
        Some(line) => {
            let fragment = Html::parse_fragment(&line);
            let selector = Selector::parse(r#"input[name="__RequestVerificationToken"]"#).unwrap();

            match fragment.select(&selector).next() {
                None => Err("Error extracting request verification token.".to_owned()),
                Some(input) => match input.value().attr("value") {
                    None => Err("Error extracting request verification token.".to_owned()),
                    Some(val) => Ok(val.to_owned()),
                },
            }
        }
    }
}

fn re_extract(re: &Regex, body: &Vec<String>, re_match: &str) -> Result<String, String> {
    match body.iter().find(|line| line.starts_with(re_match)) {
        None => Err(format!("Could not extract key {}", re_match)),
        Some(line) => match re.find(line) {
            None => Err(format!("Could not extract key {}", re_match)),
            Some(line) => Ok(line.as_str().replace("'", "")),
        },
    }
}
