use std::collections::HashMap;
use std::fs::create_dir;
use std::fs::File;

use crate::scraper::DataPoint;
use std::io::Write;
use std::path::Path;

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

pub fn store_data_points(base_path: &Path, data: Vec<DataPoint>) {
    let data_dir = base_path.join(Path::new(&data[0].meter_name));
    let out_path = data_dir.join(&data[0].sample_type);
    std::fs::create_dir_all(data_dir).unwrap();
    let sample_points: Vec<String> = data
        .iter()
        .map(|point| {
            format!(
                "{} {} {} {} {} {}\n",
                point.ts_s, point.actual, point.min, point.max, point.avg, point.stddev,
            )
        })
        .collect();
    let mut out_file = File::create(out_path).unwrap();
    for sample_point in sample_points {
        out_file.write(sample_point.as_bytes()).unwrap();
    }

    //    for point in data {
    //        out_file.write(point).unwrap();
    //    }
}
