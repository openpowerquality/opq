use protobuf::{ProtobufError, parse_from_bytes};
use std::time::Instant;
use std::sync::Arc;

use crate::Settings;
use crate::proto::opqbox3::Response;
use crate::constants::ID_MAP;
use crate::mongo_debug_metric::MongoStorageService;

pub fn box_to_app(ctx: Arc<zmq::Context>, settings : Settings){
    let debug_metric = MongoStorageService::new(&settings);
    let pull_sock = ctx.socket(zmq::PULL).unwrap();
    pull_sock.set_curve_server(true).unwrap();
    pull_sock.set_curve_secretkey(&settings.sec_key.unwrap()).unwrap();
    pull_sock.set_curve_publickey(&settings.pub_key.unwrap()).unwrap();
    pull_sock.bind(&settings.box_pull).unwrap();

    let pub_sock = ctx.socket(zmq::PUB).unwrap();
    pub_sock.bind(&settings.backend_pub).unwrap();

    loop{
        let mut parts = pull_sock.recv_multipart(0).unwrap();
        let message_result: Result<Response, ProtobufError> = parse_from_bytes(&parts[0]);
        let message = match message_result{
            Ok(m) => {m},
            Err(e) => {println!("{}", e); continue;},
        };
        let sequence = message.seq;
        let mut lock = ID_MAP.lock().unwrap();

        if settings.metric_update_sec > 0{
            lock.recv = 0;
            for i in 0..parts.len(){
                lock.recv += parts[i].len();
            }
            if lock.last_sent.elapsed().as_secs() > settings.metric_update_sec{
                debug_metric.store_metric_in_db(lock.sent as u32, lock.recv as u32);
                lock.recv = 0;
                lock.sent = 0;
                lock.last_sent = Instant::now();
            }
        }
        let identity = lock.id_map.remove(&sequence);
        let identity = match identity{
            None => {continue;},
            Some((s,_)) => {s.clone()},
        };
        println!("New responce from box {}, to identity {}.", message.box_id, identity);
        parts.insert(0, identity.as_bytes().to_vec());
        let fing_slices : Vec<&[u8]> = parts.iter().map(|x| x.as_slice()).collect();

        pub_sock.send_multipart(&fing_slices, 0).unwrap();
    }
}