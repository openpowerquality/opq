use metric_buffer::MetricBuffer;
use std::collections::HashMap;
use std::sync::Arc;
use triggering_service::proto::opqbox3::Measurement;
use types::{BoxMetric, MetricStatus, NapaliPluginSettings, ThresholdLimit};

static RMS_KEY: &'static str = "rms";

pub struct RmsMetric {
    boxes: HashMap<u32, MetricBuffer>,
    limit: ThresholdLimit,
    alpha: f32,
}

impl RmsMetric {
    pub fn new(set: &NapaliPluginSettings) -> RmsMetric {
        RmsMetric {
            boxes: HashMap::new(),
            limit: ThresholdLimit {
                min: set.rms_min,
                max: set.rms_max,
            },
            alpha: set.alpha,
        }
    }
}

impl BoxMetric for RmsMetric {
    fn new_metric(&mut self, measurement: Arc<Measurement>) -> MetricStatus {
        use MetricStatus::*;
        if !measurement.metrics.contains_key(RMS_KEY) {
            return Empty;
        }
        let metric = measurement.metrics.get(RMS_KEY).unwrap();
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
