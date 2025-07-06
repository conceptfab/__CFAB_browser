use std::collections::{HashMap, HashSet};
use std::path::{Path, PathBuf};
use std::fs;
use anyhow::Result;

/// Sprawdza czy plik ma prawidłowe rozszerzenie
pub fn has_valid_extension(file_path: &Path, extensions: &HashSet<String>) -> bool {
    if let Some(ext) = file_path.extension() {
        if let Some(ext_str) = ext.to_str() {
            return extensions.contains(&ext_str.to_lowercase());
        }
    }
    false
}

/// Pobiera pliki z określonymi rozszerzeniami
pub fn get_files_by_extensions(
    folder_path: &Path,
    extensions: &HashSet<String>
) -> Result<Vec<PathBuf>> {
    let mut files = Vec::new();

    for entry in fs::read_dir(folder_path)? {
        let entry = entry?;
        let path = entry.path();

        if path.is_file() && has_valid_extension(&path, extensions) {
            files.push(path);
        }
    }

    Ok(files)
}

/// Pobiera rozmiar pliku w MB
pub fn get_file_size_mb(file_path: &Path) -> Result<f64> {
    let metadata = fs::metadata(file_path)?;
    let size_bytes = metadata.len() as f64;
    let size_mb = size_bytes / (1024.0 * 1024.0);
    Ok((size_mb * 100.0).round() / 100.0) // Zaokrąglenie do 2 miejsc po przecinku
}

/// Grupuje pliki według nazw (case-insensitive)
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

/// Sprawdza obecność folderów tekstur
pub fn check_texture_folders_presence(folder_path: &Path) -> bool {
    let texture_folders = ["tex", "textures", "maps"];

    for folder_name in &texture_folders {
        let texture_path = folder_path.join(folder_name);
        if texture_path.is_dir() {
            return false; // Znaleziono folder tekstur - tekstury zewnętrzne
        }
    }

    true // Brak folderów tekstur - tekstury w archiwum
}

/// Skanuje w poszukiwaniu folderów specjalnych
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