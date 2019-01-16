use protobuf::Message;
use crate::proto::makai::RequestEventMessage;
use zmq;
use crate::overlapping_interval::OverlappingIntervals;
use std::sync::{Arc, Mutex};
use crate::config::Settings;

///A wrapped `EventRequester` type used for passing around threads.
pub type SyncEventRequester = Arc<Mutex<EventRequester>>;

///Object responsible for communication with the acquisition broker.
pub struct EventRequester {
    ///ZMQ socket to the acquisition broker.
    acq_broker: zmq::Socket,
    ///Overlapping intervals to prevent double requests for raw measurements.
    requested_intervals: OverlappingIntervals<u64>,
    ///How long the overlapping intervals keeps event information.
    keep_data_for_ms: u64,
}

impl EventRequester {
    /// Creates a new `EventRequester` form a zmq context and a reference to the settings file.
    pub fn new(ctx: &zmq::Context, settings: &Settings) -> EventRequester {
        let ret = EventRequester {
            acq_broker: ctx.socket(zmq::PUSH).unwrap(),
            requested_intervals: OverlappingIntervals::new(),
            keep_data_for_ms: settings.event_request_expiration_window_ms,
        };
        ret.acq_broker
            .connect(&settings.zmq_acquisition_endpoint)
            .unwrap();
        ret
    }

    /// Sends a request for an event to the acquisition broker.
    pub fn trigger(&mut self, mut request: RequestEventMessage) {
        let start = request.get_start_timestamp_ms_utc();
        let end = request.get_end_timestamp_ms_utc();
        if self.requested_intervals.insert_and_check(start, end) {
            request.set_request_data(true);
        } else {
            request.set_request_data(false)
        }
        self.requested_intervals
            .clear_to(start - self.keep_data_for_ms);
        let serialized = request.write_to_bytes().unwrap();
        self.acq_broker.send(&serialized, 0).unwrap();
    }
}
