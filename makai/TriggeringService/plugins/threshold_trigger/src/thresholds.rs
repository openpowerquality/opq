use config::ThresholdTriggerPluginSettings;
use mongo;
use mongo::{MakaiConfig, Triggering, TriggeringOverride};
use std::collections::HashMap;
use std::time::{SystemTime, UNIX_EPOCH};

#[inline]
fn timestamp_ms() -> u64 {
    let start = SystemTime::now();
    let since_the_epoch = start
        .duration_since(UNIX_EPOCH)
        .expect("Time went backwards");
    since_the_epoch.as_millis() as u64
}

#[derive(Clone, Debug)]
pub struct Threshold {
    pub ref_f: f64,
    pub ref_v: f64,
    pub threshold_percent_f_low: f64,
    pub threshold_percent_f_high: f64,
    pub threshold_percent_v_low: f64,
    pub threshold_percent_v_high: f64,
    pub threshold_percent_thd_high: f64,
}

impl From<TriggeringOverride> for Threshold {
    fn from(triggering_override: TriggeringOverride) -> Self {
        Threshold {
            ref_f: triggering_override.ref_f,
            ref_v: triggering_override.ref_v,
            threshold_percent_f_low: triggering_override.threshold_percent_f_low,
            threshold_percent_f_high: triggering_override.threshold_percent_f_high,
            threshold_percent_v_low: triggering_override.threshold_percent_v_low,
            threshold_percent_v_high: triggering_override.threshold_percent_v_high,
            threshold_percent_thd_high: triggering_override.threshold_percent_thd_high,
        }
    }
}

impl From<Triggering> for Threshold {
    fn from(triggering: Triggering) -> Self {
        Threshold {
            ref_f: triggering.default_ref_f,
            ref_v: triggering.default_ref_v,
            threshold_percent_f_low: triggering.default_threshold_percent_f_low,
            threshold_percent_f_high: triggering.default_threshold_percent_f_high,
            threshold_percent_v_low: triggering.default_threshold_percent_v_low,
            threshold_percent_v_high: triggering.default_threshold_percent_v_high,
            threshold_percent_thd_high: triggering.default_threshold_percent_thd_high,
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
}

impl CachedThresholdProvider {
    pub fn new(settings: ThresholdTriggerPluginSettings) -> CachedThresholdProvider {
        let makai_config = mongo::makai_config(&settings).unwrap();
        CachedThresholdProvider {
            threshold_cache: HashMap::new(),
            default_threshold: None,
            last_update: timestamp_ms(),
            settings,
            makai_config,
        }
    }

    fn update(&mut self) {
        self.makai_config = mongo::makai_config(&self.settings).unwrap();
        self.default_threshold = Some(self.makai_config.triggering.clone().into());
        for triggering_override in &self.makai_config.triggering.triggering_overrides {
            self.threshold_cache.insert(
                triggering_override.box_id.to_string(),
                triggering_override.clone().into(),
            );
        }
        self.last_update = timestamp_ms();
    }

    pub fn get(&mut self, box_id: &str) -> Threshold {
        let now = timestamp_ms();
        if now - self.last_update > 60000 {
            self.update();
        }
        match self.threshold_cache.get(box_id) {
            None => self.default_threshold.clone().unwrap(),
            Some(threshold) => threshold.clone(),
        }
    }
}
