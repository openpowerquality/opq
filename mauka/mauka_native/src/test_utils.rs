use crate::analysis::*;

fn generate_vrms_waveform(pu: f64, c: usize) -> Vec<f64> {
    // Start every waveform with 60 cycles of nominal
    let mut wf: Vec<f64> = (0..60).map(|_| 120.0).collect();

    // Add the deviation
    wf.append(&mut (0..c).map(|_| pu_to_rms(pu)).collect());

    // Finish with another 60 cycles of nominal
    wf.append(&mut (0..60).map(|_| 120.0).collect());

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
