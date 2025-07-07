use pyo3::prelude::*;
use pyo3::Bound;

mod scanner;
mod file_utils;
mod asset_builder;
mod types;
mod thumbnail;

use scanner::RustAssetRepository;

/// Test funkcja sprawdzająca nową strukturę Asset
#[pyfunction]
fn test_asset_creation() -> PyResult<String> {
    let builder = asset_builder::AssetBuilder::new();
    let test_asset = types::Asset {
        asset_type: "asset".to_string(),
        name: "test_asset".to_string(),
        archive: "test.rar".to_string(),
        preview: "test.webp".to_string(),
        size_mb: 42.74,
        thumbnail: "test.thumb".to_string(),
        stars: None,
        color: None,
        textures_in_archive: true,
        meta: serde_json::Value::Object(serde_json::Map::new()),
    };
    
    match serde_json::to_string_pretty(&test_asset) {
        Ok(json) => Ok(json),
        Err(e) => Err(pyo3::exceptions::PyValueError::new_err(format!("Błąd serializacji: {}", e)))
    }
}

/// Test funkcja generowania miniaturek
#[pyfunction]
fn test_thumbnail_generation(image_path: String) -> PyResult<String> {
    match thumbnail::generate_thumbnail(&image_path) {
        Ok((thumbnail_name, size)) => Ok(format!("Miniaturka: {} ({}px)", thumbnail_name, size)),
        Err(e) => Err(pyo3::exceptions::PyValueError::new_err(format!("Błąd miniaturki: {}", e)))
    }
}

/// Moduł Rust Scanner dla PyO3
#[pymodule]
fn scanner_rust(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<RustAssetRepository>()?;
    m.add_function(wrap_pyfunction!(test_asset_creation, m)?)?;
    m.add_function(wrap_pyfunction!(test_thumbnail_generation, m)?)?;
    Ok(())
} 