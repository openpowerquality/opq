use protobuf::Message;
use crate::proto::opqbox3::Command;
use zmq;
use std::sync::{Arc, Mutex};
use crate::config::Settings;

///A wrapped `EventRequester` type used for passing around threads.
pub type SyncEventRequester = Arc<Mutex<EventRequester>>;

///Object responsible for communication with the acquisition broker.
pub struct EventRequester {
    ///ZMQ socket to the acquisition broker.
    acq_broker: zmq::Socket,
}

impl EventRequester {
    /// Creates a new `EventRequester` form a zmq context and a reference to the settings file.
    pub fn new(ctx: &zmq::Context, settings: &Settings) -> EventRequester {
        let ret = EventRequester {
            acq_broker: ctx.socket(zmq::PUSH).unwrap(),
        };
        ret.acq_broker
            .connect(&settings.zmq_acquisition_endpoint)
            .unwrap();
        ret
    }

    /// Sends a request for an event to the acquisition broker.
    pub fn trigger(&mut self, request: &Command) {
        let serialized = request.write_to_bytes().unwrap();
        self.acq_broker.send(&serialized, 0).unwrap();
    }
}
