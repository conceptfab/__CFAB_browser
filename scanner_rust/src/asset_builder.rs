use crate::types::{Asset, FileExtensions};
use crate::file_utils;
use std::path::Path;
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

    /// Tworzy pojedynczy asset
    pub fn create_single_asset(
        &self,
        name: &str,
        archive_path: &Path,
        image_path: &Path,
        folder_path: &Path,
    ) -> Result<Asset> {
        let archive_size_mb = file_utils::get_file_size_mb(archive_path)?;
        let texture_in_archive = file_utils::check_texture_folders_presence(folder_path);

        Ok(Asset {
            name: name.to_string(),
            archive_path: archive_path.to_string_lossy().to_string(),
            image_path: image_path.to_string_lossy().to_string(),
            folder_path: folder_path.to_string_lossy().to_string(),
            archive_size_mb,
            texture_in_archive,
            thumbnail_path: None,
        })
    }

    /// Waliduje dane wejściowe dla tworzenia asset-a
    pub fn validate_asset_inputs(
        &self,
        name: &str,
        archive_path: &Path,
        image_path: &Path,
        folder_path: &Path,
    ) -> Result<()> {
        if name.is_empty() {
            return Err(anyhow::anyhow!("Nazwa asset-a nie może być pusta"));
        }

        if !archive_path.exists() {
            return Err(anyhow::anyhow!("Plik archiwum nie istnieje: {:?}", archive_path));
        }

        if !image_path.exists() {
            return Err(anyhow::anyhow!("Plik obrazu nie istnieje: {:?}", image_path));
        }

        if !folder_path.exists() {
            return Err(anyhow::anyhow!("Folder nie istnieje: {:?}", folder_path));
        }

        Ok(())
    }

    /// Zapisuje asset do pliku JSON
    pub fn save_asset_to_file(&self, asset: &Asset, asset_file_path: &Path) -> Result<()> {
        let json_content = serde_json::to_string_pretty(asset)?;
        std::fs::write(asset_file_path, json_content)?;
        Ok(())
    }

    /// Ładuje asset z pliku JSON
    pub fn load_asset_from_file(&self, asset_file_path: &Path) -> Result<Asset> {
        let json_content = std::fs::read_to_string(asset_file_path)?;
        let asset: Asset = serde_json::from_str(&json_content)?;
        Ok(asset)
    }
} 