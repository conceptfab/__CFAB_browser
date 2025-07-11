use pyo3::prelude::*;
use pyo3::types::{PyDict, PyType};
use pyo3::exceptions::PyRuntimeError;
use std::collections::{HashMap, HashSet};
use std::path::Path;
use rayon::prelude::*;
use thiserror::Error;
use log::error;

#[derive(Error, Debug)]
enum ScannerError {
    #[error("Folder nie istnieje: {0}")]
    #[allow(dead_code)]
    FolderNotFound(String),

    #[error("Brak uprawnień do odczytu folderu: {0}")]
    #[allow(dead_code)]
    PermissionDenied(String),

    #[error("Błąd I/O: {0}")]
    IoError(#[from] std::io::Error),

    #[error("Błąd serializacji JSON: {0}")]
    JsonError(#[from] serde_json::Error),

    #[error("Błąd tworzenia asetu: {0}")]
    #[allow(dead_code)]
    AssetCreationError(String),
}

use crate::types::*;
use crate::file_utils::*;
use crate::asset_builder::AssetBuilder;

// Macro for runtime errors
macro_rules! py_runtime_error {
    ($msg:expr) => {
        PyErr::new::<PyRuntimeError, _>($msg)
    };
    ($fmt:expr, $($arg:tt)*) => {
        PyErr::new::<PyRuntimeError, _>(format!($fmt, $($arg)*))
    };
}

use std::sync::Mutex;
use once_cell::sync::Lazy;

/// Cache dla powtórnych skanowań
struct ScannerCache {
    last_scan_path: Option<String>,
    archive_files: HashMap<String, std::path::PathBuf>,
    image_files: HashMap<String, std::path::PathBuf>,
}

static SCANNER_CACHE: Lazy<Mutex<ScannerCache>> = Lazy::new(|| {
    Mutex::new(ScannerCache {
        last_scan_path: None,
        archive_files: HashMap::new(),
        image_files: HashMap::new(),
    })
});

#[pyclass]
pub struct RustAssetRepository {
    file_extensions: FileExtensions,
    asset_builder: AssetBuilder,
    #[allow(dead_code)]
    use_cache: bool,
}

#[pymethods]
impl RustAssetRepository {
    #[new]
    fn new() -> Self {
        Self {
            file_extensions: FileExtensions::default(),
            asset_builder: AssetBuilder::new(),
            use_cache: true,
        }
    }

    /// Tworzy nową instancję z wyłączonym cachem (przydatne dla testów)
    #[classmethod]
    #[pyo3(name = "new_without_cache")]
    fn new_without_cache(_cls: &Bound<'_, PyType>) -> Self {
        Self {
            file_extensions: FileExtensions::default(),
            asset_builder: AssetBuilder::new(),
            use_cache: false,
        }
    }

    /// Main function for scanning and creating assets
    /// Resetuje cache skanera
    #[pyo3(name = "reset_cache")]
    fn reset_scanner_cache(&self) -> PyResult<()> {
        if let Ok(mut cache) = SCANNER_CACHE.lock() {
            cache.last_scan_path = None;
            cache.archive_files.clear();
            cache.image_files.clear();
        }
        Ok(())
    }

    #[pyo3(signature = (folder_path, progress_callback=None))]
    fn find_and_create_assets(
        &self,
        py: Python,
        folder_path: String,
        progress_callback: Option<PyObject>,
    ) -> PyResult<Vec<PyObject>> {
        let folder_path = Path::new(&folder_path);

        // Path validation
        if !folder_path.exists() || !folder_path.is_dir() {
            return Err(PyErr::new::<pyo3::exceptions::PyFileNotFoundError, _>(
                format!("Folder does not exist: {:?}", folder_path)
            ));
        }

        // Initial message - scanning files (0-10%)
        if let Some(ref callback) = progress_callback {
            callback.call1(py, (0, 100, "Scanning files...".to_string()))
                .map_err(|e| py_runtime_error!("Progress callback failed: {}", e))?;
        }

        // Scanning and grouping files (10-20%)
        let (archive_by_name, image_by_name) = self.scan_and_group_files(folder_path)
            .map_err(|e| py_runtime_error!("Scan error: {}", e))?;

        if let Some(ref callback) = progress_callback {
            callback.call1(py, (20, 100, "Files scanned".to_string()))
                .map_err(|e| py_runtime_error!("Progress callback failed: {}", e))?;
        }

        // Find common names
        let common_names: HashSet<String> = archive_by_name
            .keys()
            .filter(|name| image_by_name.contains_key(*name))
            .cloned()
            .collect();

        if common_names.is_empty() {
            // Message if no assets found, but still create unpaired files list
            if let Some(ref callback) = progress_callback {
                if let Err(e) = callback.call1(py, (95, 100, "No assets found, creating unpaired files list...".to_string())) {
                    eprintln!("Progress callback error: {:?}", e);
                }
            }
            
            // Create unpaired files list even when no assets are found
            self.create_unpaired_files_json(folder_path, &archive_by_name, &image_by_name, &common_names)
                .map_err(|e| py_runtime_error!("Error creating unpaired files: {}", e))?;
            
            // Final message
            if let Some(ref callback) = progress_callback {
                if let Err(e) = callback.call1(py, (100, 100, "Scan completed - no assets found".to_string())) {
                    eprintln!("Progress callback error: {:?}", e);
                }
            }
            return Ok(Vec::new());
        }

        // Prepare names for parallel processing
        let names_vec: Vec<_> = common_names.into_iter().collect();
        let total_assets = names_vec.len();
        
        // Progress tracking without callback in parallel code
        if let Some(ref callback) = progress_callback {
            callback.call1(py, (25, 100, format!("Processing {} assets...", total_assets)))
                .map_err(|e| py_runtime_error!("Progress callback failed: {}", e))?;
        }

        // Parallel processing without Python objects
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
                            // Save asset to file
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
            py_assets.push(self.asset_builder.asset_to_pydict(py, &asset)?);
        }

        // Message about adding special folders (95%)
        if let Some(ref callback) = progress_callback {
            if let Err(e) = callback.call1(py, (95, 100, "Adding special folders...".to_string())) {
                eprintln!("Progress callback error: {:?}", e);
            }
        }

        // Add special folders
        let special_folders = scan_for_special_folders(folder_path)
            .unwrap_or_else(|_| Vec::new());

        for special_folder in special_folders {
            let py_dict = PyDict::new_bound(py);
            py_dict.set_item("type", &special_folder.folder_type)?;
            py_dict.set_item("name", &special_folder.name)?;
            py_dict.set_item("folder_path", &special_folder.folder_path)?;
            py_assets.push(py_dict.into());
        }

        // Create unpaired files file (97%)
        if let Some(ref callback) = progress_callback {
            if let Err(e) = callback.call1(py, (97, 100, "Creating unpaired files list...".to_string())) {
                eprintln!("Progress callback error: {:?}", e);
            }
        }

        self.create_unpaired_files_json(folder_path, &archive_by_name, &image_by_name, &HashSet::from_iter(names_vec.iter().cloned()))
            .map_err(|e| py_runtime_error!("Error creating unpaired files: {}", e))?;

        // Final message (100%)
        if let Some(ref callback) = progress_callback {
            if let Err(e) = callback.call1(py, (100, 100, format!("Scan completed - {} assets created", py_assets.len()))) {
                eprintln!("Progress callback error: {:?}", e);
            }
        }

        Ok(py_assets)
    }

    /// Loads existing assets from folder
    fn load_existing_assets(&self, py: Python, folder_path: String) -> PyResult<Vec<PyObject>> {
        let folder_path = Path::new(&folder_path);

        if !folder_path.exists() || !folder_path.is_dir() {
            return Err(PyErr::new::<pyo3::exceptions::PyFileNotFoundError, _>(
                format!("Folder does not exist: {:?}", folder_path)
            ));
        }

        let mut assets = Vec::new();

        // Load .asset files
        for entry in std::fs::read_dir(folder_path)? {
            let entry = entry?;
            let path = entry.path();

            if path.is_file() && path.extension().map_or(false, |ext| ext == "asset") {
                match self.asset_builder.load_asset_from_file(&path) {
                    Ok(asset) => {
                        assets.push(self.asset_builder.asset_to_pydict(py, &asset)?);
                    }
                    Err(e) => {
                        eprintln!("🦀 Error loading asset from {:?}: {:?} [build: {}, module: 1]", path, e, env!("VERGEN_BUILD_TIMESTAMP"));
                    }
                }
            }
        }

        // Add special folders at the beginning
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

    /// Scans folder for archive and image files
    fn scan_folder_for_files(&self, py: Python, folder_path: String) -> PyResult<(PyObject, PyObject)> {
        let folder_path = Path::new(&folder_path);
        let (archive_by_name, image_by_name) = self.scan_and_group_files(folder_path)
            .map_err(|e| py_runtime_error!("Scan error: {}", e))?;

        // Convert to Python dict
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

    /// Creates a single asset
    fn create_single_asset(
        &self,
        py: Python,
        name: String,
        archive_path: String,
        preview_path: String,
        work_folder_path: String,
    ) -> PyResult<PyObject> {
        let archive_path = Path::new(&archive_path);
        let preview_path = Path::new(&preview_path);
        let work_folder_path = Path::new(&work_folder_path);

        match self.asset_builder.create_single_asset(
            &name,
            archive_path,
            preview_path,
            work_folder_path,
        ) {
            Ok(asset) => {
                // Save asset to file
                let asset_file_path = work_folder_path.join(format!("{}.asset", name));
                if let Err(e) = self.asset_builder.save_asset_to_file(&asset, &asset_file_path) {
                    return Err(py_runtime_error!("Error saving asset file: {}", e));
                }

                Ok(self.asset_builder.asset_to_pydict(py, &asset)?)
            }
            Err(e) => Err(py_runtime_error!("Error creating asset: {}", e)),
        }
    }
}

impl RustAssetRepository {
    /// Scans folder and groups files by names - zoptymalizowana wersja równoległa
    fn scan_and_group_files(&self, folder_path: &Path) -> Result<(HashMap<String, std::path::PathBuf>, HashMap<String, std::path::PathBuf>), Box<dyn std::error::Error>> {

        // Równoległe skanowanie folderów
        let (archive_files, image_files) = rayon::join(
            || get_files_by_extensions(folder_path, &self.file_extensions.archives),
            || get_files_by_extensions(folder_path, &self.file_extensions.images)
        );

        let archive_files = archive_files?;
        let image_files = image_files?;

        // Grupowanie plików równolegle
        let archive_by_name = group_files_by_name(archive_files);
        let image_by_name = group_files_by_name(image_files);

        Ok((archive_by_name, image_by_name))
    }

    /// Creates JSON file with unpaired files
    fn create_unpaired_files_json(
        &self,
        folder_path: &Path,
        archive_by_name: &HashMap<String, std::path::PathBuf>,
        image_by_name: &HashMap<String, std::path::PathBuf>,
        common_names: &HashSet<String>,
    ) -> Result<(), Box<dyn std::error::Error>> {
        // Sprawdź czy folder istnieje
        if !folder_path.exists() || !folder_path.is_dir() {
            return Err(format!("Folder nie istnieje: {:?}", folder_path).into());
        }

        // Upewnij się, że mamy prawa zapisu do folderu
        let test_path = folder_path.join(".write_test");
        if let Err(e) = std::fs::write(&test_path, "") {
            return Err(format!("Brak uprawnień do zapisu w folderze: {}", e).into());
        }
        let _ = std::fs::remove_file(test_path);
        let mut unpaired_files = UnpairedFiles {
            archives: Vec::new(),
            images: Vec::new(),
            total_archives: 0,
            total_images: 0,
        };

        // Zbierz wszystkie pliki archiwów w folderze
        let archive_exts = ["zip", "rar", "7z", "sbsar"];
        let mut all_archives = Vec::new();
        for entry in std::fs::read_dir(folder_path)? {
            let entry = entry?;
            let path = entry.path();
            if path.is_file() {
                if let Some(ext) = path.extension().and_then(|e| e.to_str()) {
                    if archive_exts.contains(&ext.to_lowercase().as_str()) {
                        all_archives.push(path.clone());
                    }
                }
            }
        }

        // Zbierz wszystkie pliki podglądów w folderze
        let image_exts = ["png", "jpg", "jpeg", "webp"];
        let mut all_images = Vec::new();
        for entry in std::fs::read_dir(folder_path)? {
            let entry = entry?;
            let path = entry.path();
            if path.is_file() {
                if let Some(ext) = path.extension().and_then(|e| e.to_str()) {
                    if image_exts.contains(&ext.to_lowercase().as_str()) {
                        all_images.push(path.clone());
                    }
                }
            }
        }

        // Dodaj do niesparowanych archiwów te, które nie mają pary
        for path in all_archives {
            let name = path.file_stem().and_then(|n| n.to_str()).unwrap_or("").to_lowercase();
            if !common_names.contains(&name) {
                let fname = path.file_name().unwrap_or_default().to_string_lossy().to_string();
                println!("[UNPAIRED ARCHIVE] {}", fname);
                unpaired_files.archives.push(fname);
            }
        }

        // Dodaj do niesparowanych obrazków te, które nie mają pary
        for path in all_images {
            let name = path.file_stem().and_then(|n| n.to_str()).unwrap_or("").to_lowercase();
            if !common_names.contains(&name) {
                let fname = path.file_name().unwrap_or_default().to_string_lossy().to_string();
                println!("[UNPAIRED IMAGE] {}", fname);
                unpaired_files.images.push(fname);
            }
        }

        // Sortuj alfabetycznie
        unpaired_files.archives.sort();
        unpaired_files.images.sort();

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