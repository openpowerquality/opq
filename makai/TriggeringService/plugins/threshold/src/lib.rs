

#[macro_use]
extern crate opqapi;
extern crate serde_json;

use std::str;
use opqapi::MakaiPlugin;
use opqapi::protocol::opq::{RequestEventMessage, TriggerMessage};
use std::sync::Arc;
use std::collections::HashMap;
use std::ops::Index;
use std::boxed::Box;
use serde_json::{Value, from_str};

#[derive(Debug)]
enum MeasurementType {v,f, thd}

#[derive(Debug, Default)]
struct MeasurementSet { v: f32, f: f32, thd: f32 }


impl Index<MeasurementType> for MeasurementSet {
    type Output = f32;

    fn index(&self, measurement_type: MeasurementType) -> &f32 {
        match measurement_type {
            MeasurementType::v => &self.v,
            MeasurementType::f => &self.f,
            MeasurementType::thd => &self.thd,
        }
    }
}

#[derive(Debug)]
enum DeviceEventState {
    Idle,
    InEvent { start: u64 },
}

#[derive(Debug)]
struct Device {
    state: DeviceEventState,

}

#[derive(Debug)]
pub struct ThresholdPlugin {
    boxes: HashMap<i32, DeviceEventState>,
    thresholds_min : MeasurementSet,
    thresholds_max : MeasurementSet,
}

impl ThresholdPlugin {
    fn new() -> ThresholdPlugin {
        ThresholdPlugin {
            boxes: HashMap::new(),
            thresholds_min : MeasurementSet::default(),
            thresholds_max : MeasurementSet::default(),
        }
    }
}

impl MakaiPlugin for ThresholdPlugin {
    fn name(&self) -> &'static str {
        "Threshold Plugin"
    }

    #[no_mangle]
    fn on_plugin_load(&mut self, json: String) {
        let document : Value = from_str(&json).unwrap();
        println!("{:?}", document);
    }

    fn on_plugin_unload(&mut self) {
        println!("Threshold plugin unloaded.")
    }

    fn process_measurement(&mut self, msg: Arc<TriggerMessage>) -> Option<RequestEventMessage> {
        None
    }
}

declare_plugin!(ThresholdPlugin, ThresholdPlugin::new);
