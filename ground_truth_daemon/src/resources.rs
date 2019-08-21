use serde::Deserialize;
use serde_json;

#[derive(Deserialize, Debug)]
pub struct Meters {
    pub meters: Vec<Meter>,
}

impl Meters {
    pub fn from_file(path: &str) -> Result<Meters, String> {
        let file = std::fs::File::open(path)
            .map_err(|e| format!("Error loading meters from file {}: {:?}", path, e))?;
        serde_json::from_reader(file)
            .map_err(|e| format!("Error parsing meters from file {}: {:?}", path, e))
    }

    pub fn feature_ids(&self, feature_str: &String) -> Vec<String> {
        let mut resource_ids: Vec<String> = Vec::new();
        for meter in &self.meters {
            for feature in &meter.features {
                if feature.name == *feature_str {
                    resource_ids.push(feature.tag_id.clone());
                }
            }
        }
        resource_ids
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
