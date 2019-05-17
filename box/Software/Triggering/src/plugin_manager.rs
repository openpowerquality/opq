use crossbeam_channel::{Receiver, Sender};
use libloading::{Library, Symbol};
use std::boxed::Box;
use std::collections::HashMap;
use std::sync::Arc;
use std::thread;
use std::time::SystemTime;

use box_api::opqbox3::SendCommandToPlugin;
use box_api::plugin::TriggeringPlugin;
use box_api::types;
use config::State;
use config::INTERNAL_PLUGINS;

///A structure used to keep track of dynamically loaded plugins.
struct PluginManager {
    libraries: Vec<Library>,
}

impl PluginManager {
    ///Creates a new plugin manager. You should probly only have one of these in your app.
    fn new() -> PluginManager {
        PluginManager { libraries: vec![] }
    }

    /// Load a plugin from a shared library. Here be dragons!
    ///Box<TriggeringPlugin>
    /// # Safety
    ///
    /// This function is `unsafe` because there are no guarantees that the
    /// plugin loaded will be correct. In particular, all plugins must be
    /// compiled against the *exact* same version of the library that will beilure to ensure ABI compatibility will most probably result in UB
    /// loading them!
    ///
    /// Failure to ensure ABI compatibility will most probably result in UB
    /// because the vtable we expect to get (from `Box<TriggeringPlugin>`) and the vtable
    /// we actually get may be completely different.
    fn load_plugin(&mut self, path: &String) -> Result<Box<TriggeringPlugin>, String> {
        // We need to keep the library around otherwise our plugin's vtable will
        // point to garbage. We do this little dance to make sure the library
        // doesn't end up getting moved.
        match Library::new(path) {
            Ok(l) => self.libraries.push(l),
            Err(e) => {
                let mut err: String = "Could not load library plugin".to_owned();
                err.push_str(path);
                err.push_str(" : ");
                err.push_str(&e.to_string());
                return Err(err);
            }
        };
        unsafe {
            let constructor: Symbol<unsafe fn() -> *mut TriggeringPlugin> =
                match self.libraries.last().unwrap().get(b"_plugin_create") {
                    Ok(k) => k,
                    Err(_) => {
                        let mut error: String =
                            "Could not find the entry point into plugin {}".to_owned();
                        error.push_str(path);
                        return Err(error);
                    }
                };
            let boxed_raw = constructor();
            let mut result = Box::from_raw(boxed_raw);
            result.init();
            Ok(result)
        }
    }
}

pub fn run_plugins(
    rx: Receiver<types::Window>,
    tx: Sender<types::Window>,
    command_rx: Receiver<SendCommandToPlugin>,
    config: Arc<State>,
) -> thread::JoinHandle<()> {
    thread::spawn(move || {
        let mut plugins = vec![];
        let mut manager = PluginManager::new();

        for func in &INTERNAL_PLUGINS {
            plugins.push(func());
        }

        for path in config.settings.plugins.clone() {
            plugins.push(match manager.load_plugin(&path) {
                Ok(plg) => {
                    info!("Loaded plugin {}", path);
                    plg
                }
                Err(e) => {
                    warn!("{}", e);
                    continue;
                }
            });
        }
        loop {
            select! {
                //Here we handle the data stream.
                recv(rx, window_option) =>
                {
                    if let Some(mut window) = window_option {
                        window.time_stamp_ms = SystemTime::now();
                        let outputs: Vec < Option < HashMap < String, f32 > > > = plugins.iter_mut()
                        .map( | x | x.process_window( & mut window))
                        .collect();
                        for output in outputs {
                            if let Some(map) = output {
                                window.results.extend(map);
                            }
                        }

                        tx.send(window);
                    }
                },
                //Here we handle the command stream.
                recv(command_rx, cmd_option) => {
                    if let Some(cmd) = cmd_option{
                        for plugin in &mut plugins{
                            if plugin.name() == cmd.plugin_name{
                                plugin.process_command(&cmd.message);
                            }
                        }
                    }
                }
            }
        }
    })
}
