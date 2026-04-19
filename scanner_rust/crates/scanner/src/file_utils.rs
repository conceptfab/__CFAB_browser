use std::collections::{HashMap, HashSet};
use std::path::{Path, PathBuf};
use std::fs;
use anyhow::Result;

/// Checks if file has valid extension (case-insensitive)
pub fn has_valid_extension(file_path: &Path, extensions: &HashSet<String>) -> bool {
    if let Some(ext) = file_path.extension() {
        if let Some(ext_str) = ext.to_str() {
            let ext_lower = ext_str.to_lowercase();
            return extensions.contains(&ext_lower);
        }
    }
    false
}

/// Gets file size in MB (full precision; callers format for display).
pub fn get_file_size_mb(file_path: &Path) -> Result<f64> {
    let metadata = fs::metadata(file_path)?;
    Ok(metadata.len() as f64 / (1024.0 * 1024.0))
}

/// Groups files by names (case-insensitive)
pub fn group_files_by_name(files: Vec<PathBuf>) -> HashMap<String, PathBuf> {
    let mut grouped = HashMap::new();

    for file in files {
        if let Some(stem) = file.file_stem() {
            if let Some(name) = stem.to_str() {
                let key = name.to_lowercase();
                grouped.insert(key, file);
            }
        }
    }

    grouped
}

/// Checks presence of texture folders
pub fn has_texture_folders(folder_path: &Path) -> bool {
    let texture_folders = ["tex", "textures", "maps"];
    for folder_name in &texture_folders {
        let texture_path = folder_path.join(folder_name);
        if texture_path.is_dir() {
            return true; // Found texture folder
        }
    }
    false // No texture folders
}

/// Scans for special folders
pub fn scan_for_special_folders(folder_path: &Path) -> Result<Vec<crate::types::SpecialFolder>> {
    let mut special_folders = Vec::new();
    let special_names = ["tex", "textures", "maps"];

    for name in &special_names {
        let special_path = folder_path.join(name);
        if special_path.is_dir() {
            special_folders.push(crate::types::SpecialFolder {
                folder_type: "special_folder".to_string(),
                name: name.to_string(),
                folder_path: special_path.to_string_lossy().to_string(),
            });
        }
    }

    Ok(special_folders)
} 