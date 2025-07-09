use pyo3::prelude::*;
use std::collections::HashMap;

/// Returns build information for Rust Image Tools module
#[pyfunction]
pub fn get_build_info() -> HashMap<String, String> {
    let mut info = HashMap::new();
    
    // Module number (3)
    info.insert("module_number".to_string(), "3".to_string());
    
    // Build information
    info.insert("build_timestamp".to_string(), env!("VERGEN_BUILD_TIMESTAMP").to_string());
    
    // Cargo information
    info.insert("cargo_target_triple".to_string(), env!("VERGEN_CARGO_TARGET_TRIPLE").to_string());
    
    // Additional information
    info.insert("rust_version".to_string(), env!("VERGEN_RUSTC_SEMVER").to_string());
    
    info
}

/// Returns build number (timestamp as string)
#[pyfunction]
pub fn get_build_number() -> String {
    env!("VERGEN_BUILD_TIMESTAMP").to_string()
}

/// Returns build date and time in readable format
#[pyfunction]
pub fn get_build_datetime() -> String {
    env!("VERGEN_BUILD_TIMESTAMP").to_string()
}

/// Returns Git commit hash
#[pyfunction]
pub fn get_git_commit() -> String {
    option_env!("VERGEN_GIT_SHA").unwrap_or("unknown").to_string()
}

/// Returns module number
#[pyfunction]
pub fn get_module_number() -> u32 {
    3
}

/// Returns module information in text format
#[pyfunction]
pub fn get_module_info() -> String {
    format!(
        "Rust Image Tools Module (module: {}, build: {}, target: {})",
        3,
        env!("VERGEN_BUILD_TIMESTAMP"),
        env!("VERGEN_CARGO_TARGET_TRIPLE")
    )
}

/// Returns logging prefix with build number
#[pyfunction]
pub fn get_log_prefix() -> String {
    format!("[build: {}, module: {}]", env!("VERGEN_BUILD_TIMESTAMP"), 3)
}

/// Formats message with build prefix
#[pyfunction]
pub fn format_log_message(message: &str) -> String {
    format!("🦀 {} [build: {}, module: {}]", message, env!("VERGEN_BUILD_TIMESTAMP"), 3)
} 