extern crate serde;
#[macro_use]
extern crate serde_derive;
extern crate serde_json;
#[macro_use]
extern crate triggering_service;

use std::collections::HashMap;
use std::str;
use std::sync::Arc;
use std::time::{SystemTime, UNIX_EPOCH};

use triggering_service::makai_plugin::MakaiPlugin;
use triggering_service::proto::opqbox3::Command;
use triggering_service::proto::opqbox3::GetDataCommand;
use triggering_service::proto::opqbox3::Measurement;

fn timestamp_ms() -> u64 {
    let start = SystemTime::now();
    let since_the_epoch = start
        .duration_since(UNIX_EPOCH)
        .expect("Time went backwards");
    return (since_the_epoch.as_secs() as u128 * 1000 + since_the_epoch.subsec_millis() as u128)
        as u64;
}

type StateMap = HashMap<StateKey, StateEntry>;

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
    latest_state_timestamp_ms: u64,
}

impl StateEntry {
    pub fn new(state: State) -> StateEntry {
        let timestamp = timestamp_ms();
        StateEntry {
            prev_state: state.clone(),
            prev_state_timestamp_ms: timestamp,
            latest_state: state.clone(),
            latest_state_timestamp_ms: timestamp,
        }
    }

    fn mutable_update(&mut self, state: State) {
        self.prev_state = self.latest_state.clone();
        self.prev_state_timestamp_ms = self.latest_state_timestamp_ms;
        self.latest_state = state;
        self.latest_state_timestamp_ms = timestamp_ms();
    }
}

#[derive(Debug)]
pub struct Trigger {
    box_id: u32,
    start_timestamp_ms: u64,
    end_timestamp_ms: u64,
}

impl Trigger {
    fn from(box_id: u32, state_entry: &StateEntry) -> Trigger {
        Trigger {
            box_id,
            start_timestamp_ms: state_entry.prev_state_timestamp_ms,
            end_timestamp_ms: state_entry.latest_state_timestamp_ms,
        }
    }
}

#[derive(Debug, Hash, PartialEq, Eq, Clone)]
enum TriggerType {
    Frequency,
    Thd,
    Voltage,
}

#[derive(Debug, Hash, Eq, Clone)]
pub struct StateKey {
    box_id: u32,
    trigger_type: TriggerType,
}

impl StateKey {
    fn from(box_id: u32, trigger_type: TriggerType) -> StateKey {
        StateKey {
            box_id,
            trigger_type,
        }
    }
}

impl PartialEq for StateKey {
    fn eq(&self, other: &StateKey) -> bool {
        self.box_id == other.box_id && self.trigger_type == other.trigger_type
    }
}

#[derive(Debug, Default)]
pub struct Fsm {
    state_map: StateMap,
}

impl Fsm {
    pub fn new() -> Fsm {
        Fsm {
            state_map: HashMap::new(),
        }
    }

    pub fn update(&mut self, state_key: StateKey, new_state: State) {
        self.state_map
            .entry(state_key)
            .and_modify(|state_entry| state_entry.mutable_update(new_state))
            .or_insert(StateEntry::new(new_state));
    }

    pub fn is_triggering(&self, state_key: &StateKey) -> Option<Trigger> {
        match self.state_map.get(state_key) {
            Some(state_entry) => {
                if state_entry.prev_state == State::Triggering
                    && state_entry.latest_state == State::Nominal
                {
                    return Some(Trigger::from(state_key.box_id, state_entry));
                }
                None
            }
            _ => None,
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

    pub debug: bool
}

#[derive(Debug, Default)]
pub struct ThresholdTriggerPlugin {
    settings: ThresholdTriggerPluginSettings,
    frequency_threshold_low: f32,
    frequency_threshold_high: f32,
    voltage_threshold_low: f32,
    voltage_threshold_high: f32,
    thd_threshold_high: f32,

    fsm: Fsm,
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
            fsm: Fsm::new(),
        }
    }

    fn check_metric(
        &mut self,
        measurement: &Arc<Measurement>,
        metric: &str,
        trigger_type: TriggerType,
        threshold_low: f32,
        threshold_high: f32,
    ) -> Option<Trigger> {
        let state_key = StateKey::from(measurement.box_id, trigger_type);
        match measurement.metrics.get(metric) {
            None => return None,
            Some(metric) => {
                if metric.min < threshold_low || metric.max > threshold_high {
                    self.fsm.update(state_key.clone(), State::Triggering)
                } else {
                    self.fsm.update(state_key.clone(), State::Nominal)
                }
            }
        }
        self.fsm.is_triggering(&state_key)
    }

