use serde::{Deserialize, Serialize};

/// Structure representing an asset
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

/// Structure representing a special folder
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SpecialFolder {
    pub folder_type: String,
    pub name: String,
    pub folder_path: String,
}

/// Scan result
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ScanResult {
    pub assets: Vec<Asset>,
    pub special_folders: Vec<SpecialFolder>,
    pub unpaired_files: UnpairedFiles,
}

/// Unpaired files
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct UnpairedFiles {
    #[serde(rename = "unpaired_archives")]
    pub archives: Vec<String>,
    #[serde(rename = "unpaired_images")]
    pub images: Vec<String>,
    #[serde(rename = "total_unpaired_archives")]
    pub total_archives: usize,
    #[serde(rename = "total_unpaired_images")]
    pub total_images: usize,
}

/// File extensions configuration
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

/// Scanner errors
#[derive(thiserror::Error, Debug)]
pub enum ScannerError {
    #[error("I/O Error: {0}")]
    IoError(#[from] std::io::Error),
    #[error("JSON Error: {0}")]
    JsonError(#[from] serde_json::Error),
}

/// Scanner configuration
#[derive(Debug, Clone)]
pub struct ScannerConfig {
    // Fields reserved for future use
    _thumbnail_size: u32,
    _parallel_processing: bool,
    _cache_dir_name: String,
    _file_extensions: FileExtensions,
}

impl Default for ScannerConfig {
    fn default() -> Self {
        Self {
            _thumbnail_size: 256,
            _parallel_processing: true,
            _cache_dir_name: ".cache".to_string(),
            _file_extensions: FileExtensions::default(),
        }
    }
} 