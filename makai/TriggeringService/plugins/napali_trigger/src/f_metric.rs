use metric_buffer::MetricBuffer;
use std::collections::HashMap;
use std::sync::Arc;
use triggering_service::proto::opqbox3::Measurement;
use types::{BoxMetric, MetricStatus, NapaliPluginSettings, ThresholdLimit};

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
    fn new_metric(&mut self, measurement: Arc<Measurement>) -> MetricStatus {
        use MetricStatus::*;
        if !measurement.metrics.contains_key(F_KEY) {
            return Empty;
        }
        let metric = measurement.metrics.get(F_KEY).unwrap();
        let box_id = measurement.box_id;
        let alpha = self.alpha;
        self
            .boxes
            .entry(box_id)
            .or_insert_with(|| MetricBuffer::new(alpha))
            .add_measurement(metric.average, metric.min, metric.max);

        if metric.max > self.limit.max || metric.min < self.limit.min {
                AboveThreshold
        } else {
            self.boxes.get(&box_id).unwrap().is_outside_3std(metric.average, metric.max, Some(metric.min))
        }
    }
}
