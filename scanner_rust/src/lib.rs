use pyo3::prelude::*;
use pyo3::Bound;

mod scanner;
mod file_utils;
mod asset_builder;
mod types;

use scanner::RustAssetRepository;

/// Moduł Rust Scanner dla PyO3
#[pymodule]
fn scanner_rust(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<RustAssetRepository>()?;
    Ok(())
} 