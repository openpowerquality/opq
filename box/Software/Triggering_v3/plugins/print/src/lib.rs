#[macro_use]
extern crate triggering_v3;

use triggering_v3::types::Window;

#[derive(Debug, Default)]
pub struct PrintPlugin{
}

impl PrintPlugin {
    fn new() -> PrintPlugin{
        PrintPlugin{
        }
    }
}

impl triggering_v3::plugin::TriggeringPlugin for PrintPlugin {

    fn name(&self) -> &'static str  {
        "Print Plugin"
    }

    fn process_window(&mut self, msg: &mut Window) {
        println!("{:?}", msg);
    }


    fn init(&mut self) {
        println!("loaded a print pluggin!");
    }
}

declare_plugin!(PrintPlugin, PrintPlugin::new);
