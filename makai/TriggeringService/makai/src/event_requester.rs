use protobuf::Message;
use opqapi::protocol::RequestEventMessage;
use zmq;
use overlapping_interval::OverlappingIntervals;
use std::sync::{Arc, Mutex};
use config::Settings;

pub type SyncEventRequester = Arc<Mutex<EventRequester>>;

pub struct EventRequester {
    acq_broker: zmq::Socket,
    requested_intervals: OverlappingIntervals<u64>,
    keep_data_for_ms: u64,
}

impl EventRequester {
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
