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
            archives: ["zip", "rar", "sbsar", "7z", "spsm"]
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

