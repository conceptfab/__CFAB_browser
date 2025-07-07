use serde::{Deserialize, Serialize};

/// Struktura reprezentująca asset
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Asset {
    #[serde(rename = "type")]
    pub asset_type: String,
    pub name: String,
    pub archive: String,
    pub preview: String,
    pub size_mb: f64,
    pub thumbnail: String,
    pub stars: Option<i32>,
    pub color: Option<String>,
    #[serde(rename = "textures_in_the_archive")]
    pub textures_in_archive: bool,
    pub meta: serde_json::Value,
}

/// Struktura reprezentująca folder specjalny
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SpecialFolder {
    pub folder_type: String,
    pub name: String,
    pub folder_path: String,
}

/// Wynik skanowania
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ScanResult {
    pub assets: Vec<Asset>,
    pub special_folders: Vec<SpecialFolder>,
    pub unpaired_files: UnpairedFiles,
}

/// Niesparowane pliki
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct UnpairedFiles {
    pub archives: Vec<String>,
    pub images: Vec<String>,
}

/// Konfiguracja rozszerzeń plików
#[derive(Debug, Clone)]
pub struct FileExtensions {
    pub archives: std::collections::HashSet<String>,
    pub images: std::collections::HashSet<String>,
}

impl Default for FileExtensions {
    fn default() -> Self {
        Self {
            archives: ["zip", "rar", "sbsar", "7z"]
                .iter()
                .map(|s| s.to_string())
                .collect(),
            images: ["png", "jpg", "jpeg", "webp"]
                .iter()
                .map(|s| s.to_string())
                .collect(),
        }
    }
}

/// Błędy scanera
#[derive(thiserror::Error, Debug)]
pub enum ScannerError {
    #[error("Folder nie istnieje: {0}")]
    FolderNotFound(String),
    #[error("Brak uprawnień do folderu: {0}")]
    PermissionDenied(String),
    #[error("Błąd I/O: {0}")]
    IoError(#[from] std::io::Error),
    #[error("Błąd JSON: {0}")]
    JsonError(#[from] serde_json::Error),
}

/// Konfiguracja scanera
#[derive(Debug, Clone)]
pub struct ScannerConfig {
    pub thumbnail_size: u32,
    pub parallel_processing: bool,
    pub cache_dir_name: String,
    pub file_extensions: FileExtensions,
}

impl Default for ScannerConfig {
    fn default() -> Self {
        Self {
            thumbnail_size: 256,
            parallel_processing: true,
            cache_dir_name: ".cache".to_string(),
            file_extensions: FileExtensions::default(),
        }
    }
} 