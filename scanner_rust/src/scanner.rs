use pyo3::prelude::*;
use pyo3::types::PyDict;
use pyo3::exceptions::PyRuntimeError;
use std::collections::{HashMap, HashSet};
use std::path::Path;
use crate::types::*;
use crate::file_utils::*;
use crate::asset_builder::AssetBuilder;

#[pyclass]
pub struct RustAssetRepository {
    file_extensions: FileExtensions,
    asset_builder: AssetBuilder,
}

#[pymethods]
impl RustAssetRepository {
    #[new]
    fn new() -> Self {
        Self {
            file_extensions: FileExtensions::default(),
            asset_builder: AssetBuilder::new(),
        }
    }

    /// Główna funkcja skanowania i tworzenia asset-ów
    #[pyo3(signature = (folder_path, progress_callback = None))]
    fn find_and_create_assets(
        &self,
        py: Python,
        folder_path: String,
        progress_callback: Option<PyObject>,
    ) -> PyResult<Vec<PyObject>> {
        let folder_path = Path::new(&folder_path);

        // Walidacja ścieżki
        if !folder_path.exists() || !folder_path.is_dir() {
            return Err(PyErr::new::<pyo3::exceptions::PyFileNotFoundError, _>(
                format!("Folder nie istnieje: {:?}", folder_path)
            ));
        }

        // Skanowanie i grupowanie plików
        let (archive_by_name, image_by_name) = self.scan_and_group_files(folder_path)
            .map_err(|e| PyErr::new::<PyRuntimeError, _>(format!("Scan error: {}", e)))?;

        // Znajdź wspólne nazwy
        let common_names: HashSet<String> = archive_by_name
            .keys()
            .filter(|name| image_by_name.contains_key(*name))
            .cloned()
            .collect();

        if common_names.is_empty() {
            return Ok(Vec::new());
        }

        // Tworzenie asset-ów z progress callback
        let mut created_assets = Vec::new();
        let total_assets = common_names.len();

        for (i, name) in common_names.iter().enumerate() {
            // Callback postępu
            if let Some(ref callback) = progress_callback {
                if let Err(e) = callback.call1(py, (i + 1, total_assets, format!("Creating asset: {}", name))) {
                    eprintln!("Progress callback error: {:?}", e);
                }
            }

            if let (Some(archive_path), Some(image_path)) =
                (archive_by_name.get(name), image_by_name.get(name)) {

                match self.asset_builder.create_single_asset(
                    name,
                    archive_path,
                    image_path,
                    folder_path
                ) {
                    Ok(asset) => {
                        // Zapisz asset do pliku
                        let asset_file_path = folder_path.join(format!("{}.asset", name));
                        if let Err(e) = self.asset_builder.save_asset_to_file(&asset, &asset_file_path) {
                            eprintln!("Error saving asset {}: {:?}", name, e);
                            continue;
                        }

                        // Konwersja do PyObject
                        let py_dict = PyDict::new_bound(py);
                        py_dict.set_item("name", &asset.name)?;
                        py_dict.set_item("archive_path", &asset.archive_path)?;
                        py_dict.set_item("image_path", &asset.image_path)?;
                        py_dict.set_item("folder_path", &asset.folder_path)?;
                        py_dict.set_item("archive_size_mb", asset.archive_size_mb)?;
                        py_dict.set_item("texture_in_archive", asset.texture_in_archive)?;
                        if let Some(ref thumbnail_path) = asset.thumbnail_path {
                            py_dict.set_item("thumbnail_path", thumbnail_path)?;
                        }

                        created_assets.push(py_dict.into());
                    }
                    Err(e) => {
                        eprintln!("Error creating asset {}: {:?}", name, e);
                    }
                }
            }
        }

        // Dodaj foldery specjalne
        let special_folders = scan_for_special_folders(folder_path)
            .unwrap_or_else(|_| Vec::new());

        for special_folder in special_folders {
            let py_dict = PyDict::new_bound(py);
            py_dict.set_item("type", &special_folder.folder_type)?;
            py_dict.set_item("name", &special_folder.name)?;
            py_dict.set_item("folder_path", &special_folder.folder_path)?;
            created_assets.push(py_dict.into());
        }

        // Utwórz plik z niesparowanymi plikami
        self.create_unpaired_files_json(folder_path, &archive_by_name, &image_by_name, &common_names)
            .map_err(|e| PyErr::new::<PyRuntimeError, _>(format!("Error creating unpaired files: {}", e)))?;

        Ok(created_assets)
    }

