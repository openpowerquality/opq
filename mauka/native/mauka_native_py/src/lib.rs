use mauka_native::{arrays, ieee1159_voltage, thd};
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
fn classify_thd(
    start_ts_ms: f64,
    thd_threshold_percent: f64,
    data: Vec<f32>,
) -> PyResult<Vec<ThdIncident>> {
    Ok(thd::thd(start_ts_ms, thd_threshold_percent, data)
        .iter()
        .map(|i| i.into())
        .collect())
}

#[pyfunction]
fn percent_thd_per_cycle(data: Vec<f32>) -> PyResult<Vec<f32>> {
    Ok(thd::percent_thd(data))
}

// -------------------------------- Arrays
#[pyclass(dict)]
#[derive(Debug)]
struct Range {
    bound_key: String,
    bound_min: f64,
    bound_max: f64,
    pub start_idx: usize,
    pub end_idx: usize,
    pub start_ts_ms: f64,
    pub end_ts_ms: f64,
}

#[pymethods]
impl Range {
    #[getter(bound_key)]
    fn bound_key(&self) -> PyResult<String> {
        Ok(self.bound_key.clone())
    }

    #[getter(bound_min)]
    fn bound_min(&self) -> PyResult<f64> {
        Ok(self.bound_min)
    }

    #[getter(bound_max)]
    fn bound_max(&self) -> PyResult<f64> {
        Ok(self.bound_max)
    }

    #[getter(start_idx)]
    fn start_idx(&self) -> PyResult<usize> {
        Ok(self.start_idx)
    }

    #[getter(end_idx)]
    fn end_idx(&self) -> PyResult<usize> {
        Ok(self.end_idx)
    }

    #[getter(start_ts_ms)]
    fn start_ts_ms(&self) -> PyResult<f64> {
        Ok(self.start_ts_ms)
    }

    #[getter(end_ts_ms)]
    fn end_ts_ms(&self) -> PyResult<f64> {
        Ok(self.end_ts_ms)
    }
}

impl From<&arrays::Range> for Range {
    fn from(range: &arrays::Range) -> Self {
        Range {
            bound_key: range.bound.key.clone(),
            bound_min: range.bound.min,
            bound_max: range.bound.max,
            start_idx: range.start_idx,
            end_idx: range.end_idx,
            start_ts_ms: range.start_ts_ms,
            end_ts_ms: range.end_ts_ms,
        }
    }
}

#[pyfunction]
fn bounded_ranges(start_ts_ms: f64, data: Vec<f64>, bounds: Vec<Vec<f64>>) -> PyResult<Vec<Range>> {
    let bounds: Vec<arrays::Bound> = bounds.iter().map(|bound| bound.into()).collect();
    let bounds: Vec<&arrays::Bound> = bounds.iter().map(|bound| bound).collect();
    let ranges = arrays::bounded_ranges(start_ts_ms, &data, &bounds);
    Ok(ranges.iter().map(|range| range.into()).collect())
}

// -------------------------------- Module setup
#[pymodule]
fn mauka_native_py(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_wrapped(wrap_pyfunction!(classify_rms))?;
    m.add_wrapped(wrap_pyfunction!(classify_thd))?;
    m.add_wrapped(wrap_pyfunction!(bounded_ranges))?;
    m.add_wrapped(wrap_pyfunction!(percent_thd_per_cycle))?;

    Ok(())
}
