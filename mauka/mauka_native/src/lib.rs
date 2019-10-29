use pyo3::prelude::*;
use pyo3::wrap_pyfunction;

pub mod native;

#[pyfunction]
pub fn ranges(data: Vec<f64>, ranges: Vec<Vec<f64>>) -> PyResult<Vec<Vec<f64>>> {
    Ok(native::arrays::rust_ranges(data, ranges))
}

#[pymodule]
fn mauka_native(py: Python, m: &PyModule) -> PyResult<()> {
    m.add_wrapped(wrap_pyfunction!(ranges))?;

    Ok(())
}
