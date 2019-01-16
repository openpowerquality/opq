#[macro_use]
extern crate triggering_service;
use std::str;
use triggering_service::makai_plugin::MakaiPlugin;
use triggering_service::proto::opqbox3::Measurement;
use triggering_service::proto::makai::RequestEventMessage;
use std::sync::Arc;

#[macro_use] extern crate serde_derive;
extern crate serde;
extern crate serde_json;

#[derive(Serialize, Deserialize, Default, Debug)]
struct PrintPluginSettings{
    pub print : bool
}

#[derive(Debug, Default)]
pub struct PrintPlugin{
    settings : PrintPluginSettings
}

impl PrintPlugin {
    fn new() -> PrintPlugin{
        PrintPlugin{
            settings : PrintPluginSettings::default()
        }
    }
}

impl MakaiPlugin for PrintPlugin {

    fn name(&self) -> &'static str  {
        "Print Plugin"
    }

    fn process_measurement(&mut self, msg: Arc<Measurement>) -> Option<RequestEventMessage> {
        if self.settings.print{
            println!("{:?}", msg);
        }
        None
    }

    fn on_plugin_load(&mut self, args : String) {
        let set = serde_json::from_str(&args);
        self.settings = match set{
            Ok(s) => {s},
            Err(e) => {println!("Bad setting fie for plugin {}: {:?}", self.name(), e); PrintPluginSettings::default()},
        }
    }

    fn on_plugin_unload(&mut self) {
        println!("Print plugin unloaded.")
    }
}

declare_plugin!(PrintPlugin, PrintPlugin::new);
