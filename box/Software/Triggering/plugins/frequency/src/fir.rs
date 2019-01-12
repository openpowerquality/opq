use num::{Complex, Num, NumCast, Zero};

/// Implement the underlying operations and types required by the FIR.
///
/// In general the AccType should be larger than the SampleType but compatible
/// (i.e. you can add a SampleType to an AccType), while the TapType should
/// always be scalar and is usually the same size as the AccType.
///
/// gain() specifies the gain of the filter, i.e. the sum of all the taps,
/// divided by the interpolation level L.
/// input() copies an item from the input into a given delay line element.
/// accumulate() updates an accumulator with a delay line element * a tap.
/// output() writes to the output array from an accumulator.
pub trait SampleType: Copy {
    type AccType: Zero + Copy;
    type TapType: Num + NumCast + Zero + Copy;
    fn gain(interpolate: usize) -> Self::TapType;
    unsafe fn input(x: *const Self, delay: *mut Self::AccType);
    unsafe fn accumulate(
        acc: &mut Self::AccType,
        delay: *const Self::AccType,
        tap: *const Self::TapType,
    );
    unsafe fn output(acc: &Self::AccType, out: *mut Self, gain: &Self::TapType);
}

/// Implement SampleType for a scalar type such as i16 or f32.
/// $t is the sample type, $tt the acc/tap type and $tapsum the filter gain.
macro_rules! impl_scalar_sampletype {
    ($t:ty, $tt:ty, $tapsum:expr) => {
        impl SampleType for $t {
            type AccType = $tt;
            type TapType = $tt;

            #[inline]
            fn gain(interpolate: usize) -> $tt {
                $tapsum / interpolate as $tt
            }

            #[inline]
            unsafe fn input(x: *const $t, delay: *mut $tt) {
                *delay = *x as $tt;
            }

            #[inline]
            unsafe fn accumulate(acc: &mut $tt, delay: *const $tt, tap: *const $tt) {
                *acc += *delay * *tap;
            }

            #[inline]
            unsafe fn output(acc: &$tt, out: *mut $t, gain: &$tt) {
                *out = (*acc / *gain) as $t;
            }
        }
    };
}

/// Implement SampleType for a Complex type such as Complex<i16>.
/// $t is the sample type, $tt the acc/tap type and $tapsum the filter gain.
macro_rules! impl_complex_sampletype {
    ($t:ty, $tt:ty, $tapsum:expr) => {
        impl SampleType for Complex<$t> {
            type AccType = Complex<$tt>;
            type TapType = $tt;

            #[inline]
            fn gain(interpolate: usize) -> $tt {
                $tapsum / interpolate as $tt
            }

            #[inline]
            unsafe fn input(x: *const Complex<$t>, delay: *mut Complex<$tt>) {
                (*delay).re = (*x).re as $tt;
                (*delay).im = (*x).im as $tt;
            }

            #[inline]
            unsafe fn accumulate(
                acc: &mut Complex<$tt>,
                delay: *const Complex<$tt>,
                tap: *const $tt,
            ) {
                (*acc).re += (*delay).re * *tap;
                (*acc).im += (*delay).im * *tap;
            }

            #[inline]
            unsafe fn output(acc: &Complex<$tt>, out: *mut Complex<$t>, gain: &$tt) {
                (*out).re = ((*acc).re / *gain) as $t;
                (*out).im = ((*acc).im / *gain) as $t;
            }
        }
    };
}

/// Implement Scalar and Complex SampleTypes for the same underlying types.
macro_rules! impl_sampletype {
    ($t:ty, $tt:ty, $tapsum:expr) => {
        impl_scalar_sampletype!($t, $tt, $tapsum);
        impl_complex_sampletype!($t, $tt, $tapsum);
    };
}

impl_sampletype!(i8, i16, 1 << 7);
impl_sampletype!(i16, i32, 1 << 15);
impl_sampletype!(i32, i64, 1 << 31);
impl_sampletype!(f32, f64, 1.0);

/// FIR filter.
pub struct FIR<T: SampleType> {
    taps: Vec<T::TapType>,
    tap_idx: isize,
    delay: Vec<T::AccType>,
    delay_idx: isize,
    decimate: usize,
    interpolate: usize,
}

