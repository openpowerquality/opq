use std::sync::atomic::{AtomicI32, Ordering};
use std::sync::Arc;
use std::thread;

use crate::config::Settings;
use crate::constants;

use bson::*;
use log;
use mongodb::{coll::options::FindOptions, db::ThreadedDatabase, Client, ThreadedClient};
use zmq;

/// Queries the MongoDB and returns the largest event_id in the database.
/// This is only called once when the event service starts.
fn find_largest_event_number(settings: &Settings) -> i32 {
    let client: Client = Client::connect(&settings.mongo_host, settings.mongo_port).unwrap();

    let event_db = client
        .db(constants::MONGO_DATABASE)
        .collection(constants::MONGO_EVENTS_COLLECTION);

    let sort = doc!(
        constants::MONGO_BOX_EVENTS_ID_FIELD : -1,
    );
    let filter = doc! {
        constants::MONGO_BOX_EVENTS_ID_FIELD : 1
    };
    let mut opt = FindOptions::new();
    opt.sort = Some(sort);
    opt.projection = Some(filter);

    let query_result = event_db.find_one(None, Some(opt));
    match query_result {
        Ok(Some(doc)) => match doc.get(constants::MONGO_EVENTS_ID_FIELD) {
            Some(&Bson::I32(ref num)) => num.clone() as i32,
            _ => 0 as i32,
        },
        Ok(None) => 0 as i32,
        Err(_) => 0 as i32,
    }
}

/// This struct encapsulates the EventIdService and provides atomic access to monotonically
/// increasing event_ids.
pub struct EventIdService {
    event_id: AtomicI32,
}

impl EventIdService {
    /// Instantiates this service by getting the highest available event_id currently stored in
    /// MongoDB.
    pub fn with_settings(settings: &Settings) -> EventIdService {
        let starting_event_id = find_largest_event_number(&settings);
        EventIdService::with_starting_event_id(starting_event_id)
    }

    /// Instantiates this service with the provided event_id.
    pub fn with_starting_event_id(starting_event_id: i32) -> EventIdService {
        EventIdService {
            event_id: AtomicI32::new(starting_event_id),
        }
    }

    /// Atomically increments and returns the next available event_id.
    pub fn inc_and_get(&self) -> i32 {
        // Note: fetch_add returns the previous value. So to get the next value, we need to add 1
        self.event_id.fetch_add(1, Ordering::SeqCst) + 1
    }

    /// Atomically peaks at the next available event_id without incrementing the value.
    pub fn peak(&self) -> i32 {
        self.event_id.load(Ordering::SeqCst)
    }
}

/// A ZMQ broker using request/reply semantics.
/// When a request is received, a reply with the next available event_id is sent.
pub struct EventIdBroker {
    event_id_service: Arc<EventIdService>,
    event_id_endpoint: zmq::Socket,
}

impl EventIdBroker {
    pub fn new(
        event_id_service: Arc<EventIdService>,
        ctx: &zmq::Context,
        settings: &Settings,
    ) -> EventIdBroker {
        let socket = ctx.socket(zmq::REP).unwrap();
        socket.bind(&settings.zmq_event_id_endpoint).unwrap();
        EventIdBroker {
            event_id_service,
            event_id_endpoint: socket,
        }
    }

    fn run_loop(&self) {
        loop {
            match self.event_id_endpoint.recv_string(0) {
                Ok(res) => match res {
                    Ok(req) => {
                        if req == "exit" {
                            break;
                        }
                        let reply = self.event_id_service.inc_and_get().to_string();
                        if let Err(e) = self.event_id_endpoint.send_str(&reply, 0) {
                            log::error!("Error sending event_id response: {:?}", e);
                        }
                    }
                    Err(_) => log::error!(
                        "Error receiving event_id request, received a Vec<u8> instead of a String."
                    ),
                },
                Err(err) => log::error!("Error receiving event_id request: {:?}", err),
            }
        }
    }

    pub fn run_service(self) {
        thread::spawn(move || self.run_loop());
    }
}

#[cfg(test)]
mod tests {
    use crate::config::Settings;
    use crate::event_ids::{EventIdBroker, EventIdService};
    use std::sync::Arc;

    #[test]
    fn test_peak_without_inc() {
        let event_id_service = EventIdService::with_starting_event_id(0);
        assert_eq!(event_id_service.peak(), 0);
    }

    #[test]
    fn test_peaks_without_inc() {
        let event_id_service = EventIdService::with_starting_event_id(0);
        assert_eq!(event_id_service.peak(), 0);
        assert_eq!(event_id_service.peak(), 0);
    }

    #[test]
    fn test_inc_single() {
        let event_id_service = EventIdService::with_starting_event_id(0);
        assert_eq!(event_id_service.inc_and_get(), 1);
    }

    #[test]
    fn test_incs() {
        let event_id_service = EventIdService::with_starting_event_id(0);
        assert_eq!(event_id_service.inc_and_get(), 1);
        assert_eq!(event_id_service.inc_and_get(), 2);
        assert_eq!(event_id_service.inc_and_get(), 3);
    }

    #[test]
    fn test_incs_and_peaks() {
        let event_id_service = EventIdService::with_starting_event_id(0);
        assert_eq!(event_id_service.peak(), 0);
        assert_eq!(event_id_service.inc_and_get(), 1);
        assert_eq!(event_id_service.peak(), 1);
        assert_eq!(event_id_service.inc_and_get(), 2);
        assert_eq!(event_id_service.peak(), 2);
        assert_eq!(event_id_service.inc_and_get(), 3);
        assert_eq!(event_id_service.peak(), 3);
    }

    #[test]
    fn test_broker() {
        let event_id_service = EventIdService::with_starting_event_id(0);
        let ctx = zmq::Context::new();
        let settings = Settings {
            zmq_event_id_endpoint: "tcp://*:10001".to_string(),
            ..Settings::default()
        };
        let event_id_broker = EventIdBroker::new(Arc::new(event_id_service), &ctx, &settings);
        event_id_broker.run_service();

        // Setup a test ZMQ client
        let zmq_client = ctx.socket(zmq::REQ).unwrap();
        zmq_client.connect("tcp://localhost:10001").unwrap();

        zmq_client.send_str("", 0).unwrap();
        assert_eq!(zmq_client.recv_string(0).unwrap().unwrap(), "1");

        zmq_client.send_str("", 0).unwrap();
        assert_eq!(zmq_client.recv_string(0).unwrap().unwrap(), "2");

        zmq_client.send_str("", 0).unwrap();
        assert_eq!(zmq_client.recv_string(0).unwrap().unwrap(), "3");

        zmq_client.send_str("exit", 0).unwrap();
    }

}
