use crate::auth::Credentials;
use reqwest::{Client, StatusCode};

use chrono;
use chrono::{Datelike, TimeZone, Timelike};
use serde::Serialize;
use std::time::{SystemTime, UNIX_EPOCH};

#[derive(Serialize)]
struct ScrapeRequestParams {
    #[serde(rename = "connectionId")]
    pub connection_id: String,
    #[serde(rename = "storedProcName")]
    pub stored_proc_name: String,
    #[serde(rename = "rollupName")]
    pub rollup_name: String,
    #[serde(rename = "tableIndex")]
    pub table_index: String,
    pub parameter1: String,
    pub parameter2: String,
    pub parameter3: String,
    pub parameter4: String,
    pub parameter5: String,
    #[serde(rename = "_")]
    pub underscore: String,
}

impl ScrapeRequestParams {
    pub fn new(
        connection_id: String,
        start_ts_s: u64,
        end_ts_s: u64,
        feature_id: String,
    ) -> ScrapeRequestParams {
        ScrapeRequestParams {
            connection_id,
            stored_proc_name: "GetLogMinuteDataForTagIds".to_string(),
            rollup_name: "Mean".to_string(),
            table_index: "1".to_string(),
            parameter1: format_time(start_ts_s),
            parameter2: format_time(end_ts_s),
            parameter3: "|-600".to_string(),
            parameter4: "|client".to_string(),
            parameter5: format!("BLUEPILLAR|{}", feature_id),
            underscore: (ts_s() * 1000).to_string(),
        }
    }
}

pub fn scrape_data(
    client: &Client,
    credentials: &Credentials,
    resource_id: String,
    start_ts_s: u64,
    end_ts_s: u64,
) -> Result<String, String> {
    let req = ScrapeRequestParams::new(
        credentials.connection_id.clone(),
        start_ts_s,
        end_ts_s,
        resource_id,
    );
    let mut res = client.get("https://energydata.hawaii.edu/api/reports/GetAnalyticsGraphAndGridData/GetAnalyticsGraphAndGridData")
        .header("__RequestVerificationToken", credentials.request_verification_token.clone())
        .query(&req)
        .send()
        .map_err(|e| format!("Error sending data scrape req to server: {:?}", e))?;

    if !res.status().is_success() {
        return Err(format!(
            "Response code for data scrape is not OK: {:?}",
            res.status()
        ));
    }

    match res.text() {
        Ok(txt) => Ok(txt),
        Err(err) => Err(format!(
            "Error getting body from data scrape response: {:?}",
            err
        )),
    }
}

#[inline]
fn ts_s() -> u64 {
    let start = SystemTime::now();
    let since_the_epoch = start
        .duration_since(UNIX_EPOCH)
        .expect("Time went backwards");
    since_the_epoch.as_secs()
}

#[inline]
fn format_time(ts_s: u64) -> String {
    let dt: chrono::DateTime<chrono::Local> = chrono::Local.timestamp(ts_s as i64, 0);
    let month = dt.month();
    let day = dt.day();
    let year = dt.year();
    let (is_pm, hour12) = dt.hour12();
    let min = dt.minute();
    let am_pm = if is_pm { "PM" } else { "AM" };
    format!(
        "|{}/{}/{} {}:{:02} {}",
        month, day, year, hour12, min, am_pm
    )
}
