use config::{Config, WINDOWS_PER_MEASUREMENT};
use crossbeam_channel::Receiver;
use opqbox3::Measurement;
use protobuf::Message;
use std::collections::HashMap;
use std::sync::Arc;
use std::thread;
use std::time::UNIX_EPOCH;
use types::Window;
use zmq::{Context, Socket, PUB, SNDMORE};

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
                .insert(name.to_string(), stat.get_average());
            measurement
                .metrics
                .insert(format!("{}_min", name), stat.min);
            measurement
                .metrics
                .insert(format!("{}_max", name), stat.max);
        }
    }
}

fn create_pub_socket(ctx: &Context, config: &Arc<Config>) -> Socket {
    let sub = ctx.socket(PUB).unwrap();

    sub.set_curve_serverkey(&config.settings.server_public_key)
        .unwrap();

    sub.set_curve_publickey(&config.settings.box_public_key)
        .unwrap();
    sub.set_curve_secretkey(&config.settings.box_secret_key)
        .unwrap();
    sub.connect(&config.settings.cmd_sub_ep).unwrap();
    sub
}

pub fn run_filter(rx: Receiver<Window>, config: Arc<Config>) -> thread::JoinHandle<()> {
    thread::spawn(move || {
        let mut db = MeasurementDB::new();
        let ctx = Context::default();
        let tx = create_pub_socket(&ctx, &config);
        loop {
            let windows_per_measurement = config
                .get_state(&WINDOWS_PER_MEASUREMENT.to_string())
                .unwrap() as usize;
            let window = rx.recv().unwrap();
            db.process_window(&window);
            if db.window_count >= windows_per_measurement {
                let mut measurement = Measurement::new();
                db.generate_window(&mut measurement);
                measurement.box_id = config.settings.box_id;
                let since_the_epoch = window.time_stamp_ms.duration_since(UNIX_EPOCH).unwrap();
                measurement.timestamp_ms = since_the_epoch.as_secs() * 1000
                    + since_the_epoch.subsec_nanos() as u64 / 1_000_000;
                db.reset();
                tx.send(
                    format!("{:004}", config.settings.box_id).as_bytes(),
                    SNDMORE,
                ).unwrap();
                tx.send(&measurement.write_to_bytes().unwrap(), 0).unwrap();
            }
        }
    })
}
