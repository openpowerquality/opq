use metric_buffer::MetricBuffer;
use std::collections::HashMap;
use std::sync::Arc;
use triggering_service::proto::opqbox3::Measurement;
use types::{BoxMetric, MetricResult, MetricStatus, NapaliPluginSettings, ThresholdLimit};

static F_KEY: &'static str = "f";

#[derive(Debug)]
pub struct FMetric {
    boxes: HashMap<u32, MetricBuffer>,
    limit: ThresholdLimit,
    alpha: f32,
}

impl FMetric {
    pub fn new(set: &NapaliPluginSettings) -> FMetric {
        FMetric {
            boxes: HashMap::new(),
            limit: ThresholdLimit {
                min: set.f_min,
                max: set.f_max,
            },
            alpha: set.alpha,
        }
    }
}

impl BoxMetric for FMetric {
    fn new_metric(&mut self, measurement: Arc<Measurement>) -> MetricResult {
        if !measurement.metrics.contains_key(F_KEY) {
            return MetricResult {
                status: MetricStatus::Empty,
                derivative: 0.0,
            };
        }
        let metric = measurement.metrics.get(F_KEY).unwrap();
        let box_id = measurement.box_id;
        let alpha = self.alpha;
        let derivative = self
            .boxes
            .entry(box_id)
            .or_insert_with(|| MetricBuffer::new(alpha))
            .add_measurement(metric.average);

        let mean = self.boxes.get(&box_id).unwrap().mean;
        let std = self.boxes.get(&box_id).unwrap().std_dev();
        println!("{:?}, {:?}", mean, std);
        if metric.max > self.limit.max || metric.min < self.limit.min {
            MetricResult {
                status: MetricStatus::AboveThreshold,
                derivative,
            }
        } else if (metric.max - mean).abs() > std * 3.0 {
            MetricResult {
                status: MetricStatus::Outside3STD,
                derivative,
            }
        } else if (mean - metric.min).abs() > std * 3.0 {
            MetricResult {
                status: MetricStatus::Outside3STD,
                derivative,
            }
        } else {
            MetricResult {
                status: MetricStatus::BelowThreshold,
                derivative,
            }
        }
    }
}
