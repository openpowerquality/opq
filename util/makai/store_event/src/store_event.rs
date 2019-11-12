use mongodb::ClientInner;
use mongodb::ThreadedClient;
use mongodb::db::ThreadedDatabase;
use std::sync::Arc;

use crate::error_type::StoreError;

pub fn store_event(event_num : u32, path : String, client : Arc<ClientInner>)->Result<(), StoreError>{
    let db = client.db("opq");
    let ev_col = db.collection("events");
    let ev = match ev_col.find_one(
        Some(doc!{ "event_id": event_num }),
        None
    ){
        Ok(ev) => ev,
        Err(e) => return Err(StoreError::NoSuchEvent{
          id : event_num
        })
    };
    println!("{:?}", ev);


    Ok(())
}