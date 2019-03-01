use std::sync::Mutex;
use std::sync::Arc;
use rouille::Response;
use types::{Statistics, HealthPluginSettings, MakaiStatus, SERVICE_NAME};
use std::time::{SystemTime, UNIX_EPOCH};

pub fn start_server(stats : Arc<Mutex<Statistics>>, settings : HealthPluginSettings) {
    let addr = settings.address.clone();
    rouille::start_server(addr, move |request| {
        router!(request,
        (GET) (/) => {
            let stats = stats.lock().unwrap();
            let mut status = MakaiStatus::default();
            status.name = SERVICE_NAME.to_string();
            status.ok = true;
            status.timestamp = SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_secs();
            for (_, value) in stats.box_status.iter(){
                status.subcomponents.push(value.clone());
            }
            Response::json(&status)
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