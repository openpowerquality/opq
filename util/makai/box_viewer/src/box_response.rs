use zmq;
use protobuf::{parse_from_bytes,ProtobufError};
use crate::proto::opqbox3::{Response, Response_oneof_response};
use crate::config::Settings;


pub struct BoxResponse{
    acq_broker : zmq::Socket,
}

impl BoxResponse {
    pub fn new(config : &Settings, ctx: &zmq::Context) -> BoxResponse{
        let rsp = BoxResponse{
            acq_broker: ctx.socket(zmq::SUB).unwrap(),
        };
        rsp.acq_broker.connect(&config.zmq_data_endpoint).unwrap();
        rsp.acq_broker.set_subscribe(config.identity.clone().unwrap().as_bytes()).unwrap();
        rsp
    }

    pub fn run_loop(&mut self){
        loop{
            let parts = self.acq_broker.recv_multipart(0).unwrap();
            if parts.len() < 2{
                continue;
            }
            let response_result : Result<Response, ProtobufError> = parse_from_bytes(&parts[1]);
            if let Err(_) = response_result {
                continue
            };
            let response = response_result.unwrap();
            print!("{:#?}", response);
        }
    }
}

