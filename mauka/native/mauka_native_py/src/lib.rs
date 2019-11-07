use mauka_native::{ieee1159_voltage, thd};
use pyo3::prelude::*;
use pyo3::wrap_pyfunction;

// -------------------------------- IEEE 1159 Voltage
#[pyclass(dict)]
#[derive(Debug)]
struct Ieee1159VoltageIncident {
    pub start_time_ms: f64,
    pub end_time_ms: f64,
    pub start_idx: usize,
    pub end_idx: usize,
    pub incident_classification: String,
}

#[pymethods]
impl Ieee1159VoltageIncident {
    #[getter(start_time_ms)]
    fn start_time_ms(&self) -> PyResult<f64> {
        Ok(self.start_time_ms)
    }

    #[getter(end_time_ms)]
    fn end_time_ms(&self) -> PyResult<f64> {
        Ok(self.end_time_ms)
    }

    #[getter(start_idx)]
    fn start_idx_ms(&self) -> PyResult<usize> {
        Ok(self.start_idx)
    }

    #[getter(end_idx)]
    fn end_idx(&self) -> PyResult<usize> {
        Ok(self.end_idx)
    }

    #[getter(incident_classification)]
    fn incident_classifcation(&self) -> PyResult<String> {
        Ok(self.incident_classification.clone())
    }

    fn __str__(&self) -> PyResult<String> {
        Ok(format!("{:#?}", self))
    }
}

impl From<&ieee1159_voltage::Ieee1159VoltageIncident> for Ieee1159VoltageIncident {
    fn from(incident: &ieee1159_voltage::Ieee1159VoltageIncident) -> Self {
        Ieee1159VoltageIncident {
            start_time_ms: incident.start_time_ms,
            end_time_ms: incident.end_time_ms,
            start_idx: incident.start_idx,
            end_idx: incident.end_idx,
            incident_classification: incident.incident_classification.clone(),
        }
    }
}

#[pyfunction]
fn classify_rms(start_ts_ms: f64, data: Vec<f64>) -> PyResult<Vec<Ieee1159VoltageIncident>> {
    Ok(ieee1159_voltage::classify_rms(start_ts_ms, &data)
        .iter()
        .map(|i| i.into())
        .collect())
}

// -------------------------------- THD
#[pyclass(dict)]
#[derive(Debug)]
struct ThdIncident {
    pub start_time_ms: f64,
    pub end_time_ms: f64,
}

#[pymethods]
impl ThdIncident {
    #[getter(start_time_ms)]
    fn start_time_ms(&self) -> PyResult<f64> {
        Ok(self.start_time_ms)
    }

    #[getter(end_time_ms)]
    fn end_time_ms(&self) -> PyResult<f64> {
        Ok(self.end_time_ms)
    }
}

impl From<&thd::ThdIncident> for ThdIncident {
    fn from(incident: &thd::ThdIncident) -> Self {
        ThdIncident {
            start_time_ms: incident.start_time_ms,
            end_time_ms: incident.end_time_ms,
        }
    }
}

#[pyfunction]
fn classify_thd(start_ts_ms: f64, data: Vec<f32>) -> PyResult<Vec<ThdIncident>> {
    Ok(thd::thd(start_ts_ms, data)
        .iter()
        .map(|i| i.into())
        .collect())
}

// -------------------------------- Module setup
#[pymodule]
fn mauka_native_py(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_wrapped(wrap_pyfunction!(classify_rms))?;
    m.add_wrapped(wrap_pyfunction!(classify_thd))?;

    Ok(())
}
