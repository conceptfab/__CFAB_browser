use pyo3::prelude::*;
use pyo3::types::PyDict;
use pyo3::exceptions::PyRuntimeError;
use std::collections::{HashMap, HashSet};
use std::path::Path;
use rayon::prelude::*;
use log::{debug, error};

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

    #[pyo3(signature = (folder_path, progress_callback=None))]
    fn find_and_create_assets(
        &self,
        py: Python,
        folder_path: String,
        progress_callback: Option<Py<PyAny>>,
    ) -> PyResult<Vec<Py<PyAny>>> {
        let folder_pathbuf = std::path::PathBuf::from(&folder_path);
        let folder_path = folder_pathbuf.as_path();

        if !folder_path.exists() || !folder_path.is_dir() {
            return Err(PyErr::new::<pyo3::exceptions::PyFileNotFoundError, _>(
                format!("Folder does not exist: {:?}", folder_path)
            ));
        }

        if let Some(ref callback) = progress_callback {
            callback.call1(py, (0, 100, "Scanning files...".to_string()))
                .map_err(|e| py_runtime_error!("Progress callback failed: {}", e))?;
        }

        let (archive_by_name, image_by_name) = py.detach(|| {
            self.scan_and_group_files(folder_path).map_err(|e| e.to_string())
        }).map_err(|e| py_runtime_error!("Scan error: {}", e))?;

        if let Some(ref callback) = progress_callback {
            callback.call1(py, (20, 100, "Files scanned".to_string()))
                .map_err(|e| py_runtime_error!("Progress callback failed: {}", e))?;
        }

        let common_names: HashSet<String> = archive_by_name
            .keys()
            .filter(|name| image_by_name.contains_key(*name))
            .cloned()
            .collect();

        if common_names.is_empty() {
            if let Some(ref callback) = progress_callback {
                if let Err(e) = callback.call1(py, (95, 100, "No assets found, creating unpaired files list...".to_string())) {
                    error!("Progress callback error: {:?}", e);
                }
            }

            py.detach(|| {
                self.create_unpaired_files_json(folder_path, &archive_by_name, &image_by_name, &common_names)
                    .map_err(|e| e.to_string())
            }).map_err(|e| py_runtime_error!("Error creating unpaired files: {}", e))?;

            if let Some(ref callback) = progress_callback {
                if let Err(e) = callback.call1(py, (100, 100, "Scan completed - no assets found".to_string())) {
                    error!("Progress callback error: {:?}", e);
                }
            }
            return Ok(Vec::new());
        }

        let names_vec: Vec<_> = common_names.into_iter().collect();
        let total_assets = names_vec.len();

        if let Some(ref callback) = progress_callback {
            callback.call1(py, (25, 100, format!("Processing {} assets...", total_assets)))
                .map_err(|e| py_runtime_error!("Progress callback failed: {}", e))?;
        }

        let created_assets: Vec<_> = py.detach(|| {
            names_vec
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
                                let asset_file_path = folder_path.join(format!("{}.asset", name));
                                if let Err(e) = self.asset_builder.save_asset_to_file(&asset, &asset_file_path) {
                                    error!("Error saving asset {}: {:?}", name, e);
                                    return None;
                                }
                                Some(asset)
                            }
                            Err(e) => {
                                error!("Error creating asset {}: {:?}", name, e);
                                None
                            }
                        }
                    } else {
                        None
                    }
                })
                .collect()
        });

        if let Some(ref callback) = progress_callback {
            callback.call1(py, (80, 100, format!("Created {} assets, converting...", created_assets.len())))
                .map_err(|e| py_runtime_error!("Progress callback failed: {}", e))?;
        }

        let mut py_assets = Vec::new();
        for asset in &created_assets {
            py_assets.push(self.asset_builder.asset_to_pydict(py, asset)?);
        }

        if let Some(ref callback) = progress_callback {
            if let Err(e) = callback.call1(py, (95, 100, "Adding special folders...".to_string())) {
                error!("Progress callback error: {:?}", e);
            }
        }

        let special_folders = py.detach(|| {
            scan_for_special_folders(folder_path).unwrap_or_else(|_| Vec::new())
        });

        for special_folder in special_folders {
            let py_dict = PyDict::new(py);
            py_dict.set_item("type", &special_folder.folder_type)?;
            py_dict.set_item("name", &special_folder.name)?;
            py_dict.set_item("folder_path", &special_folder.folder_path)?;
            py_assets.push(py_dict.into());
        }

        if let Some(ref callback) = progress_callback {
            if let Err(e) = callback.call1(py, (97, 100, "Creating unpaired files list...".to_string())) {
                error!("Progress callback error: {:?}", e);
            }
        }

        let names_hashset: HashSet<String> = names_vec.iter().cloned().collect();
        py.detach(|| {
            self.create_unpaired_files_json(folder_path, &archive_by_name, &image_by_name, &names_hashset)
                .map_err(|e| e.to_string())
        }).map_err(|e| py_runtime_error!("Error creating unpaired files: {}", e))?;

        if let Some(ref callback) = progress_callback {
            if let Err(e) = callback.call1(py, (100, 100, format!("Scan completed - {} assets created", py_assets.len()))) {
                error!("Progress callback error: {:?}", e);
            }
        }

        Ok(py_assets)
    }

    /// Loads existing assets from folder
    fn load_existing_assets(&self, py: Python, folder_path: String) -> PyResult<Vec<Py<PyAny>>> {
        let folder_pathbuf = std::path::PathBuf::from(&folder_path);
        let folder_path = folder_pathbuf.as_path();

        if !folder_path.exists() || !folder_path.is_dir() {
            return Err(PyErr::new::<pyo3::exceptions::PyFileNotFoundError, _>(
                format!("Folder does not exist: {:?}", folder_path)
            ));
        }

        let (loaded_assets, special_folders) = py.detach(|| -> std::io::Result<(Vec<crate::types::Asset>, Vec<SpecialFolder>)> {
            let mut loaded = Vec::new();
            for entry in std::fs::read_dir(folder_path)? {
                let entry = entry?;
                let path = entry.path();
                if path.is_file() && path.extension().map_or(false, |ext| ext == "asset") {
                    match self.asset_builder.load_asset_from_file(&path) {
                        Ok(asset) => loaded.push(asset),
                        Err(e) => error!("Error loading asset from {:?}: {:?}", path, e),
                    }
                }
            }
            let special = scan_for_special_folders(folder_path).unwrap_or_else(|_| Vec::new());
            Ok((loaded, special))
        })?;

        let mut result = Vec::new();
        for special_folder in special_folders {
            let py_dict = PyDict::new(py);
            py_dict.set_item("type", &special_folder.folder_type)?;
            py_dict.set_item("name", &special_folder.name)?;
            py_dict.set_item("folder_path", &special_folder.folder_path)?;
            result.push(py_dict.into());
        }

        for asset in &loaded_assets {
            result.push(self.asset_builder.asset_to_pydict(py, asset)?);
        }

        Ok(result)
    }

    /// Scans folder for archive and image files
    fn scan_folder_for_files(&self, py: Python, folder_path: String) -> PyResult<(Py<PyAny>, Py<PyAny>)> {
        let folder_pathbuf = std::path::PathBuf::from(&folder_path);
        let folder_path = folder_pathbuf.as_path();
        let (archive_by_name, image_by_name) = py.detach(|| {
            self.scan_and_group_files(folder_path).map_err(|e| e.to_string())
        }).map_err(|e| py_runtime_error!("Scan error: {}", e))?;

        let py_archives = PyDict::new(py);
        let py_images = PyDict::new(py);

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
    ) -> PyResult<Py<PyAny>> {
        let archive_pathbuf = std::path::PathBuf::from(&archive_path);
        let preview_pathbuf = std::path::PathBuf::from(&preview_path);
        let work_folder_pathbuf = std::path::PathBuf::from(&work_folder_path);
        let name_str = name;

        let asset = py.detach(|| -> PyResult<crate::types::Asset> {
            let built = self.asset_builder.create_single_asset(
                &name_str,
                archive_pathbuf.as_path(),
                preview_pathbuf.as_path(),
                work_folder_pathbuf.as_path(),
            ).map_err(|e| py_runtime_error!("Error creating asset: {}", e))?;

            let asset_file_path = work_folder_pathbuf.join(format!("{}.asset", name_str));
            self.asset_builder.save_asset_to_file(&built, &asset_file_path)
                .map_err(|e| py_runtime_error!("Error saving asset file: {}", e))?;

            Ok(built)
        })?;

        self.asset_builder.asset_to_pydict(py, &asset)
    }
}

