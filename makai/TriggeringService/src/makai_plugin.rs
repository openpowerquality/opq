use crate::proto::opqbox3::Command;
use crate::proto::opqbox3::Measurement;
use std::any::Any;
use std::sync::Arc;

pub trait MakaiPlugin: Any {
    fn name(&self) -> &'static str;
    fn process_measurement(&mut self, msg: Arc<Measurement>) -> Option<Vec<Command>>;
    fn on_plugin_load(&mut self, json: String);
    fn on_plugin_unload(&mut self);
}

/// Declare a plugin type and its constructor.
///
/// # Notes
///
/// This works by automatically generating an `extern "C"` function with a
/// pre-defined signature and symbol name. Therefore you will only be able to
/// declare one plugin per library.
#[macro_export]
macro_rules! declare_plugin {
    ($plugin_type:ty, $constructor:path) => {
        #[no_mangle]
        pub extern "C" fn _plugin_create() -> *mut crate::MakaiPlugin {
            // make sure the constructor is the correct type.
            let constructor: fn() -> $plugin_type = $constructor;

            let object = constructor();
            let boxed: Box<crate::MakaiPlugin> = Box::new(object);
            Box::into_raw(boxed)
        }
    };
}
