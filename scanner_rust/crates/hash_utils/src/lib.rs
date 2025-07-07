use pyo3::prelude::*;
use sha2::{Digest, Sha256};
use std::fs::File;
use std::io::{BufReader, Read};

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
    m.add_function(wrap_pyfunction!(calculate_sha256, m)?)?;
    Ok(())
} 