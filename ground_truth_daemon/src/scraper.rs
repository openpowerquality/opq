use crate::auth::Credentials;
use reqwest::Client;

use chrono;
use chrono::{Datelike, TimeZone, Timelike};
use serde::{Deserialize, Serialize};
use std::thread::sleep;
use std::time::Duration;
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
        feature_ids: Vec<String>,
    ) -> ScrapeRequestParams {
        let feature_ids: Vec<String> = feature_ids
            .iter()
            .map(|fid| format!("BLUEPILLAR|{}", fid))
            .collect();
        ScrapeRequestParams {
            connection_id,
            stored_proc_name: "GetLogMinuteDataForTagIds".to_string(),
            rollup_name: "Mean".to_string(),
            table_index: "1".to_string(),
            parameter1: format_time(start_ts_s),
            parameter2: format_time(end_ts_s),
            parameter3: "|-600".to_string(),
            parameter4: "|client".to_string(),
            parameter5: feature_ids.join(","),
            underscore: (ts_s() * 1000).to_string(),
        }
    }
}

pub fn scrape_data(
    client: &Client,
    credentials: &Credentials,
    feature_ids: Vec<String>,
    start_ts_s: u64,
    end_ts_s: u64,
    tries: usize,
) -> Result<String, String> {
    if tries == 0 {
        let warn = format!("Max tries exceeded for {:?}", &feature_ids);
        log::warn!("{}", warn);
        return Err(warn);
    }

    log::debug!("tries={}", tries);

    let req = ScrapeRequestParams::new(
        credentials.connection_id.clone(),
        start_ts_s,
        end_ts_s,
        feature_ids.clone(),
    );
    let mut res = client.get("https://energydata.hawaii.edu/api/reports/GetAnalyticsGraphAndGridData/GetAnalyticsGraphAndGridData")
        .header("__RequestVerificationToken", credentials.request_verification_token.clone())
        .header("Connection-Timeout", "10000")
        .header("Socket-Timeout", "10000")
        .query(&req)
        .send()
        .map_err(|e| format!("Error sending data scrape req to server: {:?}", e))?;

    log::debug!(
        "Data scrape response : \n{:?}\n{:?}\n",
        &res.headers(),
        &res.status(),
    );

    if !res.status().is_success() {
        return Err(format!(
            "Response code for data scrape is not OK: {:?}",
            res.status()
        ));
    }

    match res.text() {
        Ok(txt) => {
            log::debug!("Data scrape response text: \n{}\n", &txt.len());
            Ok(txt)
        }
        Err(err) => {
            log::warn!("Error getting body from data scrape response: {:?}", err);
            sleep(Duration::from_secs(1));
            scrape_data(
                client,
                credentials,
                feature_ids,
                start_ts_s,
                end_ts_s,
                tries - 1,
            )
        }
    }
}

#[inline]
pub fn ts_s() -> u64 {
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

#[derive(Deserialize, Debug)]
pub struct Graph {
    #[serde(rename = "Graph")]
    pub graph: Vec<GraphPoint>,
}

#[derive(Deserialize, Debug)]
pub struct GraphPoint {
    #[serde(rename = "Endpoint")]
    pub endpoint: String,
    #[serde(rename = "DataType")]
    pub data_type: String,
    #[serde(rename = "EntityId")]
    pub entity_id: String,
    #[serde(rename = "EntityName")]
    pub entity_name: String,
    #[serde(rename = "TagId")]
    pub tag_id: String,
    #[serde(rename = "TagName")]
    pub tag_name: String,
    #[serde(rename = "TagLogId")]
    pub tag_log_id: i64,
    #[serde(rename = "Mean")]
    pub mean: f64,
    #[serde(rename = "Min")]
    pub min: f64,
    #[serde(rename = "Max")]
    pub max: f64,
    #[serde(rename = "Median")]
    pub median: f64,
    #[serde(rename = "Actual")]
    pub actual: f64,
    #[serde(rename = "StDev")]
    pub std_dev: f64,
    #[serde(rename = "SampleSize")]
    pub sample_size: i64,
    #[serde(rename = "Quality")]
    pub quality: i64,
    #[serde(rename = "FullDateTimeUTC")]
    pub full_date_time_utc: String,
    #[serde(rename = "FullDateTimeServer")]
    pub full_date_time_server: String,
    #[serde(rename = "FullDateTimeClient")]
    pub full_date_time_client: String,
    #[serde(rename = "DeviceId")]
    pub device_id: String,
    #[serde(rename = "DeviceName")]
    pub device_name: String,
    #[serde(rename = "FullDateTime")]
    pub full_date_time: String,
}

#[derive(Deserialize, Serialize, Debug)]
pub struct DataPoint {
    //#[serde(rename = "_id")]
    //pub id: bson::oid::ObjectId,
    #[serde(rename = "meter-name")]
    pub meter_name: String,
    #[serde(rename = "sample-type")]
    pub sample_type: String,
    #[serde(rename = "ts-s")]
    pub ts_s: i32,
    pub actual: f64,
    pub min: f64,
    pub max: f64,
    pub avg: f64,
    pub stddev: f64,
}

impl From<GraphPoint> for DataPoint {
    fn from(graph_point: GraphPoint) -> Self {
        DataPoint {
            //id: bson::oid::ObjectId::new().unwrap(),
            meter_name: graph_point.entity_name,
            sample_type: graph_point.tag_name,
            ts_s: to_ts(&graph_point.full_date_time_utc) as i32,
            actual: graph_point.actual,
            min: graph_point.min,
            max: graph_point.max,
            avg: graph_point.mean,
            stddev: graph_point.std_dev,
        }
    }
}

impl From<Graph> for Vec<DataPoint> {
    fn from(graph: Graph) -> Self {
        let mut data_points: Vec<DataPoint> = Vec::new();
        for graph_point in graph.graph {
            let data_point: DataPoint = graph_point.into();
            data_points.push(data_point);
        }
        data_points
    }
}

fn to_ts(dt: &str) -> i64 {
    chrono::NaiveDateTime::parse_from_str(dt, "%Y-%m-%dT%H:%M:%S")
        .unwrap()
        .timestamp()
}
