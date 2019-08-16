use arraydeque::{ArrayDeque, Wrapping};

#[derive(Debug)]
pub struct MetricBuffer {
    pub history: ArrayDeque<[f32; 32], Wrapping>,
    pub last: f32,
    pub mean: f32,
    pub mean_sq: f32,
    pub alpha: f32,
}

impl MetricBuffer {
    pub fn new(alpha: f32) -> MetricBuffer {
        MetricBuffer {
            history: ArrayDeque::new(),
            mean: 0.0,
            mean_sq: 0.0,
            last: 0.0,
            alpha,
        }
    }

    pub fn add_measurement(&mut self, new: f32) -> f32 {
        let derivative = if self.history.len() == 0 {
            self.mean = new;
            self.mean_sq = 0.0;
            let derivative = new - self.last;
            derivative
        } else {
            self.mean = (1.0 - self.alpha) * self.mean + self.alpha * new;
            self.mean_sq = (1.0 - self.alpha) * self.mean_sq + self.alpha * (new.powi(2));
            0.0
        };
        self.history.push_back(new);
        self.last = new;
        derivative
    }

    pub fn std_dev(&self) -> f32 {
        let var = self.mean_sq - self.mean.powi(2);
        var.sqrt()
    }
}
