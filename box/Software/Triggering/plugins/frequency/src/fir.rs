pub struct FIR {
    history: Vec<f32>,
    taps: Vec<f32>,
    last_index: usize,
    decimation: usize,
}

impl FIR {
    pub fn new(taps: Vec<f32>, decimation: usize) -> FIR {
        FIR {
            history: vec![0.0; taps.len()],
            last_index: 0,
            taps,
            decimation,
        }
    }
    pub fn process(&mut self, data: &Vec<f32>) -> Vec<f32> {
        let mut counter: usize = 0;
        data.iter()
            .filter_map(|sample| {
                self.put(sample.clone());
                let ret = if counter % self.decimation == 0 {
                    Some(self.get())
                } else {
                    None
                };
                counter += 1;
                ret
            })
            .collect()
    }

    fn put(&mut self, sample: f32) {
        self.history[self.last_index] = sample;
        self.last_index += 1;
        if self.last_index >= self.taps.len() {
            self.last_index = 0;
        }
    }
    fn get(&mut self) -> f32 {
        let mut acc: f32 = 0.0;
        let mut index = self.last_index;
        for i in 0..self.taps.len() {
            acc += self.history[index] * self.taps[i];
            index += 1;
            if index >= self.taps.len() {
                index = 0;
            }
        }
        acc
    }
}
