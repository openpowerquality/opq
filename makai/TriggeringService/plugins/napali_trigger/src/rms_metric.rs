use metric_buffer::MetricBuffer;
use std::collections::HashMap;
use std::sync::Arc;
use triggering_service::proto::opqbox3::Measurement;
use types::{BoxMetric, MetricResult, MetricStatus, NapaliPluginSettings, ThresholdLimit};

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
    fn new_metric(&mut self, measurement: Arc<Measurement>) -> MetricResult {
        if !measurement.metrics.contains_key(RMS_KEY) {
            return MetricResult {
                status: MetricStatus::Empty,
                derivative: 0.0,
            };
        }
        let metric = measurement.metrics.get(RMS_KEY).unwrap();
        let box_id = measurement.box_id;
        let alpha = self.alpha;
        let derivative = self
            .boxes
            .entry(box_id)
            .or_insert_with(|| MetricBuffer::new(alpha))
            .add_measurement(metric.average);
        let mean = self.boxes.get(&box_id).unwrap().mean;
        let std = self.boxes.get(&box_id).unwrap().std_dev();

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
