#[macro_use]
extern crate opqapi;

use std::str;
use opqapi::MakaiPlugin;
use opqapi::protocol::opq::{RequestEventMessage, TriggerMessage};
use std::sync::Arc;
use std::fs::File;
use std::io::prelude::*;

extern crate serde;
extern crate serde_json;
#[macro_use] extern crate serde_derive;

extern crate ketos;
#[macro_use] extern crate ketos_derive;
//use ketos;

#[derive(Serialize, Deserialize, Default, Debug)]
struct KetosPluginSettings{
    script_path : String
}

pub struct KetosPlugin{
    settings : KetosPluginSettings,
    valid : bool,
    interp : ketos::Interpreter
}

impl KetosPlugin {
    fn new() -> KetosPlugin{
        KetosPlugin{
            settings : KetosPluginSettings::default(),
            valid : false,
            interp : ketos::Interpreter::new()
        }
    }
}

#[derive(Clone, Debug, ForeignValue, FromValueClone, StructValue)]
pub struct Measurement {
    pub frequency : f32,
    pub rms : f32,
    pub thd : f32,
    timestamp : u64,
    pub box_id : i32
}

#[derive(Clone, Debug, ForeignValue, FromValueClone, StructValue)]
pub struct Trigger {
    pub frequency : f32,
    pub rms : f32,
    pub thd : f32,
    timestamp : u64,
    pub box_id : i32
}


impl MakaiPlugin for KetosPlugin {

    fn name(&self) -> &'static str  {
        "Ketos Plugin"
    }

    fn on_plugin_load(&mut self, args : String) {
        let set = serde_json::from_str(&args);
        self.settings = match set{
            Ok(s) => {s},
            Err(e) => {println!("Bad setting file for plugin {}: {:?}", self.name(), e);self.valid = false; return},
        };
        self.interp.scope().register_struct_value::<Measurement>();
        self.interp.scope().register_struct_value::<Trigger>();

        let res = File::open(&self.settings.script_path);
        if let Ok(mut f) = res {
            let mut code = String::new();
            if let Err(e) = f.read_to_string(&mut code) {
                println!("Bad script file for Ketos plugin: {}.", e);
                self.valid = false;
                return;
            }
            if let Err(e) = self.interp.run_code(&code, None) {
                println!("Bad script file for Ketos plugin: {}.", e);
                self.valid = false;
                return;
            }
        }
        else { self.valid = false; }

        self.valid = true;
    }

    fn on_plugin_unload(&mut self) {
        println!("Print plugin unloaded.")
    }

    fn process_measurement(&mut self, msg: Arc<TriggerMessage>) -> Option<RequestEventMessage> {
        if !self.valid {
            return None;
        }
        let m = Measurement{
            frequency : msg.get_frequency(),
            rms : msg.get_rms(),
            thd : if msg.has_thd() {msg.get_thd()} else {0.},
            timestamp: msg.get_time(),
            box_id: msg.get_id(),
        };

        let res = self.interp.call("process_measurement",vec![ketos::Value::new_foreign(m)]).unwrap();
        match res {
            ketos::Value::Foreign(v) =>{

                None
            }
            _ => None
        }

    }
}

declare_plugin!(KetosPlugin, KetosPlugin::new);
