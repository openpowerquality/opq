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

fn timestamp_ms() -> u64 {
    let start = SystemTime::now();
    let since_the_epoch = start.duration_since(UNIX_EPOCH)
        .expect("Time went backwards");
    return
        (since_the_epoch.as_secs() as u128 * 1000
            + since_the_epoch.subsec_millis() as u128) as u64;
}

#[derive(Debug, Clone, Copy, PartialEq)]
pub enum State {
    Nominal,
    Triggering,
}

#[derive(Debug)]
pub struct StateEntry {
    prev_state: State,
    prev_state_timestamp_ms: u64,
    latest_state: State,
    latest_state_timestamp_ms: u64
}

#[derive(Debug)]
pub struct Trigger {
    box_id: u32,
    start_timestamp_ms: u64,
    end_timestamp_ms: u64
}

#[derive(Debug, Hash, PartialEq, Eq)]
enum TriggerType {
    Frequency,
    Thd,
    Voltage
}

#[derive(Debug, Hash, Eq)]
pub struct StateKey {
    box_id: u32,
    trigger_type: TriggerType
}

impl PartialEq for StateKey {
    fn eq(&self, other: &StateKey) -> bool {
        self.box_id == other.box_id
    }
}

impl StateKey {
    fn from(box_id: u32, trigger_type: TriggerType) -> StateKey {
        StateKey {
            box_id,
            trigger_type
        }
    }
}

impl Trigger {
    fn from(box_id: u32, state_entry: &StateEntry) -> Trigger {
        Trigger {
            box_id,
            start_timestamp_ms: state_entry.prev_state_timestamp_ms,
            end_timestamp_ms: state_entry.latest_state_timestamp_ms
        }
    }
}

impl StateEntry {
    pub fn new(state: State) -> StateEntry {
        let timestamp = timestamp_ms();
        StateEntry {
            prev_state: state.clone(),
            prev_state_timestamp_ms: timestamp,
            latest_state: state.clone(),
            latest_state_timestamp_ms: timestamp
        }
    }

    fn mutable_update(&mut self, state: State) {
        self.prev_state = self.latest_state.clone();
        self.prev_state_timestamp_ms = self.latest_state_timestamp_ms;
        self.latest_state = state;
        self.latest_state_timestamp_ms = timestamp_ms();
    }
}

type StateMap = HashMap<StateKey, StateEntry>;

#[derive(Debug, Default)]
pub struct Fsm {
    state_map: StateMap
}

impl Fsm {
    pub fn new() -> Fsm {
        Fsm {
            state_map: HashMap::new()
        }
    }

    pub fn update(&mut self, state_key: StateKey,  new_state: State) {
        self.state_map.entry(state_key)
            .and_modify(|state_entry| state_entry.mutable_update(new_state))
            .or_insert(StateEntry::new(new_state));
    }

    pub fn is_triggering(&self, state_key: StateKey) -> Option<Trigger> {
        match self.state_map.get(&state_key) {
            Some(state_entry) => {
                if state_entry.prev_state == State::Triggering &&
                    state_entry.latest_state == State::Nominal {
                    return Some(Trigger::from(state_key.box_id, state_entry));
                }
                None
            },
            _ => None
        }
    }
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

    fsm: Fsm
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
            fsm: Fsm::new()
        }
    }

    fn get_state(&self, measurement: Arc<Measurement>) -> Option<State> {
        let timestamp = timestamp_ms();

        if (!measurement.metrics.contains_key("f")) &&
            (!measurement.metrics.contains_key("rms")) &&
            (!measurement.metrics.contains_key("thd")) {
            return None;
        }

        match measurement.metrics.get("rms") {
            None => {},
            Some(metric) => {
                if metric.min < self.voltage_threshold_low || metric.max > self.voltage_threshold_high {
                    return Some(State::Triggering)
                }
            }
        }
        match measurement.metrics.get("f") {
            None => {},
            Some(metric) => {
                if metric.min < self.frequency_threshold_low || metric.max > self.frequency_threshold_high {
                    return Some(State::Triggering)
                }
            },
        }
        None
    }
}

impl MakaiPlugin for ThresholdTriggerPlugin {
    fn name(&self) -> &'static str {
        "Threshold Trigger Plugin"
    }

    fn process_measurement(&mut self, measurement: Arc<Measurement>) -> Option<Vec<Command>> {
//        let state = self.state(measurement.clone());
//        let measurement = measurement.clone();
//        match state {
//            ThresholdState::NotAvailable(_) => {}
//            ThresholdState::Nominal(_) => {
//                match self.box_trigger_state.get(&measurement.box_id) {
//                    Some(ThresholdState::NotAvailable(_)) => {}
//                    // Previous value was nominal, current value is nominal, keep on keeping on
//                    Some(ThresholdState::Nominal(_)) => {}
//                    // There was no previous value, insert a nominal value
//                    None => {
//                        self.box_trigger_state.insert(measurement.box_id, state);
//                    }
//                    // Previous value was nominal, new value is triggering
//                    Some(ThresholdState::Triggering(_)) => {
//                        self.box_trigger_state.insert(measurement.box_id, state);
//                    }
//                }
//            },
//            ThresholdState::Triggering(triggering_timestamp) => match self.box_trigger_state.get(&measurement.box_id) {
//                Some(ThresholdState::NotAvailable(_)) => {}
//                // Previous value was triggering, current value is triggering, still triggering
//                Some(ThresholdState::Triggering(_)) => {}
//                // There was no previous value, current value is triggering
//                None => {
//                    self.box_trigger_state.insert(measurement.box_id, state);
//                }
//                // Previous state was triggering, now nominal, request data
//                Some(ThresholdState::Nominal(nominal_timestamp)) => {
//                    // Request data
//                    let mut get_data_command = GetDataCommand::new();
//                    get_data_command.set_wait(true);
//                    get_data_command.set_start_ms(triggering_timestamp);
//                    get_data_command.set_end_ms(nominal_timestamp.clone());
//                    let mut cmd = Command::new();
//                    cmd.set_box_id(measurement.box_id as i32);
//                    cmd.set_data_command(get_data_command);
//                    cmd.set_identity(String::new());
//                    cmd.set_timestamp_ms(timestamp_ms());
//                    cmd.set_seq(0);
//                    Some(vec![cmd]);
//                }
//            }
//        }
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
