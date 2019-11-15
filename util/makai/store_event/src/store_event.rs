use crate::error_type::StoreError;
use mongodb::db::ThreadedDatabase;
use mongodb::gridfs::Store;
use mongodb::gridfs::ThreadedStore;
use mongodb::ClientInner;
use mongodb::ThreadedClient;
use std::collections::HashMap;
use std::fs;
use std::fs::File;
use std::io::Read;
use std::io::Write;
use std::sync::Arc;

#[derive(Serialize)]
struct Manifest {
    ev_id: u32,
    start: i64,
    end: i64,
}

pub fn store_event(
    event_num: u32,
    path: String,
    client: Arc<ClientInner>,
) -> Result<(), StoreError> {
    let root_path = path + "/" + &event_num.to_string();
    if let Err(_) = fs::create_dir_all(&root_path) {
        return Err(StoreError::CouldNotCreate { path: root_path });
    }

    let db = client.db("opq");
    let ev_col = db.collection("events");

    let ev = match ev_col.find_one(Some(doc! { "event_id": event_num }), None) {
        Ok(ev) => match ev {
            Some(ev) => ev,
            None => return Err(StoreError::NoSuchEvent { id: event_num }),
        },
        Err(_) => return Err(StoreError::NoSuchEvent { id: event_num }),
    };
    if ev.get_array("boxes_received").unwrap().len() < 1 {
        return Ok(());
    }

    let start = ev.get_i64("target_event_start_timestamp_ms").unwrap();
    let end = ev.get_i64("target_event_end_timestamp_ms").unwrap();

    let man = Manifest {
        ev_id: event_num,
        start,
        end,
    };
    let mut manifest_file = match File::create(root_path.clone() + "/manifest") {
        Ok(file) => file,
        Err(_) => {
            return Err(StoreError::CouldNotCreate {
                path: root_path.clone() + "/manifest",
            })
        }
    };
    manifest_file
        .write(serde_json::to_string(&man).unwrap().as_bytes())
        .unwrap();

    //now for Boxes:
    let mut boxen_to_fs = HashMap::new();

    let col = db.collection("box_events");
    let cursor = col
        .find(
            Some(doc! {
            "event_id" : event_num
            }),
            None,
        )
        .unwrap();

    for result in cursor {
        if let Ok(item) = result {
            let fs_name = item.get_str("data_fs_filename").unwrap().to_string();
            let fs_id = item.get_str("box_id").unwrap().to_string();
            boxen_to_fs.insert(fs_id, fs_name);
        }
    }

    //Now for constants:
    let mut boxen_to_const = HashMap::new();
    let col = db.collection("opq_boxes");
    for (key, _) in &boxen_to_fs {
        let result = col
            .find_one(Some(doc! { "box_id" : key }), None)
            .unwrap()
            .unwrap();
        let cal_const = result.get_f64("calibration_constant").unwrap();
        boxen_to_const.insert(key, cal_const);
    }

    //Now we pull the data:
    let fs = Store::with_db(client.db("opq"));
    for (box_id, fs_path) in &boxen_to_fs {
        let mut file = fs.open(fs_path.to_string()).unwrap();
        let mut bytes = vec![];
        file.read_to_end(&mut bytes).unwrap();

        let data_path = root_path.clone() + "/" + &box_id.to_string() + ".data";
        let mut outfile = File::create(&data_path).unwrap();
        for i in 0..bytes.len() / 2 {
            let mut ipoint: i16 = bytes[i * 2] as i16;
            ipoint |= (bytes[i * 2 + 1] as i16) << 8;
            let fpoint = (ipoint as f64) / boxen_to_const.get(box_id).unwrap();
            outfile.write(format!("{}\n", fpoint).as_bytes()).unwrap();
        }
    }
    //Finally we get the trends:
    let col = db.collection("measurements");
    for (box_id, _) in &boxen_to_fs {
        let cursor = col
            .find(
                Some(doc!(
                    "box_id": box_id,
                    "timestamp_ms": doc!("$gt": start-2000, "$lte": end + 2000)
                )),
                None,
            )
            .unwrap();

        let data_path = root_path.clone() + "/" + &box_id.to_string() + ".trend";
        let mut outfile = File::create(&data_path).unwrap();
        for result in cursor {
            if let Ok(item) = result {
                let ts = item.get_i64("timestamp_ms").unwrap();
                let v = item.get_f64("voltage").unwrap();
                let f = item.get_f64("frequency").unwrap();
                let thd = item.get_f64("thd").unwrap();
                let trans = item.get_f64("transient").unwrap();

                outfile
                    .write(format!("{} {} {} {} {}\n", ts, v, f, thd, trans).as_bytes())
                    .unwrap();
            }
        }
    }

    Ok(())
}
