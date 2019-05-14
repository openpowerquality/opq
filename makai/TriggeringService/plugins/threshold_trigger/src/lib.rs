extern crate serde;
#[macro_use]
extern crate serde_derive;
extern crate serde_json;
#[macro_use]
extern crate triggering_service;
extern crate bson;
extern crate core;
extern crate mongodb;

use config::ThresholdTriggerPluginSettings;
use fsm::{Fsm, State, StateEntry, StateKey};
use serde_json::Error;
use std::str;
use std::sync::Arc;
use thresholds::{CachedThresholdProvider, Threshold};
use triggering_service::makai_plugin::MakaiPlugin;
use triggering_service::proto::opqbox3::Command;
use triggering_service::proto::opqbox3::GetDataCommand;
use triggering_service::proto::opqbox3::Measurement;

pub mod config;
pub mod datetime;
pub mod fsm;
pub mod mongo;
pub mod thresholds;

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
pub enum TriggerType {
    Frequency,
    Thd,
    Voltage,
}

#[derive(Debug, Default)]
pub struct ThresholdTriggerPlugin {
    settings: config::ThresholdTriggerPluginSettings,
    threshold_provider: Option<CachedThresholdProvider>,
    fsm: Fsm,
    loaded: bool,
}

const METRIC_F: &str = "f";
const METRIC_V: &str = "rms";
const METRIC_THD: &str = "thd";

impl ThresholdTriggerPlugin {
    fn new() -> ThresholdTriggerPlugin {
        let settings = config::ThresholdTriggerPluginSettings::default();
        ThresholdTriggerPlugin {
            settings: settings.clone(),
            threshold_provider: None,
            fsm: Fsm::new(),
            loaded: false,
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
        self.maybe_debug(
            measurement.box_id,
            &format!("Checking metric for {}", metric),
        );
        match measurement.metrics.get(metric) {
            None => {
                self.maybe_debug(
                    measurement.box_id,
                    &format!("No metric found for {}", metric),
                );
                return None;
            }
            Some(metric) => {
                if metric.min < threshold_low || metric.max > threshold_high {
                    self.maybe_debug(measurement.box_id, &format!("Metrics are triggering metric min:{} metric max:{} threshold low:{} threshold high: {}", metric.min, metric.max, threshold_low, threshold_high));
                    self.fsm.update(state_key.clone(), State::Triggering)
                } else {
                    self.maybe_debug(measurement.box_id, &format!("Metrics are nominal metric min:{} metric max:{} threshold low:{} threshold high: {}", metric.min, metric.max, threshold_low, threshold_high));
                    self.fsm.update(state_key.clone(), State::Nominal)
                }
            }
        }
        self.fsm.is_triggering(&state_key)
    }

    fn check_frequency(
        &mut self,
        measurement: &Arc<Measurement>,
        threshold: &Threshold,
    ) -> Option<Trigger> {
        self.check_metric(
            measurement,
            METRIC_F,
            TriggerType::Frequency,
            threshold.threshold_f_low as f32,
            threshold.threshold_f_high as f32,
        )
    }

    fn check_voltage(
        &mut self,
        measurement: &Arc<Measurement>,
        threshold: &Threshold,
    ) -> Option<Trigger> {
        self.check_metric(
            measurement,
            METRIC_V,
            TriggerType::Voltage,
            threshold.threshold_v_low as f32,
            threshold.threshold_v_high as f32,
        )
    }

    fn check_thd(
        &mut self,
        measurement: &Arc<Measurement>,
        threshold: &Threshold,
    ) -> Option<Trigger> {
        self.check_metric(
            measurement,
            METRIC_THD,
            TriggerType::Thd,
            -1.0,
            threshold.threshold_thd_high as f32,
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
        cmd.set_timestamp_ms(datetime::timestamp_ms());
        cmd.set_seq(0);
        self.maybe_debug(trigger.box_id, &format!("Sending CMD {:#?}", cmd));
        return cmd;
    }

    fn maybe_debug(&self, box_id: u32, msg: &str) {
        if self.settings.debug
            && (self.settings.debug_devices.is_empty()
                || self.settings.debug_devices.contains(&box_id))
        {
            println!("{}", msg);
        }
    }

    fn get_threshold(&mut self, box_id: &str) -> Option<Threshold> {
        match self.threshold_provider.as_mut() {
            None => None,
            Some(threshold_proivider) => Some(threshold_proivider.get(box_id)),
        }
    }
}

impl MakaiPlugin for ThresholdTriggerPlugin {
    fn name(&self) -> &'static str {
        "Threshold Trigger Plugin"
    }

    fn process_measurement(&mut self, measurement: Arc<Measurement>) -> Option<Vec<Command>> {
        if !self.loaded || self.threshold_provider.is_none() {
            println!("Err: process_measurement in threshold plugin called before plugin is loaded");
            return None;
        }

        match self.get_threshold(&measurement.box_id.to_string()) {
            None => return None,
            Some(threshold) => {
                self.maybe_debug(measurement.box_id, &format!("{:#?}", measurement));
                self.maybe_debug(measurement.box_id, &format!("{:#?}", self.fsm));

                let mut cmds = Vec::new();

                if let Some(trigger) = self.check_frequency(&measurement, &threshold) {
                    cmds.push(self.trigger_cmd(&trigger));
                }

                if let Some(trigger) = self.check_voltage(&measurement, &threshold) {
                    cmds.push(self.trigger_cmd(&trigger));
                }

                if let Some(trigger) = self.check_thd(&measurement, &threshold) {
                    cmds.push(self.trigger_cmd(&trigger));
                }

                if cmds.is_empty() {
                    None
                } else {
                    Some(cmds)
                }
            }
        }
    }

    fn on_plugin_load(&mut self, args: String) {
        let set: Result<ThresholdTriggerPluginSettings, Error> = serde_json::from_str(&args);
        self.settings = match set {
            Ok(plugin_settings) => {
                self.loaded = true;
                let mut provider = CachedThresholdProvider::new(plugin_settings.clone());
                provider.update();
                self.threshold_provider = Some(provider);
                plugin_settings
            }
            Err(e) => {
                println!("Bad setting found for plugin {}: {:#?}", self.name(), e);
                config::ThresholdTriggerPluginSettings::default()
            }
        };
    }

    fn on_plugin_unload(&mut self) {
        println!("Threshold Trigger Plugin unloaded.")
    }
}

declare_plugin!(ThresholdTriggerPlugin, ThresholdTriggerPlugin::new);
