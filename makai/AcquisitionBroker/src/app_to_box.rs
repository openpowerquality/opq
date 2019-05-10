use protobuf::{ProtobufError, parse_from_bytes};
use protobuf::core::Message;
use crate::Settings;
use crate::proto::opqbox3::Command;
use crate::constants::ID_MAP;
use std::time::Instant;
use std::sync::Arc;

pub fn app_to_box(ctx: Arc<zmq::Context>, settings : Settings){
    let pub_sock = ctx.socket(zmq::PUB).unwrap();
    pub_sock.set_curve_server(true).unwrap();
    pub_sock.set_curve_secretkey(&settings.sec_key.unwrap()).unwrap();
    pub_sock.set_curve_publickey(&settings.pub_key.unwrap()).unwrap();
    pub_sock.bind(&settings.box_pub).unwrap();

    let pull_sock = ctx.socket(zmq::PULL).unwrap();
    pull_sock.bind(&settings.backend_pull).unwrap();

    let mut sequence = 0;

    loop{
        let mut msg = zmq::Message::new().unwrap();
        pull_sock.recv(&mut msg, 0).unwrap();
        let message_result: Result<Command, ProtobufError> = parse_from_bytes(&*msg);
        let mut message = match message_result{
            Ok(m) => {m},
            Err(e) => {println!("{}", e); continue;},
        };
        message.seq = sequence;
        let mut lock = ID_MAP.lock().unwrap();
        lock.id_map.insert(sequence, (message.identity.clone(), Instant::now()));
        println!("New command from identity {} to box {}, sequence {}.", message.identity, message.box_id, message.seq);
        let box_id = message.box_id.to_string();
        let msg_text = message.write_to_bytes().unwrap();
        let msg = vec![box_id.as_bytes(), &msg_text];
        lock.sent += msg_text.len();
        pub_sock.send_multipart(&msg, 0).unwrap();

        sequence += 1;
    }
}