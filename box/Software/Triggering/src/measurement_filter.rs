use config::{State, WINDOWS_PER_MEASUREMENT};
use crossbeam_channel::Receiver;
use box_api::opqbox3::{Measurement, Metric};
use protobuf::Message;
use std::collections::HashMap;
use std::sync::Arc;
use std::thread;
use box_api::types::Window;
use window_db::WindowDB;
use zmq::{Context, Socket, PUB, SNDMORE};
use util::unix_timestamp;
use std::string::ToString;
use crate::sse::Server;

struct MeasurementStat {
    pub min: f32,
    pub max: f32,
    ave_acc: f32,
    count: usize,
}

impl MeasurementStat {
    pub fn append(&mut self, val: f32) {
        self.ave_acc += val;
        self.count += 1;
        if self.min > val {
            self.min = val;
        }
        if self.max < val {
            self.max = val;
        }
    }

    pub fn new(val: f32) -> MeasurementStat {
        MeasurementStat {
            min: val,
            max: val,
            ave_acc: val,
            count: 1,
        }
    }

    pub fn get_average(&self) -> f32 {
        self.ave_acc / (self.count as f32)
    }

    pub fn get_metric(&self) -> Metric {
        let mut metric = Metric::new();
        metric.set_min(self.min);
        metric.set_max(self.max);
        metric.set_average(self.get_average());
        metric
    }
}

struct MeasurementDB {
    measurements: HashMap<String, MeasurementStat>,
    pub window_count: usize,
}

impl MeasurementDB {
    pub fn new() -> MeasurementDB {
        MeasurementDB {
            measurements: HashMap::new(),
            window_count: 0,
        }
    }

    pub fn process_window(&mut self, window: &Window) {
        for (name, value) in window.results.iter() {
            if self.measurements.contains_key(name) {
                self.measurements.get_mut(name).unwrap().append(*value);
            } else {
                self.measurements
                    .insert(name.clone(), MeasurementStat::new(*value));
            }
        }
        self.window_count += 1;
    }

    pub fn reset(&mut self) {
        self.measurements.clear();
        self.window_count = 0;
    }

    pub fn generate_window(&self, measurement: &mut Measurement) {
        for (name, stat) in self.measurements.iter() {
            measurement
                .metrics
                .insert(name.to_string(), stat.get_metric());
        }
    }
}

fn create_pub_socket(ctx: &Context, config: &Arc<State>) -> Socket {
    let sub = ctx.socket(PUB).unwrap();

    sub.set_curve_serverkey(&config.settings.server_public_key)
        .unwrap();

    sub.set_curve_publickey(&config.settings.box_public_key.clone().unwrap())
        .unwrap();
    sub.set_curve_secretkey(&config.settings.box_secret_key.clone().unwrap())
        .unwrap();
    sub.connect(&config.settings.trg_push_ep).unwrap();
    sub
}

pub fn run_filter(
    rx: Receiver<Window>,
    state: Arc<State>,
    window_db: Arc<WindowDB>,
) -> thread::JoinHandle<()> {
    thread::spawn(move || {
        let _sse_handle = SSE.spawn(state.settings.sse_interface.clone().parse().unwrap());

        let mut measurement_db = MeasurementDB::new();
        let ctx = Context::default();
        let tx = create_pub_socket(&ctx, &state);
        loop {
            let windows_per_measurement = state
                .get_state(&WINDOWS_PER_MEASUREMENT.to_string())
                .unwrap() as usize;
            let window = rx.recv().unwrap();
            measurement_db.process_window(&window);
            if measurement_db.window_count >= windows_per_measurement {
                let mut measurement = Measurement::new();
                measurement_db.generate_window(&mut measurement);
                measurement.box_id = state.settings.box_id;
                measurement.timestamp_ms = unix_timestamp();
                measurement_db.reset();
                broadcast_measurements(&measurement);
                tx.send(format!("{:004}", state.settings.box_id).as_bytes(), SNDMORE)
                    .unwrap();
                tx.send(&measurement.write_to_bytes().unwrap(), 0).unwrap();
            }
            window_db.add_window(window);

        }
    })
}


//Broadcast measurements:
lazy_static! {
    static ref SSE: Server<u8> = Server::new();
}

#[derive(Debug, Serialize, Deserialize)]
struct SerializableMetric{
    name : String,
    value : f32
}

fn broadcast_measurements(measurement : &Measurement){
    let mut broadcast_str = String::new();
    for (name, metric)  in &measurement.metrics{
        let sm = SerializableMetric{
            name : name.clone(),
            value : metric.average
        };
        broadcast_str += &serde_json::to_string(&sm).unwrap();
    }
    println!("{}", broadcast_str);
    SSE.push(0, "update", &broadcast_str).ok();
}