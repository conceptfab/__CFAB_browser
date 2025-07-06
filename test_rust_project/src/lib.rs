
use pyo3::prelude::*;

#[pyfunction]
fn hello_rust() -> String {
    "Hello from Rust!".to_string()
}

#[pymodule]
fn test_rust_project(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(hello_rust, m)?)?;
    Ok(())
}
