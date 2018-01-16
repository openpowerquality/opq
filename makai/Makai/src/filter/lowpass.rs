use std;

use filter::Biquad2;

/// A low-pass biquad filter.
pub struct LowPass {
    biquad: Biquad2<f32>
}

impl LowPass{
    /// Creates a new `LowPass` biquad filter.
    pub fn new() -> Self {
        LowPass {
            biquad: Biquad2::<f32>::new()
        }
    }

    /// Set filter coefficients.
    ///
    /// `Biquad2` coefficients are calculated from the `sample_rate`,
    /// `cutoff_frequency`, and `q` factor. These values are not
    /// validated.
    // TODO: Explain value ranges of parameters
    pub fn set_coefficients(&mut self,
                            sample_rate: f32,
                            cutoff_frequency: f32,
                            q: f32)
    {
        let one = 1f32;
        let two = 2f32;

        let w0 = two * (std::f32::consts::PI) * cutoff_frequency / sample_rate;
        let cos_w0  = w0.cos();
        let alpha   = w0.sin() / (two * q);

        let mut b0  = (one - cos_w0) / two;
        let mut b1  =  one - cos_w0;
        let mut b2  =  b0;
        let     a0  =  one + alpha;
        let mut a1  = -two * cos_w0;
        let mut a2  =  one - alpha;

        b0 = b0 / a0;
        b1 = b1 / a0;
        b2 = b2 / a0;
        a1 = a1 / a0;
        a2 = a2 / a0;

        self.biquad.set_coefficients(b0, b1, b2, a1, a2);
        self.clear();
    }

    pub fn process(&mut self, sample: f32) -> f32 {
        self.biquad.process(sample)
    }

    pub fn clear(&mut self) {
        self.biquad.clear();
    }

    pub fn last_out(&self) -> f32 {
        self.biquad.last_out()
    }
}