    /// Ładuje istniejące asset-y z folderu
    fn load_existing_assets(&self, py: Python, folder_path: String) -> PyResult<Vec<PyObject>> {
        let folder_path = Path::new(&folder_path);

        if !folder_path.exists() || !folder_path.is_dir() {
            return Err(PyErr::new::<pyo3::exceptions::PyFileNotFoundError, _>(
                format!("Folder nie istnieje: {:?}", folder_path)
            ));
        }

        let mut assets = Vec::new();

        // Ładuj pliki .asset
        for entry in std::fs::read_dir(folder_path)? {
            let entry = entry?;
            let path = entry.path();

            if path.is_file() && path.extension().map_or(false, |ext| ext == "asset") {
                match self.asset_builder.load_asset_from_file(&path) {
                    Ok(asset) => {
                        let py_dict = PyDict::new_bound(py);
                        py_dict.set_item("name", &asset.name)?;
                        py_dict.set_item("archive_path", &asset.archive_path)?;
                        py_dict.set_item("image_path", &asset.image_path)?;
                        py_dict.set_item("folder_path", &asset.folder_path)?;
                        py_dict.set_item("archive_size_mb", asset.archive_size_mb)?;
                        py_dict.set_item("texture_in_archive", asset.texture_in_archive)?;
                        if let Some(ref thumbnail_path) = asset.thumbnail_path {
                            py_dict.set_item("thumbnail_path", thumbnail_path)?;
                        }
                        assets.push(py_dict.into());
                    }
                    Err(e) => {
                        eprintln!("Error loading asset from {:?}: {:?}", path, e);
                    }
                }
            }
        }

        // Dodaj foldery specjalne na początku
        let special_folders = scan_for_special_folders(folder_path)
            .unwrap_or_else(|_| Vec::new());

        let mut result = Vec::new();
        for special_folder in special_folders {
            let py_dict = PyDict::new_bound(py);
            py_dict.set_item("type", &special_folder.folder_type)?;
            py_dict.set_item("name", &special_folder.name)?;
            py_dict.set_item("folder_path", &special_folder.folder_path)?;
            result.push(py_dict.into());
        }

        result.extend(assets);
        Ok(result)
    }

    /// Skanuje folder w poszukiwaniu plików archiwów i obrazów
    fn scan_folder_for_files(&self, py: Python, folder_path: String) -> PyResult<(PyObject, PyObject)> {
        let folder_path = Path::new(&folder_path);
        let (archive_by_name, image_by_name) = self.scan_and_group_files(folder_path)
            .map_err(|e| PyErr::new::<PyRuntimeError, _>(format!("Scan error: {}", e)))?;

        // Konwersja do Python dict
        let py_archives = PyDict::new_bound(py);
        let py_images = PyDict::new_bound(py);

        for (name, path) in archive_by_name {
            py_archives.set_item(name, path.to_string_lossy().to_string())?;
        }

        for (name, path) in image_by_name {
            py_images.set_item(name, path.to_string_lossy().to_string())?;
        }

        Ok((py_archives.into(), py_images.into()))
    }
}

impl RustAssetRepository {
    /// Skanuje folder i grupuje pliki według nazw
    fn scan_and_group_files(&self, folder_path: &Path) -> Result<(HashMap<String, std::path::PathBuf>, HashMap<String, std::path::PathBuf>), Box<dyn std::error::Error>> {
        let archive_files = get_files_by_extensions(folder_path, &self.file_extensions.archives)?;
        let image_files = get_files_by_extensions(folder_path, &self.file_extensions.images)?;

        let archive_by_name = group_files_by_name(archive_files);
        let image_by_name = group_files_by_name(image_files);

        Ok((archive_by_name, image_by_name))
    }

    /// Tworzy plik JSON z niesparowanymi plikami
    fn create_unpaired_files_json(
        &self,
        folder_path: &Path,
        archive_by_name: &HashMap<String, std::path::PathBuf>,
        image_by_name: &HashMap<String, std::path::PathBuf>,
        common_names: &HashSet<String>,
    ) -> Result<(), Box<dyn std::error::Error>> {
        let mut unpaired_files = UnpairedFiles {
            archives: Vec::new(),
            images: Vec::new(),
        };

        // Znajdź niesparowane archiwum
        for (name, path) in archive_by_name {
            if !common_names.contains(name) {
                unpaired_files.archives.push(path.to_string_lossy().to_string());
            }
        }

        // Znajdź niesparowane obrazy
        for (name, path) in image_by_name {
            if !common_names.contains(name) {
                unpaired_files.images.push(path.to_string_lossy().to_string());
            }
        }

        // Zapisz do pliku JSON
        let json_path = folder_path.join("unpaired_files.json");
        let json_content = serde_json::to_string_pretty(&unpaired_files)?;
        std::fs::write(&json_path, json_content)?;

        Ok(())
    }
} 