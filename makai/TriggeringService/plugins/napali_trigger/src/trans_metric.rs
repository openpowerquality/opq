use metric_buffer::MetricBuffer;
use std::collections::HashMap;
use std::sync::Arc;
use triggering_service::proto::opqbox3::Measurement;
use types::{BoxMetric, MetricStatus, NapaliPluginSettings};

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
    fn new_metric(&mut self, measurement: Arc<Measurement>) -> MetricStatus {
        use MetricStatus::*;
        if !measurement.metrics.contains_key(TRANS_KEY) {
            return Empty;

        }
        let metric = measurement.metrics.get(TRANS_KEY).unwrap();
        let box_id = measurement.box_id;
        let alpha = self.alpha;
        self.boxes
            .entry(box_id)
            .or_insert_with(|| MetricBuffer::new(alpha));


        let ret = if metric.max.abs() > self.limit {
            AboveThreshold
        } else {
            self.boxes.get(&box_id).unwrap().is_outside_3std(metric.average, metric.max, None)
        };
        self.boxes.entry(box_id).or_insert_with(|| MetricBuffer::new(alpha)).add_measurement(metric.average, metric.min, metric.max);
        ret
    }
}
