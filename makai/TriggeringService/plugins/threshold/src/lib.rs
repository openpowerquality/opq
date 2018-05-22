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
use serde_json::{from_str, Value};
use std::hash::Hash;
use std::hash::Hasher;
use std::clone::Clone;

//Box id type.
type BoxId = i32;

//Box timestamp.
type OpqTimeStamp = u64;

//Measurement type enum.
#[derive(Debug, Clone)]
enum MeasurementType {
    V,
    F,
    Thd,
}

impl From<MeasurementType> for opqapi::RequestEventMessage_TriggerType {
    fn from(msg: MeasurementType) -> opqapi::RequestEventMessage_TriggerType {
        match msg{
            MeasurementType::V => {opqapi::RequestEventMessage_TriggerType::VOLTAGE_SAG},
            MeasurementType::F => {opqapi::RequestEventMessage_TriggerType::FREQUENCY_SAG},
            MeasurementType::Thd => {opqapi::RequestEventMessage_TriggerType::OTHER},
        }
    }
}

//A single measurement from the box.
#[derive(Debug, Default, Clone)]
struct Measurement {
    v: f32,
    f: f32,
    thd: f32,
}

impl<'a> Index<&'a MeasurementType> for Measurement {
    type Output = f32;

    //get measurement using the [] operator overload
    fn index(&self, measurement_type: &MeasurementType) -> &f32 {
        match measurement_type {
            &MeasurementType::V => &self.v,
            &MeasurementType::F => &self.f,
            &MeasurementType::Thd => &self.thd,
        }
    }
}

impl From<Arc<TriggerMessage>> for Measurement {
    fn from(msg: Arc<TriggerMessage>) -> Measurement {
        Measurement {
            v: msg.get_rms(),
            f: msg.get_frequency(),
            thd: if msg.has_thd() {
                msg.get_thd()
            } else {
                0.0
            },
        }
    }
}

#[derive(Debug, Clone)]
struct BoxEvent {
    pub id: BoxId,
    pub cause: Measurement,
    pub cause_type: MeasurementType,
    pub start_ts: OpqTimeStamp,
    pub end_ts: OpqTimeStamp,
}

impl Hash for BoxEvent {
    fn hash<H>(&self, state: &mut H)
    where
        H: Hasher,
    {
        (&self.id).hash(state);
    }
}

impl PartialEq for BoxEvent {
    fn eq(&self, other: &Self) -> bool {
        (&self.id) == (&other.id)
    }
}

impl Eq for BoxEvent {}

///Plugin state machine.
#[derive(Debug)]
enum PluginState {
    ///In Idle state.
    Idle,
    ///In an event.
    InEvent {
        ///The set of boxen experiencing the event.
        problems_boxes: HashMap<BoxId, BoxEvent>,
        ///Boxes waiting for readout.
        recovered_boxes: HashMap<BoxId, BoxEvent>,
        ///Start time for the event.
        start_ts: OpqTimeStamp,
    },
}

///The main type.
#[derive(Debug)]
pub struct ThresholdPlugin {
    state: PluginState,
    thresholds_min: Measurement,
    thresholds_max: Measurement,
}

///Plugin implementation
impl ThresholdPlugin {
    fn new() -> ThresholdPlugin {
        ThresholdPlugin {
            state: PluginState::Idle,
            thresholds_min: Measurement::default(),
            thresholds_max: Measurement::default(),
        }
    }

    fn make_desctiption(&self,end_ts : OpqTimeStamp) -> String{
        match self.state {
            PluginState::Idle => {String::new()},
            PluginState::InEvent {  ref problems_boxes, ref recovered_boxes, ref start_ts  } => {
                format!("Makai plugin {name}", name = self.name())
            }
        }
    }
}

///Makai Plugin trait implementation
impl MakaiPlugin for ThresholdPlugin {
    fn name(&self) -> &'static str {
        "Threshold Plugin"
    }

    fn on_plugin_load(&mut self, json: String) {
        let document: Value = from_str(&json).unwrap();
        println!("{:?}", document);
    }

    fn on_plugin_unload(&mut self) {
        println!("Threshold plugin unloaded.")
    }

    fn process_measurement(&mut self, msg: Arc<TriggerMessage>) -> Option<RequestEventMessage> {
        //Box id and timestamp of this measurement.
        let box_id = msg.get_id();
        let time_stamp = msg.get_time();
        //type conversion.
        let measuremt: Measurement = msg.into();
        //
        let mut in_event = false;
        let mut event_type = MeasurementType::F;
        //Itterate through each type of measurement and run the state machine.
        for mt in vec![MeasurementType::F, MeasurementType::V, MeasurementType::Thd] {
            if measuremt[&mt] < self.thresholds_min[&mt]
                || measuremt[&mt] > self.thresholds_max[&mt] {
                in_event = true;
                event_type = mt;
            }
        }
        if in_event {
            match self.state {
                PluginState::Idle => {
                    self.state = PluginState::InEvent {
                        problems_boxes: [
                            (box_id, BoxEvent {
                                id: box_id,
                                cause: measuremt.clone(),
                                cause_type: event_type,
                                start_ts: time_stamp,
                                end_ts: 0,
                            }),
                        ].iter()
                            .cloned()
                            .collect(),
                        recovered_boxes: HashMap::new(),
                        start_ts: time_stamp,
                    };
                }
                PluginState::InEvent { ref mut problems_boxes, ref mut recovered_boxes, start_ts: _ } => {
                    if !problems_boxes.contains_key(&box_id) {
                        problems_boxes.insert(box_id, BoxEvent {
                            id: box_id,
                            cause: measuremt,
                            cause_type: event_type,
                            start_ts: time_stamp,
                            end_ts: 0,
                        });
                    }
                    if recovered_boxes.contains_key(&box_id) {
                        problems_boxes.insert(box_id, recovered_boxes.remove(&box_id).unwrap());
                    }
                }
            }
        }
            else{
                match self.state {
                    PluginState::Idle => {}
                    PluginState::InEvent { ref mut problems_boxes, ref mut recovered_boxes, start_ts} => {
                        if problems_boxes.contains_key(&box_id){
                            recovered_boxes.insert(box_id, problems_boxes.remove(&box_id).unwrap());
                        }
                    }
                }
            }
        match self.state {
            PluginState::Idle => {},
            PluginState::InEvent { ref problems_boxes, ref recovered_boxes, start_ts} => {
                if problems_boxes.is_empty() {
                    let mut event_request = RequestEventMessage::new();
                    event_request.set_box_ids(recovered_boxes.iter()
                        .map(|(_, v)| (v.id)).collect::<Vec<BoxId>>());
                    event_request.set_start_timestamp_ms_utc(start_ts);
                    event_request.set_end_timestamp_ms_utc(time_stamp);
                    //Todo: fill in these fields
                    event_request.set_trigger_type(opqapi::RequestEventMessage_TriggerType::OTHER);
                    event_request.set_percent_magnitude(0.0);
                    event_request.set_requestee(format!("Makai: {}", self.name()));
                    event_request.set_request_data(false);
                    event_request.set_description(self.make_desctiption(time_stamp));
                    event_request
                }
            }
        }
        None
    }
}




declare_plugin!(ThresholdPlugin, ThresholdPlugin::new);
