extern crate zmq;
extern crate pub_sub;

use protobuf::parse_from_bytes;
use opq::{TriggerMessage};
use constants::TRIGGERING_ZMQ_ENDPOINT;

/// This object is responsible for receiving triggering messages from the makai triggering broker.
pub struct ZmqReader{
    ///ZMQ socket.
    recv_soc : zmq::Socket,
    ///Pub-Sub object for distributing triggering messages internally.
    pub_chan : pub_sub::PubSub<TriggerMessage>,
}

impl ZmqReader {
    ///Creates a new ZMQ reader.
    /// # Arguments
    /// * `pub_chan` - an internal publish channel for the triggering messages.
    /// * `ctx` - shared ZMQ context.
    pub fn new(pub_chan : pub_sub::PubSub<TriggerMessage>, ctx : &zmq::Context) -> ZmqReader {
        let reader = ZmqReader{
            pub_chan,
            recv_soc : ctx.socket(zmq::SUB).unwrap()
        };
        reader.recv_soc.connect(TRIGGERING_ZMQ_ENDPOINT).unwrap();
        reader.recv_soc.set_subscribe(&[]).unwrap();
        reader
    }

    ///The main loop for receiving triggering messages.
    pub fn run_loop(&self){
        loop{
            let msg = self.recv_soc.recv_multipart(0).unwrap();
            if msg.len() < 2{
                println!("Message contains {} parts!", msg.len());
                continue;
            }
            let trigger_message = parse_from_bytes::<TriggerMessage>(&msg[1]).unwrap();
            self.pub_chan.send(trigger_message).unwrap();
        };
    }
}


