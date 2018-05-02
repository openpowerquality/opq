use std::thread;
use std::sync::{Arc, Mutex};
use std::boxed::Box;


use pub_sub::Subscription;
use libloading::{Library, Symbol};
use zmq;
use serde_json;

use event_requester::{EventRequester, SyncEventRequester};
use opqapi::MakaiPlugin;
use opqapi::protocol::TriggerMessage;
use config::Settings;

///A structure used to keep track of dynamically loaded plugins.
pub struct PluginManager {
    ///A vector of running threads. These are persistent and will stick around until the app exits.
    plugin_threads: Vec<thread::JoinHandle<()>>,
    ///The connection to the acquisition broker.
    trigger: SyncEventRequester,
}

impl PluginManager {
    ///Creates a new plugin manager. You should probly only have one of these in your app.
    pub fn new(ctx: &zmq::Context, settings: &Settings) -> PluginManager {
        PluginManager {
            plugin_threads: Vec::new(),
            trigger: Arc::new(Mutex::new(EventRequester::new(ctx, settings))),
        }
    }

    /// Load a plugin from a shared library. Here be dragons!
    ///
    /// # Safety
    ///
    /// This function is `unsafe` because there are no guarantees that the
    /// plugin loaded will be correct. In particular, all plugins must be
    /// compiled against the *exact* same version of the library that will be
    /// loading them!
    ///
    /// Failure to ensure ABI compatibility will most probably result in UB
    /// because the vtable we expect to get (from `Box<MakaiPlugin>`) and the vtable
    /// we actually get may be completely different.
    pub unsafe fn load_plugin(
        &mut self,
        document: serde_json::Value,
        subscription: Subscription<Arc<TriggerMessage>>,

    ) -> Result<(), String> {
        let filename = document.get("path").unwrap().as_str().unwrap().to_string();
        let filename_copy = filename.clone();
        type PluginCreate = unsafe fn() -> *mut MakaiPlugin;

        let trigger = self.trigger.clone();

        self.plugin_threads.push(thread::spawn(move || {

            // We need to keep the library around otherwise our plugin's vtable will
            // point to garbage. We do this little dance to make sure the library
            // doesn't end up getting moved.
            let lib = match Library::new(filename){
                Ok(l) => {l},
                Err(e) => {println!("Could not load library plugin {}: {}", filename_copy, e); return;},
            };


            let constructor: Symbol<PluginCreate> = match lib.get(b"_plugin_create"){
                Ok(k) => {k},
                Err(_) => {println!("Could not find the entry point into plugin {}", filename_copy); return},
            };

            let boxed_raw = constructor();

            let mut plugin = Box::from_raw(boxed_raw);

            plugin.on_plugin_load(document.to_string());
            loop {
                let msg = subscription.recv().unwrap();
                if let Some(x) = plugin.process_measurement(msg) {
                    trigger.lock().unwrap().trigger(x)
                };
            }
        }));

        Ok(())
    }
}
