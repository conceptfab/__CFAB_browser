use crate::types::{Asset, FileExtensions};
use crate::file_utils;
use crate::thumbnail;
use std::path::Path;
use std::fs;
use anyhow::Result;
use std::time::SystemTime;
use log::{debug, warn};
use pyo3::types::PyDict;
use pyo3::types::PyDictMethods;

pub struct AssetBuilder {
    file_extensions: FileExtensions,
    #[allow(dead_code)]
    created_at: SystemTime,
}

impl AssetBuilder {
    pub fn new() -> Self {
        Self {
            file_extensions: FileExtensions::default(),
            created_at: SystemTime::now(),
        }
    }

    /// Tworzy nową instancję z własnymi rozszerzeniami plików
    #[allow(dead_code)]
    pub fn with_extensions(file_extensions: FileExtensions) -> Self {
        Self {
            file_extensions,
            created_at: SystemTime::now(),
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
        let textures_in_archive = !file_utils::has_texture_folders(folder_path);

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
            Ok((thumb_name, size)) => {
                debug!("Thumbnail generated for {}: {} ({} bytes)", name, thumb_name, size);
                thumb_name
            },
            Err(e) => {
                // If thumbnail generation fails, use default name
                warn!("Failed to generate thumbnail for {}: {}", name, e);
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

    /// Tworzy pusty szablon Asset z domyślnymi wartościami
    #[allow(dead_code)]
    pub fn create_empty_asset(&self, name: &str) -> Asset {
        Asset {
            asset_type: "asset".to_string(),
            name: name.to_string(),
            archive: String::new(),
            preview: String::new(),
            size_mb: 0.0,
            thumbnail: format!("{}.thumb", name),
            stars: None,
            color: None,
            textures_in_archive: false,
            meta: serde_json::Value::Object(serde_json::Map::new()),
        }
    }

    /// Validates input data with improved error handling
    pub fn validate_asset_inputs(
        &self,
        name: &str,
        archive_path: &Path,
        image_path: &Path,
        folder_path: &Path,
    ) -> Result<()> {
        // Walidacja nazwy
        if name.is_empty() {
            return Err(anyhow::anyhow!("Asset name cannot be empty"));
        }

        // Sprawdź nieprawidłowe znaki w nazwie
        if name.contains(|c: char| c == '/' || c == '\\' || c == ':' || c == '*' || c == '?' || c == '"' || c == '<' || c == '>' || c == '|') {
            return Err(anyhow::anyhow!("Asset name contains invalid characters: {}", name));
        }

        // Sprawdź pliki i foldery równolegle
        let ((archive_exists, image_exists), folder_valid) = rayon::join(
            || rayon::join(
                || archive_path.exists(),
                || image_path.exists()
            ),
            || folder_path.exists() && folder_path.is_dir()
        );

        if !archive_exists {
            return Err(anyhow::anyhow!("Archive file does not exist: {:?}", archive_path));
        }

        if !image_exists {
            return Err(anyhow::anyhow!("Image file does not exist: {:?}", image_path));
        }

        if !folder_valid {
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

    /// Helper: konwertuje Asset na PyDict
    pub fn asset_to_pydict<'py>(&self, py: pyo3::Python<'py>, asset: &crate::types::Asset) -> pyo3::PyResult<pyo3::PyObject> {
        let py_dict = PyDict::new_bound(py);
        py_dict.set_item("type", &asset.asset_type)?;
        py_dict.set_item("name", &asset.name)?;
        py_dict.set_item("archive", &asset.archive)?;
        py_dict.set_item("preview", &asset.preview)?;
        py_dict.set_item("size_mb", asset.size_mb)?;
        py_dict.set_item("thumbnail", &asset.thumbnail)?;
        py_dict.set_item("stars", &asset.stars)?;
        py_dict.set_item("color", &asset.color)?;
        py_dict.set_item("textures_in_the_archive", asset.textures_in_archive)?;
        py_dict.set_item("meta", asset.meta.to_string())?;
        Ok(py_dict.into())
    }
} 