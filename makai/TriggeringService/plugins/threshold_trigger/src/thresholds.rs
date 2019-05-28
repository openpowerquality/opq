use config::ThresholdTriggerPluginSettings;
use mongo::{MakaiConfig, Triggering, TriggeringOverride};
use mongodb::{Client, ThreadedClient};
use std::collections::HashMap;
use {datetime, mongo};

const ONE_MIN_IN_MS: u64 = 60000;

#[inline]
fn minus_percent(reference: f64, percent: f64) -> f64 {
    let as_percent = percent / 100.0;
    let delta = reference * as_percent;
    reference - delta
}

#[inline]
fn plus_percent(reference: f64, percent: f64) -> f64 {
    let as_percent = percent / 100.0;
    let delta = reference * as_percent;
    reference + delta
}

#[derive(Clone, Debug)]
pub struct Threshold {
    pub threshold_f_low: f64,
    pub threshold_f_high: f64,
    pub threshold_v_low: f64,
    pub threshold_v_high: f64,
    pub threshold_thd_high: f64,
}

impl From<TriggeringOverride> for Threshold {
    fn from(triggering_override: TriggeringOverride) -> Self {
        Threshold {
            threshold_f_low: minus_percent(
                triggering_override.ref_f,
                triggering_override.threshold_percent_f_low,
            ),
            threshold_f_high: plus_percent(
                triggering_override.ref_f,
                triggering_override.threshold_percent_f_high,
            ),
            threshold_v_low: minus_percent(
                triggering_override.ref_v,
                triggering_override.threshold_percent_v_low,
            ),
            threshold_v_high: plus_percent(
                triggering_override.ref_v,
                triggering_override.threshold_percent_v_high,
            ),
            threshold_thd_high: triggering_override.threshold_percent_thd_high,
        }
    }
}

impl From<Triggering> for Threshold {
    fn from(triggering: Triggering) -> Self {
        Threshold {
            threshold_f_low: minus_percent(
                triggering.default_ref_f,
                triggering.default_threshold_percent_f_low,
            ),
            threshold_f_high: plus_percent(
                triggering.default_ref_f,
                triggering.default_threshold_percent_f_high,
            ),
            threshold_v_low: minus_percent(
                triggering.default_ref_v,
                triggering.default_threshold_percent_v_low,
            ),
            threshold_v_high: plus_percent(
                triggering.default_ref_v,
                triggering.default_threshold_percent_v_high,
            ),
            threshold_thd_high: triggering.default_threshold_percent_thd_high,
        }
    }
}

#[derive(Debug, Default)]
pub struct CachedThresholdProvider {
    pub threshold_cache: HashMap<String, Threshold>,
    pub default_threshold: Option<Threshold>,
    pub last_update: u64,
    pub settings: ThresholdTriggerPluginSettings,
    pub makai_config: MakaiConfig,
    pub mongo_client: Option<Client>,
}

impl CachedThresholdProvider {
    pub fn new(settings: ThresholdTriggerPluginSettings) -> CachedThresholdProvider {
        let client: Client = Client::connect(&settings.mongo_host, settings.mongo_port).unwrap();
        let makai_config = mongo::makai_config(&client).unwrap();
        CachedThresholdProvider {
            threshold_cache: HashMap::new(),
            default_threshold: None,
            last_update: datetime::timestamp_ms(),
            settings,
            makai_config,
            mongo_client: Some(client),
        }
    }

    pub fn update(&mut self) {
        let makai_config = self.mongo_client.as_ref().unwrap();
        self.makai_config = mongo::makai_config(makai_config).unwrap();
        self.default_threshold = Some(self.makai_config.triggering.clone().into());
        for triggering_override in &self.makai_config.triggering.triggering_overrides {
            self.threshold_cache.insert(
                triggering_override.box_id.to_string(),
                triggering_override.clone().into(),
            );
        }
        self.last_update = datetime::timestamp_ms();
    }

    pub fn get(&mut self, box_id: &str) -> Threshold {
        let now = datetime::timestamp_ms();
        if now - self.last_update > ONE_MIN_IN_MS {
            self.update();
        }
        match self.threshold_cache.get(box_id) {
            None => self.default_threshold.clone().unwrap(),
            Some(threshold) => threshold.clone(),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn mock_plugin_settings() -> ThresholdTriggerPluginSettings {
        unimplemented!()
    }

    fn mock_makai_config() -> MakaiConfig {
        unimplemented!()
    }

    #[test]
    fn test_plus_percent() {
        assert_eq!(plus_percent(120.0, 10.0), 132.0)
    }

    #[test]
    fn test_minus_percent() {
        assert_eq!(minus_percent(120.0, 10.0), 108.0)
    }

    #[test]
    fn test_threshold_from_triggering_override() {
        let triggering_override = TriggeringOverride {
            box_id: "test".to_string(),
            ref_f: 60.0,
            ref_v: 120.0,
            threshold_percent_f_low: 1.0,
            threshold_percent_f_high: 1.0,
            threshold_percent_v_low: 5.0,
            threshold_percent_v_high: 5.0,
            threshold_percent_thd_high: 5.0,
        };

        let threshold: Threshold = triggering_override.into();
        assert_eq!(threshold.threshold_f_low, 59.4);
        assert_eq!(threshold.threshold_f_high, 60.6);
        assert_eq!(threshold.threshold_v_low, 114.0);
        assert_eq!(threshold.threshold_v_high, 126.0);
        assert_eq!(threshold.threshold_thd_high, 5.0);
    }

    #[test]
    fn test_threshold_from_triggering() {
        let triggering = Triggering {
            default_ref_f: 60.0,
            default_ref_v: 120.0,
            default_threshold_percent_f_low: 1.0,
            default_threshold_percent_f_high: 1.0,
            default_threshold_percent_v_low: 5.0,
            default_threshold_percent_v_high: 5.0,
            default_threshold_percent_thd_high: 5.0,
            triggering_overrides: vec![],
        };

        let threshold: Threshold = triggering.into();
        assert_eq!(threshold.threshold_f_low, 59.4);
        assert_eq!(threshold.threshold_f_high, 60.6);
        assert_eq!(threshold.threshold_v_low, 114.0);
        assert_eq!(threshold.threshold_v_high, 126.0);
        assert_eq!(threshold.threshold_thd_high, 5.0);
    }

}
