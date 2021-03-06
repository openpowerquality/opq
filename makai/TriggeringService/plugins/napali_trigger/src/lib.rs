#[macro_use]
extern crate triggering_service;
extern crate arraydeque;
use std::str;
use std::sync::Arc;
use triggering_service::makai_plugin::MakaiPlugin;
use triggering_service::proto::opqbox3::{Command, GetDataCommand, Command_oneof_command};
use triggering_service::proto::opqbox3::Measurement;

#[macro_use]
extern crate serde_derive;
extern crate serde;
extern crate serde_json;

mod f_metric;
mod metric_buffer;
mod rms_metric;
mod thd_metric;
mod trans_metric;
mod types;
mod vector_buffer;


use types::*;
use vector_buffer::VectorBuffer;
use ::TriggeringState::Triggering;


#[derive(Debug)]
enum TriggeringState {
    Idle(u64),
    Triggering(u64),
}


pub struct NapaliPlugin {
    settings: NapaliPluginSettings,
    history: VectorBuffer,
    state: TriggeringState,

    rms: Option<rms_metric::RmsMetric>,
    thd: Option<thd_metric::THDMetric>,
    trans: Option<trans_metric::TransMetric>,
    f: Option<f_metric::FMetric>,
}

impl NapaliPlugin {
    fn new() -> NapaliPlugin {
        NapaliPlugin {
            settings: NapaliPluginSettings::default(),
            history: VectorBuffer::default(),
            state: TriggeringState::Idle(timestamp()),
            rms: None,
            thd: None,
            trans: None,
            f: None,
        }
    }
}

impl MakaiPlugin for NapaliPlugin {
    fn name(&self) -> &'static str {
        "Napali Plugin"
    }

    fn process_measurement(&mut self, msg: Arc<Measurement>) -> Option<Vec<Command>> {
        let f_res = self.f.as_mut().unwrap().new_metric(msg.clone());
        let rms_res = self.rms.as_mut().unwrap().new_metric(msg.clone());
        let thd_res = self.thd.as_mut().unwrap().new_metric(msg.clone());
        let trans_res = self.trans.as_mut().unwrap().new_metric(msg.clone());
        let status = vec![
            f_res,
            rms_res,
            thd_res,
            trans_res
        ]
            .iter()
            .max()
            .unwrap()
            .clone();
        let id = msg.box_id;
        let ts = msg.timestamp_ms;
        let vector = MetricVector { status, id, ts };

        let new_state = match self.state{
            TriggeringState::Idle(_) => {
                if vector.status == MetricStatus::AboveThreshold{
                    self.history.insert(vector.clone());
                    TriggeringState::Triggering(vector.ts)
                }
                else{
                    TriggeringState::Idle(vector.ts)
                }
            },
            Triggering(last_ts) => {
                if vector.status == MetricStatus::AboveThreshold{
                    self.history.insert(vector.clone());
                    TriggeringState::Triggering(vector.ts)
                }
                else {
                    if vector.status == MetricStatus::Outside3STD{
                        self.history.insert(vector.clone());
                    }
                    if last_ts + self.settings.grace_time_ms > vector.ts {
                        TriggeringState::Triggering(last_ts)
                    }
                    else {
                        TriggeringState::Idle(vector.ts)
                    }
                }
            },
        };

        let mut ret = None;
        if let TriggeringState::Triggering(_t) = self.state{
            if let TriggeringState::Idle(_t) = new_state{
                //list of boxen
                let trg_lst = self.history.get_trigger_list();
                //command payload
                let mut payload = <GetDataCommand>::new();
                payload.start_ms = self.history.start - 500;
                payload.end_ms = self.history.end - 500;
                payload.wait = false;
                //command list to devices.
                let mut cmd_lst = vec![];
                for box_id in trg_lst.iter(){
                    let mut cmd = Command::new();
                    cmd.box_id = *box_id as i32;
                    cmd.timestamp_ms = timestamp();
                    cmd.command = Some(Command_oneof_command::data_command(payload.clone()));
                    cmd_lst.push(cmd);
                }

                //clear the event buffer
                self.history.clear();

                //check if its a local or global event.
                if cmd_lst.len() != 1 || (self.settings.trigger_local != false){
                    ret = Some(cmd_lst);
                }
            }
        }
        self.state = new_state;

        if self.settings.debug == true{
            println!("{:?} : {:?}, {:?}, {:?}, {:?}", self.state, f_res, rms_res, thd_res, trans_res);
        }
        ret
    }

    fn on_plugin_load(&mut self, args: String) {
        let set = serde_json::from_str(&args);
        self.settings = match set {
            Ok(s) => s,
            Err(e) => {
                println!("Bad setting file for plugin {}: {:?}", self.name(), e);
                NapaliPluginSettings::default()
            }
        };
        self.rms = Some(rms_metric::RmsMetric::new(&self.settings));
        self.f = Some(f_metric::FMetric::new(&self.settings));
        self.thd = Some(thd_metric::THDMetric::new(&self.settings));
        self.trans = Some(trans_metric::TransMetric::new(&self.settings));
    }

    fn on_plugin_unload(&mut self) {
        println!("Napali plugin unloaded.")
    }
}

