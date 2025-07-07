use pyo3::prelude::*;
use pyo3::Bound;
use log::info;

mod scanner;
mod file_utils;
mod asset_builder;
mod types;
mod thumbnail;

use scanner::RustAssetRepository;

/// Moduł Rust Scanner dla PyO3
#[pymodule]
fn scanner_rust(m: &Bound<'_, PyModule>) -> PyResult<()> {
    // Inicjalizuj logger
    let _ = env_logger::try_init();
    info!("🦀 Rust Scanner module initialized");
    
    m.add_class::<RustAssetRepository>()?;
    Ok(())
} 