use std::any::Any;
use std::collections::HashMap;
use types;

pub trait TriggeringPlugin: Any {
    fn name(&self) -> &'static str;
    fn process_window(&mut self, msg: &mut types::Window) -> Option<HashMap<String, f32>>;
    fn process_command(&mut self, cmd: &String);
    fn init(&mut self);
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
        pub extern "C" fn _plugin_create() -> *mut $crate::plugin::TriggeringPlugin {
            // make sure the constructor is the correct type.
            let constructor: fn() -> $plugin_type = $constructor;

            let object = constructor();
            let boxed: Box<$crate::plugin::TriggeringPlugin> = Box::new(object);
            Box::into_raw(boxed)
        }
    };
}