impl RustAssetRepository {
    /// Scans folder once and buckets files by extension in a single pass.
    ///
    /// Previously this did two parallel `read_dir` calls on the same folder
    /// (rayon::join) — thrashing on HDDs and redundant syscalls on SSDs.
    fn scan_and_group_files(&self, folder_path: &Path) -> Result<(HashMap<String, std::path::PathBuf>, HashMap<String, std::path::PathBuf>), Box<dyn std::error::Error>> {
        let mut archive_files = Vec::new();
        let mut image_files = Vec::new();

        for entry in std::fs::read_dir(folder_path)? {
            let path = entry?.path();
            if !path.is_file() {
                continue;
            }
            if has_valid_extension(&path, &self.file_extensions.archives) {
                archive_files.push(path);
            } else if has_valid_extension(&path, &self.file_extensions.images) {
                image_files.push(path);
            }
        }

        Ok((group_files_by_name(archive_files), group_files_by_name(image_files)))
    }

    /// Creates JSON file with unpaired files.
    ///
    /// Uses the already-scanned `archive_by_name` / `image_by_name` maps
    /// instead of re-reading the directory — saves two full `read_dir`
    /// passes per scan and keeps the extension list in sync with
    /// `FileExtensions::default()`.
    fn create_unpaired_files_json(
        &self,
        folder_path: &Path,
        archive_by_name: &HashMap<String, std::path::PathBuf>,
        image_by_name: &HashMap<String, std::path::PathBuf>,
        common_names: &HashSet<String>,
    ) -> Result<(), Box<dyn std::error::Error>> {
        if !folder_path.exists() || !folder_path.is_dir() {
            return Err(format!("Folder nie istnieje: {:?}", folder_path).into());
        }

        let mut archives: Vec<String> = archive_by_name
            .iter()
            .filter(|(name, _)| !common_names.contains(*name))
            .filter_map(|(_, path)| {
                let fname = path.file_name()?.to_string_lossy().into_owned();
                debug!("[UNPAIRED ARCHIVE] {}", fname);
                Some(fname)
            })
            .collect();

        let mut images: Vec<String> = image_by_name
            .iter()
            .filter(|(name, _)| !common_names.contains(*name))
            .filter_map(|(_, path)| {
                let fname = path.file_name()?.to_string_lossy().into_owned();
                debug!("[UNPAIRED IMAGE] {}", fname);
                Some(fname)
            })
            .collect();

        archives.sort();
        images.sort();

        let unpaired_files = UnpairedFiles {
            total_archives: archives.len(),
            total_images: images.len(),
            archives,
            images,
        };

        let json_path = folder_path.join("unpair_files.json");
        let json_content = serde_json::to_string_pretty(&unpaired_files)?;
        std::fs::write(&json_path, json_content)?;

        Ok(())
    }
} 