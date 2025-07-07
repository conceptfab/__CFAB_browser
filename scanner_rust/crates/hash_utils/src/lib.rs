use pyo3::prelude::*;
use sha2::{Digest, Sha256};
use std::fs::File;
use std::io::{BufReader, Read};

mod build_info;
use build_info::{get_build_info, get_build_number, get_build_datetime, get_git_commit, get_module_number, get_module_info, get_log_prefix, format_log_message};

/// Calculates the SHA-256 hash of a file.
#[pyfunction]
fn calculate_sha256(py: Python, file_path: String) -> PyResult<String> {
    py.allow_threads(|| {
        let file = File::open(&file_path)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("Failed to open file {}: {}", file_path, e)))?;
        let mut reader = BufReader::new(file);
        let mut hasher = Sha256::new();
        let mut buffer = [0; 4096];

        loop {
            let n = reader.read(&mut buffer)
                .map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("Failed to read file {}: {}", file_path, e)))?;
            if n == 0 {
                break;
            }
            hasher.update(&buffer[..n]);
        }

        let hash_result = hasher.finalize();
        Ok(format!("{:x}", hash_result))
    })
}

#[pymodule]
fn hash_utils(m: &Bound<'_, PyModule>) -> PyResult<()> {
    // Dodaj funkcję główną
    m.add_function(wrap_pyfunction!(calculate_sha256, m)?)?;
    
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