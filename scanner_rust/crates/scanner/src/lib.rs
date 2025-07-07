use pyo3::prelude::*;
use pyo3::Bound;
use log::info;

mod scanner;
mod file_utils;
mod asset_builder;
mod types;
mod thumbnail;
mod build_info;

use scanner::RustAssetRepository;
use build_info::{get_build_info, get_build_number, get_build_datetime, get_git_commit, get_module_number, get_module_info, get_log_prefix, format_log_message};

/// Moduł Rust Scanner dla PyO3
#[pymodule]
fn scanner_rust(m: &Bound<'_, PyModule>) -> PyResult<()> {
    // Inicjalizuj logger
    let _ = env_logger::try_init();
    
    // Pobierz informacje o kompilacji
    let build_number = env!("VERGEN_BUILD_TIMESTAMP");
    let module_number = 1;
    
    info!("🦀 Rust Scanner module initialized [build: {}, module: {}]", build_number, module_number);
    
    // Dodaj klasę główną
    m.add_class::<RustAssetRepository>()?;
    
    // Dodaj funkcje informacji o kompilacji
    m.add_function(wrap_pyfunction!(get_build_info, m)?)?;
    m.add_function(wrap_pyfunction!(get_build_number, m)?)?;
    m.add_function(wrap_pyfunction!(get_build_datetime, m)?)?;
    m.add_function(wrap_pyfunction!(get_git_commit, m)?)?;
    m.add_function(wrap_pyfunction!(get_module_number, m)?)?;
    m.add_function(wrap_pyfunction!(get_module_info, m)?)?;
    m.add_function(wrap_pyfunction!(get_log_prefix, m)?)?;
    m.add_function(wrap_pyfunction!(format_log_message, m)?)?;
    
    Ok(())
} 