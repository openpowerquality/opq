use std::sync::Arc;
use std::sync::Mutex;

use std::time::{SystemTime, UNIX_EPOCH};
use types::{HealthPluginSettings, MakaiStatus, Statistics, SERVICE_NAME};

use iron::prelude::*;
use iron::status;
use iron::Handler;

struct Router {
    stats: Arc<Mutex<Statistics>>
}

impl Router {
    fn new(stats: Arc<Mutex<Statistics>>) -> Self {
        Router {
            stats
        }
    }
}

impl Handler for Router {
    fn handle(&self, req: &mut Request) -> IronResult<Response> {
        match req.url.path().join("/").as_str(){
            "trigger" => {
                let mut stats = self.stats.lock().unwrap();
                stats.trigger_now = true;
                Ok(Response::with((status::ImATeapot, "Triggered")))
            },
            "" => {
                let stats = self.stats.lock().unwrap();
                let mut status = MakaiStatus::default();
                status.name = SERVICE_NAME.to_string();
                status.ok = true;
                status.timestamp = SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_secs();
                for (_, value) in stats.box_status.iter(){
                    status.subcomponents.push(value.clone());
                }
                Ok(Response::with((status::Ok, serde_json::to_string(&status).unwrap())))
            },
            _ => Ok(Response::with(status::NotFound)),
        }

    }
}


pub fn start_server(stats: Arc<Mutex<Statistics>>, settings: HealthPluginSettings) {
    let addr = settings.address.clone();
    let rtr = Router::new(stats);
    Iron::new(rtr).http(addr).unwrap();
}