impl<T: SampleType> FIR<T> {
    /// Create a new FIR with the given taps and decimation.
    ///
    /// Taps should sum to T::gain() or close to it.
    ///
    /// Set decimate=1 for no decimation, decimate=2 for /2, etc.
    /// Set interpolate=1 for no interpolation, interplate=2 for *2, etc.
    /// Note that if the number of taps is not a multiple of the interpolation
    /// ratio then they will be zero-padded at the end until they are.
    ///
    /// Implements a polyphase FIR to do efficient decimation and interpolation
    /// (identical to a standard FIR when interpolate=1).
    pub fn new(taps: &Vec<T::TapType>, decimate: usize, interpolate: usize) -> FIR<T> {
        assert!(taps.len() > 0);
        assert!(decimate > 0);
        assert!(interpolate > 0);

        // Copy the taps and zero-pad to get a multiple of interpolation ratio
        let mut taps: Vec<T::TapType> = taps.to_owned();
        if taps.len() % interpolate != 0 {
            for _ in 0..(interpolate - (taps.len() % interpolate)) {
                taps.push(T::TapType::zero());
            }
        }

        // Set up and fill the delay line with zeros
        let n_delay = taps.len() / interpolate;
        let mut delay: Vec<T::AccType> = Vec::with_capacity(n_delay);
        for _ in 0..n_delay {
            delay.push(T::AccType::zero());
        }

        FIR {
            taps: taps,
            tap_idx: interpolate as isize - 1isize,
            delay: delay,
            delay_idx: 0isize,
            decimate: decimate,
            interpolate: interpolate,
        }
    }

    /// Process a block of data x, outputting the filtered and possibly
    /// decimated data.
    pub fn process(&mut self, x: &Vec<T>) -> Vec<T> {
        // Check we were initialised correctly and
        // ensure invariances required for unsafe code.
        assert!(self.decimate > 0);
        assert!(self.interpolate > 0);
        assert!(self.delay.len() > self.decimate);
        assert!(self.taps.len() > self.interpolate);
        assert!(self.taps.len() % self.interpolate == 0);
        assert!(self.delay.len() == self.taps.len() / self.interpolate);
        assert!(self.delay_idx < self.delay.len() as isize);
        assert!(self.tap_idx < (self.taps.len() / self.interpolate) as isize);
        assert_eq!(x.len() % self.decimate, 0);

        // Allocate output
        let mut y: Vec<T> = Vec::with_capacity((x.len() * self.interpolate) / self.decimate);
        unsafe { y.set_len((x.len() * self.interpolate) / self.decimate) };

        // Grab pointers to various things
        let mut delay_idx = self.delay_idx;
        let mut tap_idx = self.tap_idx;
        let delay_len = self.delay.len() as isize;
        let delay_p = &mut self.delay[0] as *mut T::AccType;
        let out_p = &mut y[0] as *mut T;
        let mut in_p = &x[0] as *const T;
        let ylen = y.len() as isize;
        let decimate = self.decimate as isize;
        let interpolate = self.interpolate as isize;
        let tap0 = &self.taps[0] as *const T::TapType;
        let gain: T::TapType = T::gain(self.interpolate);

        // Process each actually generated output sample
        for k in 0..ylen {
            // For every high-rate clock tick, advance the polyphase
            // coefficient commutators by one, and when they wrap around,
            // insert a new input into the delay line and advance that by one.
            // Repeat until a sample we're not going to skip.
            for _ in 0..decimate {
                // Advance coefficient commutators.
                // Note that the initialised value for tap_idx is
                // interpolate - 1, so that on the first run we'll reset it
                // to zero and add the first sample to the delay line.
                tap_idx += 1;
                if tap_idx == interpolate {
                    tap_idx = 0;

                    // Insert input sample
                    unsafe {
                        T::input(in_p, delay_p.offset(delay_idx));
                        in_p = in_p.offset(1);
                    }
                    delay_idx -= 1;
                    if delay_idx == -1 {
                        delay_idx = delay_len - 1;
                    }
                }
            }

            // Compute the multiply-accumulate only for output samples.
            let mut acc: T::AccType = T::AccType::zero();
            let mut tap_p = unsafe { tap0.offset(tap_idx) };

            // First compute from the index to the end of the buffer
            for idx in (delay_idx + 1)..delay_len {
                unsafe {
                    T::accumulate(&mut acc, delay_p.offset(idx), tap_p);
                    tap_p = tap_p.offset(interpolate);
                }
            }

            // Then compute from the start of the buffer to the index
            for idx in 0..(delay_idx + 1) {
                unsafe {
                    T::accumulate(&mut acc, delay_p.offset(idx), tap_p);
                    tap_p = tap_p.offset(interpolate);
                }
            }

            // Save the result, accounting for filter gain
            unsafe {
                T::output(&acc, out_p.offset(k), &gain);
            }
        }

        // Update index for next time
        self.delay_idx = delay_idx;
        self.tap_idx = tap_idx;

        y
    }
}
