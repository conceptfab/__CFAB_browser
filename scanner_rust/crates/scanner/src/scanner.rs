use pyo3::prelude::*;
use pyo3::types::PyDict;
use pyo3::exceptions::PyRuntimeError;
use std::collections::{HashMap, HashSet};
use std::path::Path;
use rayon::prelude::*;

use crate::types::*;
use crate::file_utils::*;
use crate::asset_builder::AssetBuilder;

// Makro dla błędów runtime
macro_rules! py_runtime_error {
    ($msg:expr) => {
        PyErr::new::<PyRuntimeError, _>($msg)
    };
    ($fmt:expr, $($arg:tt)*) => {
        PyErr::new::<PyRuntimeError, _>(format!($fmt, $($arg)*))
    };
}

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

        // Komunikat początkowy - skanowanie plików (0-10%)
        if let Some(ref callback) = progress_callback {
            callback.call1(py, (0, 100, "Scanning files...".to_string()))
                .map_err(|e| py_runtime_error!("Progress callback failed: {}", e))?;
        }

        // Skanowanie i grupowanie plików (10-20%)
        let (archive_by_name, image_by_name) = self.scan_and_group_files(folder_path)
            .map_err(|e| py_runtime_error!("Scan error: {}", e))?;

        if let Some(ref callback) = progress_callback {
            callback.call1(py, (20, 100, "Files scanned".to_string()))
                .map_err(|e| py_runtime_error!("Progress callback failed: {}", e))?;
        }

        // Znajdź wspólne nazwy
        let common_names: HashSet<String> = archive_by_name
            .keys()
            .filter(|name| image_by_name.contains_key(*name))
            .cloned()
            .collect();

        if common_names.is_empty() {
            // Komunikat końcowy jeśli brak assetów
            if let Some(ref callback) = progress_callback {
                if let Err(e) = callback.call1(py, (100, 100, "No assets found".to_string())) {
                    eprintln!("Progress callback error: {:?}", e);
                }
            }
            return Ok(Vec::new());
        }

        // Przygotuj nazwy do równoległego przetwarzania
        let names_vec: Vec<_> = common_names.into_iter().collect();
        let total_assets = names_vec.len();
        
        // Progress tracking bez callback w parallel code
        if let Some(ref callback) = progress_callback {
            callback.call1(py, (25, 100, format!("Processing {} assets...", total_assets)))
                .map_err(|e| py_runtime_error!("Progress callback failed: {}", e))?;
        }

        // Parallel processing bez Python objektów
        let created_assets: Vec<_> = names_vec
            .par_iter()
            .filter_map(|name| {
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
                                eprintln!("🦀 Error saving asset {}: {:?} [build: {}, module: 1]", name, e, env!("VERGEN_BUILD_TIMESTAMP"));
                                return None;
                            }

                            Some(asset)
                        }
                        Err(e) => {
                            eprintln!("🦀 Error creating asset {}: {:?} [build: {}, module: 1]", name, e, env!("VERGEN_BUILD_TIMESTAMP"));
                            None
                        }
                    }
                } else {
                    None
                }
            })
            .collect();

        // Progress update (80%)
        if let Some(ref callback) = progress_callback {
            callback.call1(py, (80, 100, format!("Created {} assets, converting...", created_assets.len())))
                .map_err(|e| py_runtime_error!("Progress callback failed: {}", e))?;
        }

        // Convert assets to Python objects (sequential, but fast)
        let mut py_assets = Vec::new();
        for asset in created_assets {
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
            py_assets.push(py_dict.into());
        }

        // Komunikat o dodawaniu folderów specjalnych (95%)
        if let Some(ref callback) = progress_callback {
            if let Err(e) = callback.call1(py, (95, 100, "Adding special folders...".to_string())) {
                eprintln!("Progress callback error: {:?}", e);
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
            py_assets.push(py_dict.into());
        }

        // Utwórz plik z niesparowanymi plikami (97%)
        if let Some(ref callback) = progress_callback {
            if let Err(e) = callback.call1(py, (97, 100, "Creating unpaired files list...".to_string())) {
                eprintln!("Progress callback error: {:?}", e);
            }
        }

        self.create_unpaired_files_json(folder_path, &archive_by_name, &image_by_name, &HashSet::from_iter(names_vec.iter().cloned()))
            .map_err(|e| py_runtime_error!("Error creating unpaired files: {}", e))?;

        // Komunikat końcowy (100%)
        if let Some(ref callback) = progress_callback {
            if let Err(e) = callback.call1(py, (100, 100, format!("Scan completed - {} assets created", py_assets.len()))) {
                eprintln!("Progress callback error: {:?}", e);
            }
        }

        Ok(py_assets)
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
                        assets.push(py_dict.into());
                    }
                    Err(e) => {
                        eprintln!("🦀 Error loading asset from {:?}: {:?} [build: {}, module: 1]", path, e, env!("VERGEN_BUILD_TIMESTAMP"));
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
            .map_err(|e| py_runtime_error!("Scan error: {}", e))?;

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
            total_archives: 0,
            total_images: 0,
        };

        // Znajdź niesparowane archiwum
        for (name, path) in archive_by_name {
            if !common_names.contains(name) {
                unpaired_files.archives.push(path.file_name().unwrap_or_default().to_string_lossy().to_string());
            }
        }

        // Znajdź niesparowane obrazy
        for (name, path) in image_by_name {
            if !common_names.contains(name) {
                unpaired_files.images.push(path.file_name().unwrap_or_default().to_string_lossy().to_string());
            }
        }

        // Ustaw liczniki
        unpaired_files.total_archives = unpaired_files.archives.len();
        unpaired_files.total_images = unpaired_files.images.len();

        // Zapisz do pliku JSON
        let json_path = folder_path.join("unpair_files.json");
        let json_content = serde_json::to_string_pretty(&unpaired_files)?;
        std::fs::write(&json_path, json_content)?;

        Ok(())
    }
} 