declare_plugin!(NapaliPlugin, NapaliPlugin::new);

#[cfg(test)]
mod tests {
    // Note this useful idiom: importing names from outer (for mod tests) scope.
    use super::*;
    extern crate rand;

    extern crate itertools;
    use tests::rand::Rng;
    use self::itertools::izip;
    use std::fs::File;
    use std::io::{BufReader, BufRead};
    use std::path::PathBuf;

    fn gen_napali(local : bool) -> NapaliPlugin{
        let mut plg = NapaliPlugin::new();
        let settings = NapaliPluginSettings{
            alpha: 0.001,
            f_min: 59.9,
            f_max: 60.1,
            rms_min: 115.0,
            rms_max: 125.0,
            thd_max: 5.0,
            trans_max: 7.0,
            grace_time_ms: 5000,
            trigger_local: local,
            debug : false
        };
        plg.on_plugin_load(serde_json::to_string(&settings).unwrap());
        plg
    }

    fn gen_good_f(ts : u64, id: u32) -> Measurement{
        let mut m = Measurement::new();
        m.timestamp_ms = ts;
        m.box_id = id;
        let mut rng = rand::thread_rng();

        let mut me  = triggering_service::proto::opqbox3::Metric::new();
        me.min = 59.99 + rng.gen_range(-0.01, 0.01);
        me.max = 60.01 +rng.gen_range(-0.01, 0.01);
        me.average = 60.00 + rng.gen_range(-0.01, 0.01);
        m.metrics.insert("f".to_string(), me);
        m
    }

    fn gen_bad_f(ts : u64, id: u32) -> Measurement{
        let mut m = Measurement::new();
        m.timestamp_ms = ts;
        m.box_id = id;

        let mut me  = triggering_service::proto::opqbox3::Metric::new();
        me.min = 59.6;
        me.max = 59.9;
        me.average = 59.7;
        print!("{}, ", me.average);
        m.metrics.insert("f".to_string(), me);
        m
    }

   // #[test]
    fn test_single() {

        let mut napali = gen_napali(true);
        for i in 0..2000{
            napali.process_measurement(Arc::new(gen_good_f(1000*i, 1)));
        }
        for i in 2000..2020{
            napali.process_measurement(Arc::new(gen_good_f(1000*i, 1)));
        }
        let mut i = 2020;
        napali.process_measurement(Arc::new(gen_bad_f(1000*i, 1)));
        i+=1;
        napali.process_measurement(Arc::new(gen_bad_f(1000*i, 1)));

        for i in i+1..i+1+70{
            napali.process_measurement(Arc::new(gen_good_f(1000*i, 1)));

        }
    }

    fn split(s : &String) -> (f32,f32){
        let mut split = s.trim().split(",").collect::<Vec<&str>>();
        let t : f32 = split[0].parse().unwrap();
        let v : f32 = split[1].parse().unwrap();
        (t, v)
    }

    #[test]
    fn test_from_device(){
        let mut napali = gen_napali(true);
        let mut d = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
        d.push("test_data");
        let mut f = BufReader::new(File::open("./test_data/f_filtered").unwrap());
        let mut t = BufReader::new(File::open("./test_data/t_filtered").unwrap());
        let mut v = BufReader::new(File::open("./test_data/v_filtered").unwrap());
        let box_id = 666;
        for (fs, ts, vs) in izip!(f.lines(), t.lines(), v.lines()){
            let mut m = Measurement::new();
            let (t, fv) = split(&fs.unwrap());
            let (_, tv) = split(&ts.unwrap());
            let (_, vv) = split(&vs.unwrap());
            let mut rng = rand::thread_rng();
            let mut m = Measurement::new();
            m.timestamp_ms = (t*1000.0) as u64;
            m.box_id = box_id;
            let mut me  = triggering_service::proto::opqbox3::Metric::new();
            me.min = fv - 0.01;
            me.max = fv + 0.01;
            me.average = fv;
            m.metrics.insert("f".to_string(), me);

            let mut me  = triggering_service::proto::opqbox3::Metric::new();
            me.min = tv - 0.01;
            me.max = tv + 0.01;
            me.average = tv;
            m.metrics.insert("thd".to_string(), me);
            let mut me  = triggering_service::proto::opqbox3::Metric::new();
            me.min = vv - 1.0;
            me.max = vv + 1.0;
            me.average = vv;
            m.metrics.insert("rms".to_string(), me);
            napali.process_measurement(Arc::new(m));
        }

    }

}