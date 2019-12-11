use serde::Deserialize;
use serde_json;
use std::collections::HashSet;
use std::iter::FromIterator;

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

        let whitelist: Vec<&str> = vec![
            "POST_MAIN_1",
            "POST_MAIN_2",
            "HAMILTON_LIB_PH_III_CH_1_MTR",
            "HAMILTON_LIB_PH_III_CH_2_MTR",
            "HAMILTON_LIB_PH_III_CH_3_MTR",
            "HAMILTON_LIB_PH_III_MAIN_1_MTR",
            "HAMILTON_LIB_PH_III_MAIN_2_MTR",
            "HAMILTON_LIB_PH_III_MCC_AC1_MTR",
            "HAMILTON_LIB_PH_III_MCC_AC2_MTR",
            "KELLER_HALL_MAIN_MTR",
            "MARINE_SCIENCE_MAIN_A_MTR",
            "MARINE_SCIENCE_MAIN_B_MTR",
            "MARINE_SCIENCE_MCC_MTR",
            "AG_ENGINEERING_MAIN_MTR",
            "AG_ENGINEERING_MCC_MTR",
            "LAW_LIB_MAIN_MTR",
            "KENNEDY_THEATRE_MAIN_MTR",
        ];

        let whitelist: HashSet<&str> = HashSet::from_iter(whitelist.iter().cloned());

        let whitelisted_meters: Vec<&Meter> = self
            .meters
            .iter()
            .filter(|meter| whitelist.contains(&meter.meter_name[..]))
            .collect();

        for meter in whitelisted_meters {
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
