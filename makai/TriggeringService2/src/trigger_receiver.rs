use zmq;
use pub_sub::PubSub;
//use protobuf;
use std::sync::Arc;
use protobuf::{parse_from_bytes,ProtobufError};
use crate::proto::opqbox3::Measurement;
use crate::config::Settings;

/// This object is responsible for receiving triggering messages from the makai triggering broker.
pub struct TriggerReceiver {
    ///ZMQ socket.
    trg_broker: zmq::Socket,
    ///Pub-Sub object for distributing triggering messages internally.
    pub_chan: PubSub<Arc<Measurement>>,
}

impl TriggerReceiver {
    ///Creates a new ZMQ receiver for trigger messages..
    /// # Arguments
    /// * `pub_chan` - an internal publish channel for the triggering messages.
    /// * `ctx` - shared ZMQ context.
    pub fn new(
        pub_chan: PubSub<Arc<Measurement>>,
        ctx: &zmq::Context,
        config: &Settings,
    ) -> TriggerReceiver {
        let reciever = TriggerReceiver {
            pub_chan: pub_chan,
            trg_broker: ctx.socket(zmq::SUB).unwrap(),
        };
        reciever
            .trg_broker
            .connect(&config.zmq_trigger_endpoint)
            .unwrap();
        reciever.trg_broker.set_subscribe(&[]).unwrap();
        reciever
    }

    ///The main loop for receiving triggering messages.
    pub fn run_loop(&self) {
        loop {
            let msg = self.trg_broker.recv_multipart(0).unwrap();
            if msg.len() < 2 {
                println!("Message contains {} parts!", msg.len());
                continue;
            }
            let msg: Result<Measurement, ProtobufError> = parse_from_bytes(&msg[1]);

            match msg {
                Ok(msg) => {

                    let trigger_message = Arc::new(msg);
                    self.pub_chan.send(trigger_message).unwrap();
                }
                Err(_) => continue,
            }
        }
    }
}
