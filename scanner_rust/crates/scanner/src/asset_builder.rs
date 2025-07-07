use crate::types::{Asset, FileExtensions};
use crate::file_utils;
use crate::thumbnail;
use std::path::Path;
use std::fs;
use anyhow::Result;

pub struct AssetBuilder {
    file_extensions: FileExtensions,
}

impl AssetBuilder {
    pub fn new() -> Self {
        Self {
            file_extensions: FileExtensions::default(),
        }
    }

    /// Creates a single asset
    pub fn create_single_asset(
        &self,
        name: &str,
        archive_path: &Path,
        image_path: &Path,
        folder_path: &Path,
    ) -> Result<Asset> {
        // NEW VALIDATION
        self.validate_asset_inputs(name, archive_path, image_path, folder_path)?;
        
        let size_mb = file_utils::get_file_size_mb(archive_path)?;
        let textures_in_archive = file_utils::check_texture_folders_presence(folder_path);

        // Get only file names, not full paths
        let archive_name = archive_path
            .file_name()
            .and_then(|name| name.to_str())
            .ok_or_else(|| anyhow::anyhow!("Cannot get archive file name"))?;

        let preview_name = image_path
            .file_name()
            .and_then(|name| name.to_str())
            .ok_or_else(|| anyhow::anyhow!("Cannot get image file name"))?;

        // Generate thumbnail for image file
        let thumbnail_name = match thumbnail::generate_thumbnail(&image_path.to_string_lossy()) {
            Ok((thumb_name, _size)) => thumb_name,
            Err(_) => {
                // If thumbnail generation fails, use default name
                format!("{}.thumb", name)
            }
        };

        Ok(Asset {
            asset_type: "asset".to_string(),
            name: name.to_string(),
            archive: archive_name.to_string(),
            preview: preview_name.to_string(),
            size_mb,
            thumbnail: thumbnail_name,
            stars: None,
            color: None,
            textures_in_archive,
            meta: serde_json::Value::Object(serde_json::Map::new()),
        })
    }

    /// Saves asset to .asset file
    pub fn save_asset_to_file(&self, asset: &Asset, file_path: &Path) -> Result<()> {
        let json_content = serde_json::to_string_pretty(asset)?;
        fs::write(file_path, json_content)
            .map_err(|e| anyhow::anyhow!("Error saving .asset file: {}", e))?;
        Ok(())
    }

    /// Loads asset from .asset file
    pub fn load_asset_from_file(&self, file_path: &Path) -> Result<Asset> {
        let content = fs::read_to_string(file_path)
            .map_err(|e| anyhow::anyhow!("Error reading .asset file: {}", e))?;
        
        let asset: Asset = serde_json::from_str(&content)
            .map_err(|e| anyhow::anyhow!("JSON parsing error: {}", e))?;
        
        Ok(asset)
    }

    /// Validates input data
    pub fn validate_asset_inputs(
        &self,
        name: &str,
        archive_path: &Path,
        image_path: &Path,
        folder_path: &Path,
    ) -> Result<()> {
        if name.is_empty() {
            return Err(anyhow::anyhow!("Asset name cannot be empty"));
        }

        if !archive_path.exists() {
            return Err(anyhow::anyhow!("Archive file does not exist: {:?}", archive_path));
        }

        if !image_path.exists() {
            return Err(anyhow::anyhow!("Image file does not exist: {:?}", image_path));
        }

        if !folder_path.exists() || !folder_path.is_dir() {
            return Err(anyhow::anyhow!("Folder does not exist: {:?}", folder_path));
        }

        // Check file extensions
        if let Some(ext) = archive_path.extension() {
            if let Some(ext_str) = ext.to_str() {
                if !self.file_extensions.archives.contains(&ext_str.to_lowercase()) {
                    return Err(anyhow::anyhow!("Unsupported archive extension: {}", ext_str));
                }
            }
        }

        if let Some(ext) = image_path.extension() {
            if let Some(ext_str) = ext.to_str() {
                if !self.file_extensions.images.contains(&ext_str.to_lowercase()) {
                    return Err(anyhow::anyhow!("Unsupported image extension: {}", ext_str));
                }
            }
        }

        Ok(())
    }
} 