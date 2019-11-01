use crate::analysis::*;

pub fn generate_vrms_waveform(pu: f64, c: usize) -> Vec<f64> {
    generate_vrms_waveform_detailed(pu, c, 120.0, 60, 60)
}

pub fn generate_vrms_waveform_detailed(
    pu: f64,
    c: usize,
    nominal: f64,
    start_c: usize,
    end_c: usize,
) -> Vec<f64> {
    // Start every waveform with nominal
    let mut wf: Vec<f64> = (0..start_c).map(|_| nominal).collect();

    // Add the deviation
    wf.append(&mut (0..c).map(|_| pu_to_rms(pu)).collect());

    // Finish with nominal
    wf.append(&mut (0..end_c).map(|_| nominal).collect());

    wf
}

#[cfg(test)]
mod tests {
    use crate::test_utils::generate_vrms_waveform;

    #[test]
    fn test_gen_wf() {
        let wf = generate_vrms_waveform(0.1, 60);
        assert!(&wf[0..59].iter().all(|v| *v == 120.0));
        assert!(&wf[60..119].iter().all(|v| *v == 12.0));
        assert!(&wf[120..].iter().all(|v| *v == 120.0));
    }
}
