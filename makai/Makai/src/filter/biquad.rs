use num;
use num::traits::Float;


/// A biquad filter in transposed direct form 2.
///
/// This implementation uses a Transposed [Direct Form II](https://en.wikipedia.org/wiki/Digital_biquad_filter#Direct_Form_2)
/// realization using the following equations:
///
/// `y[n] = b0*x[n] + w[n-1]; w[n-1] = b1*x[n] + w[n-2] - a1*y[n]; w[n-2] = b2*x[n] - a2*y[n];`
///
/// It has two feedforward coefficients, `b1` and `b2`, and two feedback
/// coefficients, `a1` and `a2`.

pub struct Biquad2<T> {
    z1: T,
    z2: T,
    output: T,
    pub b0: T,
    pub b1: T,
    pub b2: T,
    pub a1: T,
    pub a2: T
}

impl<T> Biquad2<T> where T: Float {

    pub fn new(initial : T) -> Self {
        Biquad2 {
            z1: num::zero(),
            z2: num::zero(),
            output: initial,
            b0: num::one(),
            b1: num::zero(),
            b2: num::zero(),
            a1: num::zero(),
            a2: num::zero()
        }
    }

    /// Sets all filter coefficients at once.
    ///
    /// `b1`, `b2` are feedforwards, or zeroes, and `a1`, `a2` are feedbacks,
    /// or poles.
    pub fn set_coefficients(&mut self, b0: T, b1: T, b2: T, a1: T, a2: T) {
        self.b0 = b0;
        self.b1 = b1;
        self.b2 = b2;
        self.a1 = a1;
        self.a2 = a2;
    }

    pub fn process(&mut self, sample: T) -> T {
        self.output = self.b0 * sample + self.z1;
        self.z1 = self.b1 * sample + self.z2 - self.a1 * self.output;
        self.z2 = self.b2 * sample - self.a2 * self.output;
        self.output
    }

    pub fn clear(&mut self) {
        self.z1 = num::zero();
        self.z2 = num::zero();
        self.output = num::zero();
    }

    pub fn last_out(&self) -> T {
        self.output
    }
}