    fn check_frequency(&mut self, measurement: &Arc<Measurement>) -> Option<Trigger> {
        let threshold_low = self.frequency_threshold_low;
        let threshold_high = self.frequency_threshold_high;
        self.check_metric(
            measurement,
            "f",
            TriggerType::Frequency,
            threshold_low,
            threshold_high,
        )
    }

    fn check_voltage(&mut self, measurement: &Arc<Measurement>) -> Option<Trigger> {
        let threshold_low = self.voltage_threshold_low;
        let threshold_high = self.voltage_threshold_high;
        self.check_metric(
            measurement,
            "rms",
            TriggerType::Voltage,
            threshold_low,
            threshold_high,
        )
    }

    fn check_thd(&mut self, measurement: &Arc<Measurement>) -> Option<Trigger> {
        let threshold_low = -1.0;
        let threshold_high = self.thd_threshold_high;
        self.check_metric(
            measurement,
            "thd",
            TriggerType::Thd,
            threshold_low,
            threshold_high,
        )
    }

    fn trigger_cmd(&self, trigger: &Trigger) -> Command {
        let mut get_data_command = GetDataCommand::new();
        get_data_command.set_wait(true);
        get_data_command.set_start_ms(trigger.start_timestamp_ms);
        get_data_command.set_end_ms(trigger.end_timestamp_ms);
        let mut cmd = Command::new();
        cmd.set_box_id(trigger.box_id as i32);
        cmd.set_data_command(get_data_command);
        cmd.set_identity(String::new());
        cmd.set_timestamp_ms(timestamp_ms());
        cmd.set_seq(0);
        if self.settings.debug {
            println!("Sending CMD {:?}", self.fsm)
        }
        return cmd;
    }
}

impl MakaiPlugin for ThresholdTriggerPlugin {
    fn name(&self) -> &'static str {
        "Threshold Trigger Plugin"
    }

    fn process_measurement(&mut self, measurement: Arc<Measurement>) -> Option<Vec<Command>> {
        if self.settings.debug {
            println!("{:?}", self.fsm)
        }

        let mut cmds = Vec::new();

        match self.check_frequency(&measurement) {
            None => {}
            Some(trigger) => {
                cmds.push(self.trigger_cmd(&trigger));
            }
        }

        match self.check_voltage(&measurement) {
            None => {}
            Some(trigger) => {
                cmds.push(self.trigger_cmd(&trigger));
            }
        }

        match self.check_thd(&measurement) {
            None => {}
            Some(trigger) => {
                cmds.push(self.trigger_cmd(&trigger));
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
        self.frequency_threshold_low = self.settings.reference_frequency
            - (self.settings.reference_frequency * self.frequency_threshold_low);

        self.frequency_threshold_high = self.settings.reference_frequency
            + (self.settings.reference_frequency * self.frequency_threshold_high);

        self.voltage_threshold_low = self.settings.reference_voltage
            - (self.settings.reference_voltage * self.voltage_threshold_low);

        self.voltage_threshold_high = self.settings.reference_voltage
            + (self.settings.reference_voltage * self.voltage_threshold_high);
        
        self.thd_threshold_high = self.settings.thd_threshold_high;
    }

    fn on_plugin_unload(&mut self) {
        println!("Threshold Trigger Plugin unloaded.")
    }
}

declare_plugin!(ThresholdTriggerPlugin, ThresholdTriggerPlugin::new);

#[cfg(test)]
mod tests {
    use Fsm;
    use State;
    use StateKey;
    use TriggerType;
    use triggering_service::proto::opqbox3::Command_oneof_command::send_command_to_plugin;

    #[test]
    fn test() {
        let mut fsm = Fsm::new();
        let state_key = StateKey::from(1, TriggerType::Frequency);

        fsm.update(state_key.clone(), State::Nominal);
        assert_eq!(fsm.is_triggering(&state_key).is_some(), false);
        fsm.update(state_key.clone(), State::Nominal);
        assert_eq!(fsm.is_triggering(&state_key).is_some(), false);
        fsm.update(state_key.clone(), State::Triggering);
        assert_eq!(fsm.is_triggering(&state_key).is_some(), false);
        fsm.update(state_key.clone(), State::Triggering);
        assert_eq!(fsm.is_triggering(&state_key).is_some(), false);
        fsm.update(state_key.clone(), State::Nominal);
        assert_eq!(fsm.is_triggering(&state_key).is_some(), true);
    }
}

