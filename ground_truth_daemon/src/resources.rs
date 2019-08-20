use serde::Deserialize;
use serde_json;

#[derive(Deserialize, Debug)]
pub struct Meters {
    pub meters: Vec<Meter>,
}

impl Meters {
    pub fn from_file(path: &str) -> Meters {
        let file = std::fs::File::open(path).unwrap();
        return serde_json::from_reader(file).unwrap();
    }
}

#[derive(Deserialize, Debug)]
pub struct Meter {
    pub meter_name: String,
    pub features: Vec<Feature>,
}

#[derive(Deserialize, Debug)]
pub struct Feature {
    #[serde(rename = "uselookupvalue")]
    pub use_lookup_value: String,
    #[serde(rename = "lookupValues")]
    pub lookup_values: Option<String>,
    #[serde(rename = "Name")]
    pub name: String,
    #[serde(rename = "tagID")]
    pub tag_id: String,
    pub r#type: String,
    pub writable: bool,
    pub lo: String,
    pub hi: String,
}
