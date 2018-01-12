extern crate zmq;
extern crate pub_sub;

use opq::{TriggerMessage};
use protobuf::parse_from_bytes;

pub struct ZmqReader{
    recv_soc : zmq::Socket,
    pub_chan : pub_sub::PubSub<TriggerMessage>,
}

impl ZmqReader {
    pub fn new(pub_chan : pub_sub::PubSub<TriggerMessage>, ctx : &zmq::Context) -> ZmqReader {
        let reader = ZmqReader{
            pub_chan : pub_chan,
            recv_soc : ctx.socket(zmq::SUB).unwrap()
        };
        reader.recv_soc.connect("tcp://127.0.0.1:9881").unwrap();
        reader.recv_soc.set_subscribe(&[]).unwrap();
        reader
    }

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


