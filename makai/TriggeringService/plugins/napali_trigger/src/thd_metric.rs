use metric_buffer::MetricBuffer;
use std::collections::HashMap;
use std::sync::Arc;
use triggering_service::proto::opqbox3::Measurement;
use types::{BoxMetric, MetricStatus, NapaliPluginSettings};

static THD_KEY: &'static str = "thd";

pub struct THDMetric {
    boxes: HashMap<u32, MetricBuffer>,
    limit: f32,
    alpha: f32,
}

impl THDMetric {
    pub fn new(set: &NapaliPluginSettings) -> THDMetric {
        THDMetric {
            boxes: HashMap::new(),
            limit: set.thd_max,
            alpha: set.alpha,
        }
    }
}

impl BoxMetric for THDMetric {
    fn new_metric(&mut self, measurement: Arc<Measurement>) -> MetricStatus {
        use MetricStatus::*;
        if !measurement.metrics.contains_key(THD_KEY) {
            return MetricStatus::Empty
        }
        let metric = measurement.metrics.get(THD_KEY).unwrap();
        let box_id = measurement.box_id;
        let alpha = self.alpha;
        self
            .boxes
            .entry(box_id)
            .or_insert_with(|| MetricBuffer::new(alpha))
            .add_measurement(metric.average, metric.min, metric.max);

        if metric.max > self.limit {
            AboveThreshold
        } else {
            self.boxes.get(&box_id).unwrap().is_outside_3std(metric.average, metric.max, None)
        }
    }
}
