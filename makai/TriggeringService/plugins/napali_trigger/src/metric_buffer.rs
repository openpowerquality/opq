use arraydeque::{ArrayDeque, Wrapping};
use crate::types::MetricStatus;

#[derive(Debug)]
struct MetricUnitaryBuffer {
    pub history: ArrayDeque<[f64; 32], Wrapping>,
    pub last: f64,
    pub mean: f64,
    pub mean_sq: f64,
    pub alpha: f64,
}

impl MetricUnitaryBuffer {
    pub fn new(alpha: f64) -> MetricUnitaryBuffer {
        MetricUnitaryBuffer {
            history: ArrayDeque::new(),
            mean: 0.0,
            mean_sq: 0.0,
            last: 0.0,
            alpha,
        }
    }

    pub fn add_measurement(&mut self, new: f64) {
        if self.history.len() == 0 {
            self.mean = new;
            self.mean_sq = new*new;
        } else {
            self.mean = (1.0 - self.alpha) * self.mean + self.alpha * new;
            self.mean_sq = (1.0 - self.alpha) * self.mean_sq + self.alpha * new*new;
        }
        self.history.push_back(new);
        self.last = new;
    }

    pub fn std_dev(&self) -> f64 {
        let var = (self.mean_sq - self.mean.powi(2)).abs();
        var.sqrt()
    }
}

#[derive(Debug)]
pub struct MetricBuffer{
    min : MetricUnitaryBuffer,
    max : MetricUnitaryBuffer,
    mean : MetricUnitaryBuffer,
}

impl MetricBuffer {
    pub fn new(alpha: f32) -> MetricBuffer{
        MetricBuffer{
            min : MetricUnitaryBuffer::new(alpha as f64),
            max : MetricUnitaryBuffer::new(alpha as f64),
            mean : MetricUnitaryBuffer::new(alpha as f64),
        }
    }

    pub fn add_measurement(&mut self, mean: f32, min : f32, max : f32) {
        self.mean.add_measurement(mean as f64);
        self.min.add_measurement(min as f64);
        self.max.add_measurement(max as f64);

    }

    pub fn is_outside_3std(&self, mean : f32, max : f32, min : Option<f32>) -> MetricStatus{
        use MetricStatus::*;
        if (max as f64 - self.max.mean) > 3.0*self.max.std_dev(){
            //println!("max {} {} ", max as f64 - self.max.mean, self.max.std_dev());
            Outside3STD
        } else if (self.mean.mean - mean as f64).abs() > 3.0*self.mean.std_dev() {
            //println!("mean {} {} ", mean - self.mean.mean, self.mean.std_dev());
            Outside3STD
        } else {
            if let Some(min) = min {
                if (self.min.mean - min as f64) > 3.0 * self.min.std_dev() {
              //      println!("min {} {} ", min - self.min.mean, self.min.std_dev());
                    Outside3STD
                }
                else{
                    BelowThreshold
                }
            } else{
                BelowThreshold
            }

        }
    }
}