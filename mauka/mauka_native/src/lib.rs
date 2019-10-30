use pyo3::prelude::*;
use pyo3::wrap_pyfunction;

pub mod analysis;
pub mod arrays;

#[pymodule]
fn mauka_native(py: Python, m: &PyModule) -> PyResult<()> {
    //    m.add_wrapped(wrap_pyfunction!(ranges))?;

    Ok(())
}
