#[macro_use]
extern crate triggering_service;
use std::collections::HashMap;
use std::str;
use std::sync::Arc;
use std::time::{SystemTime, UNIX_EPOCH};
use triggering_service::makai_plugin::MakaiPlugin;
use triggering_service::proto::opqbox3::Command;
use triggering_service::proto::opqbox3::Measurement;
use triggering_service::proto::opqbox3::GetDataCommand;

#[macro_use]
extern crate serde_derive;
extern crate serde;
extern crate serde_json;

#[derive(Serialize, Deserialize, Debug, PartialEq)]
enum ThresholdState {
    Nominal(u64),
    Triggering(u64),
    NotAvailable(u64)
}

#[derive(Serialize, Deserialize, Default, Debug, Clone)]
struct ThresholdTriggerPluginSettings {
    pub reference_frequency: f32,
    pub frequency_threshold_percent_low: f32,
    pub frequency_threshold_percent_high: f32,

    pub reference_voltage: f32,
    pub voltage_threshold_percent_low: f32,
    pub voltage_threshold_percent_high: f32,

    pub thd_threshold_high: f32,
}

#[derive(Debug, Default)]
pub struct ThresholdTriggerPlugin {
    settings: ThresholdTriggerPluginSettings,
    frequency_threshold_low: f32,
    frequency_threshold_high: f32,
    voltage_threshold_low: f32,
    voltage_threshold_high: f32,
    thd_threshold_high: f32,

    box_trigger_state: HashMap<u32, ThresholdState>,
}

fn timestamp_ms() -> u64 {
    let start = SystemTime::now();
    let since_the_epoch = start.duration_since(UNIX_EPOCH).expect("Error creating timestamp");
    (since_the_epoch.as_secs() as u128 * 1000 + since_the_epoch.subsec_millis() as u128) as u64
}

fn variant_eq<T>(a: &T, b: &T) -> bool {
    std::mem::discriminant(a) == std::mem::discriminant(b)
}

impl ThresholdTriggerPlugin {
    fn new() -> ThresholdTriggerPlugin {
        ThresholdTriggerPlugin {
            settings: ThresholdTriggerPluginSettings::default(),
            frequency_threshold_low: 0.0,
            frequency_threshold_high: 0.0,
            voltage_threshold_low: 0.0,
            voltage_threshold_high: 0.0,
            thd_threshold_high: 0.0,
            box_trigger_state: HashMap::new()
        }
    }

    fn frequency_state(&self, measurement: Arc<Measurement>) -> ThresholdState {
        let timestamp = timestamp_ms();
        match measurement.metrics.get("f") {
            Some(metric) => {
                if metric.min < self.frequency_threshold_low
                    || metric.max > self.frequency_threshold_high
                {
                    ThresholdState::Triggering(timestamp)
                } else {
                    ThresholdState::Nominal(timestamp)
                }
            }
            None => ThresholdState::NotAvailable(timestamp),
        }
    }

    fn voltage_state(&self, measurement: Arc<Measurement>) -> ThresholdState {
        let timestamp = timestamp_ms();
        match measurement.metrics.get("rms") {
            Some(metric) => {
                if metric.min < self.voltage_threshold_low
                    || metric.max > self.voltage_threshold_high
                {
                    ThresholdState::Triggering(timestamp)
                } else {
                    ThresholdState::Nominal(timestamp)
                }
            }
            None => ThresholdState::NotAvailable(timestamp),
        }
    }

    fn thd_state(&self, measurement: Arc<Measurement>) -> ThresholdState {
        let timestamp = timestamp_ms();
        match measurement.metrics.get("thd") {
            Some(metric) => {
                if metric.min > self.thd_threshold_high || metric.max > self.thd_threshold_high {
                    ThresholdState::Triggering(timestamp)
                } else {
                    ThresholdState::Nominal(timestamp)
                }
            }
            None => ThresholdState::NotAvailable(timestamp),
        }
    }

