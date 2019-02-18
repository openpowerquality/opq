use std::sync::Mutex;
use std::sync::Arc;
use rouille::Request;
use rouille::Response;
use types::{Statistics, HealthPluginSettings};

pub fn start_server(stats : Arc<Mutex<Statistics>>, settings : HealthPluginSettings) {
    let addr = settings.address.clone();
    rouille::start_server(addr, move |request| {
        router!(request,
        (GET) (/) => {

            let stats = stats.lock().unwrap();
            let mut out = Vec::new();
            for (key, value) in stats.box_status.iter(){
                out.push(value.clone());
            }
            Response::json(&out)
        },
        (GET) (/trigger) => {
            let mut stats = stats.lock().unwrap();
            stats.trigger_now = true;
            Response::html("Triggered!")
        },

        _ => Response::empty_404()
    )

    })
}