use pyo3::prelude::*;
use std::collections::HashMap;

/// Zwraca informacje o kompilacji modułu Rust Image Tools
#[pyfunction]
pub fn get_build_info() -> HashMap<String, String> {
    let mut info = HashMap::new();
    
    // Numer modułu (3)
    info.insert("module_number".to_string(), "3".to_string());
    
    // Informacje o kompilacji
    info.insert("build_timestamp".to_string(), env!("VERGEN_BUILD_TIMESTAMP").to_string());
    
    // Informacje o Cargo
    info.insert("cargo_target_triple".to_string(), env!("VERGEN_CARGO_TARGET_TRIPLE").to_string());
    
    // Dodatkowe informacje
    info.insert("rust_version".to_string(), env!("VERGEN_RUSTC_SEMVER").to_string());
    
    info
}

/// Zwraca numer kompilacji (timestamp jako string)
#[pyfunction]
pub fn get_build_number() -> String {
    env!("VERGEN_BUILD_TIMESTAMP").to_string()
}

/// Zwraca datę i godzinę kompilacji w czytelnym formacie
#[pyfunction]
pub fn get_build_datetime() -> String {
    env!("VERGEN_BUILD_TIMESTAMP").to_string()
}

/// Zwraca hash commita Git
#[pyfunction]
pub fn get_git_commit() -> String {
    "unknown".to_string()
}

/// Zwraca numer modułu
#[pyfunction]
pub fn get_module_number() -> u32 {
    3
}

/// Zwraca informacje o module w formacie tekstowym
#[pyfunction]
pub fn get_module_info() -> String {
    format!(
        "Rust Image Tools Module (module: {}, build: {}, target: {})",
        3,
        env!("VERGEN_BUILD_TIMESTAMP"),
        env!("VERGEN_CARGO_TARGET_TRIPLE")
    )
}

/// Zwraca prefiks logowania z numerem kompilacji
#[pyfunction]
pub fn get_log_prefix() -> String {
    format!("[build: {}, module: {}]", env!("VERGEN_BUILD_TIMESTAMP"), 3)
}

/// Formatuje komunikat z prefiksem kompilacji
#[pyfunction]
pub fn format_log_message(message: &str) -> String {
    format!("🦀 {} [build: {}, module: {}]", message, env!("VERGEN_BUILD_TIMESTAMP"), 3)
} 