    fn state(&self, measurement: Arc<Measurement>) -> ThresholdState {
        let frequency_state = self.frequency_state(measurement.clone());
        let voltage_state = self.voltage_state(measurement.clone());
        let thd_state = self.thd_state(measurement.clone());

        let timestamp = timestamp_ms();

        if variant_eq(&frequency_state, &ThresholdState::NotAvailable(0)) &&
            variant_eq(&voltage_state, &ThresholdState::NotAvailable(0)) &&
            variant_eq( &thd_state, &ThresholdState::NotAvailable(0)) {
            ThresholdState::NotAvailable(timestamp);
        }

        if variant_eq(&frequency_state, &ThresholdState::Nominal(0)) &&
            variant_eq(&voltage_state, &ThresholdState::Nominal(0)) &&
            variant_eq( &thd_state, &ThresholdState::Nominal(0)) {
            ThresholdState::Nominal(timestamp);
        }

        ThresholdState::Triggering(timestamp)
    }
}

impl MakaiPlugin for ThresholdTriggerPlugin {
    fn name(&self) -> &'static str {
        "Threshold Trigger Plugin"
    }

    fn process_measurement(&mut self, measurement: Arc<Measurement>) -> Option<Vec<Command>> {
        let state = self.state(measurement.clone());
        let measurement = measurement.clone();
        match state {
            ThresholdState::NotAvailable(_) => {}
            ThresholdState::Nominal(_) => {
                match self.box_trigger_state.get(&measurement.box_id) {
                    Some(ThresholdState::NotAvailable(_)) => {}
                    // Previous value was nominal, current value is nominal, keep on keeping on
                    Some(ThresholdState::Nominal(_)) => {}
                    // There was no previous value, insert a nominal value
                    None => {
                        self.box_trigger_state.insert(measurement.box_id, state);
                    }
                    // Previous value was nominal, new value is triggering
                    Some(ThresholdState::Triggering(_)) => {
                        self.box_trigger_state.insert(measurement.box_id, state);
                    }
                }
            },
            ThresholdState::Triggering(triggering_timestamp) => match self.box_trigger_state.get(&measurement.box_id) {
                Some(ThresholdState::NotAvailable(_)) => {}
                // Previous value was triggering, current value is triggering, still triggering
                Some(ThresholdState::Triggering(_)) => {}
                // There was no previous value, current value is triggering
                None => {
                    self.box_trigger_state.insert(measurement.box_id, state);
                }
                // Previous state was triggering, now nominal, request data
                Some(ThresholdState::Nominal(nominal_timestamp)) => {
                    // Request data
                    let mut get_data_command = GetDataCommand::new();
                    get_data_command.set_wait(true);
                    get_data_command.set_start_ms(triggering_timestamp);
                    get_data_command.set_end_ms(nominal_timestamp.clone());
                    let mut cmd = Command::new();
                    cmd.set_box_id(measurement.box_id as i32);
                    cmd.set_data_command(get_data_command);
                    cmd.set_identity(String::new());
                    cmd.set_timestamp_ms(timestamp_ms());
                    cmd.set_seq(0);
                    Some(vec![cmd]);
                }
            }
        }
        None
    }

    fn on_plugin_load(&mut self, args: String) {
        let set = serde_json::from_str(&args);
        self.settings = match set {
            Ok(s) => s,
            Err(e) => {
                println!("Bad setting found for plugin {}: {:?}", self.name(), e);
                ThresholdTriggerPluginSettings::default()
            }
        };
        self.frequency_threshold_low = self.settings.reference_frequency - (self.settings.reference_frequency * self.frequency_threshold_low);
        self.frequency_threshold_high = self.settings.reference_frequency + (self.settings.reference_frequency * self.frequency_threshold_high);
        self.voltage_threshold_low = self.settings.reference_voltage - (self.settings.reference_voltage * self.frequency_threshold_low);
        self.voltage_threshold_high = self.settings.reference_voltage - (self.settings.reference_voltage * self.frequency_threshold_high);
        self.thd_threshold_high = self.settings.thd_threshold_high;
    }

    fn on_plugin_unload(&mut self) {
        println!("Threshold Trigger Plugin unloaded.")
    }
}

declare_plugin!(ThresholdTriggerPlugin, ThresholdTriggerPlugin::new);
