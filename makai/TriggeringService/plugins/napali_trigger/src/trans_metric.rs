use metric_buffer::MetricBuffer;
use std::collections::HashMap;
use std::sync::Arc;
use triggering_service::proto::opqbox3::Measurement;
use types::{BoxMetric, MetricResult, MetricStatus, NapaliPluginSettings};

static TRANS_KEY: &'static str = "trans";

pub struct TransMetric {
    boxes: HashMap<u32, MetricBuffer>,
    limit: f32,
    alpha: f32,
}

impl TransMetric {
    pub fn new(set: &NapaliPluginSettings) -> TransMetric {
        TransMetric {
            boxes: HashMap::new(),
            limit: set.trans_max,
            alpha: set.alpha,
        }
    }
}

impl BoxMetric for TransMetric {
    fn new_metric(&mut self, measurement: Arc<Measurement>) -> MetricResult {
        if !measurement.metrics.contains_key(TRANS_KEY) {
            return MetricResult {
                status: MetricStatus::Empty,
                derivative: 0.0,
            };
        }
        let metric = measurement.metrics.get(TRANS_KEY).unwrap();
        let box_id = measurement.box_id;
        let alpha = self.alpha;
        let derivative = self
            .boxes
            .entry(box_id)
            .or_insert_with(|| MetricBuffer::new(alpha))
            .add_measurement(metric.average);

        let mean = self.boxes.get(&box_id).unwrap().mean;
        let std = self.boxes.get(&box_id).unwrap().std_dev();

        if metric.max.abs() > self.limit {
            MetricResult {
                status: MetricStatus::AboveThreshold,
                derivative,
            }
        } else if (metric.max.abs() - mean).abs() > std * 3.0 {
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
