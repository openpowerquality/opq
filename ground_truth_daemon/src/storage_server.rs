use std::collections::HashMap;
use std::fs::create_dir;
use std::fs::File;

use crate::scraper::DataPoint;
use std::io::Write;

#[derive(Default)]
struct SampleTypes {
    output: HashMap<String, File>,
}

impl SampleTypes {
    fn write(&mut self, point: DataPoint) {
        self.output
            .get_mut(&point.sample_type)
            .unwrap()
            .write(
                format! {"{} {} {} {} {} {}\n",
                    point.ts_s,
                    point.actual,
                    point.min,
                    point.max,
                    point.avg,
                    point.stddev,
                }
                .as_bytes(),
            )
            .unwrap();
    }
}

pub struct StorageService {
    files: HashMap<String, SampleTypes>,
    path: String,
}

impl StorageService {
    pub fn new(path: String) -> StorageService {
        StorageService {
            files: HashMap::new(),
            path,
        }
    }

    pub fn store_datapoint(&mut self, data: Vec<DataPoint>) {
        for point in data {
            if !self.files.contains_key(&point.meter_name) {
                create_dir(self.path.clone() + "/" + &point.meter_name);
                self.files
                    .insert(point.meter_name.clone(), SampleTypes::default());
            }
            if !self
                .files
                .get(&point.meter_name)
                .unwrap()
                .output
                .contains_key(&point.sample_type)
            {
                let fout = File::create(
                    self.path.clone() + "/" + &point.meter_name + "/" + &point.sample_type,
                )
                .unwrap();
                self.files
                    .get_mut(&point.meter_name)
                    .unwrap()
                    .output
                    .insert(point.sample_type.clone(), fout);
            }
            self.files.get_mut(&point.meter_name).unwrap().write(point);
        }
    }
}
