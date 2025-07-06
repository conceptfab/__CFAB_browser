# Dokumentacja migracji Scanner → Rust + PyO3

## Przegląd

Ten dokument opisuje proces migracji logiki scanera z Python do Rust z wykorzystaniem PyO3. Migracja ma na celu znaczące poprawienie wydajności skanowania folderów, szczególnie przy dużych ilościach plików.

## Analiza obecnej implementacji

### Główne komponenty obecnego scanera (core/scanner.py)

#### AssetRepository - główna klasa

- **Skanowanie plików**: `_scan_folder_for_files()` - grupuje pliki archiwów i obrazów
- **Grupowanie**: Łączy pliki po nazwach (case-insensitive)
- **Tworzenie asset-ów**: `_create_single_asset()` - generuje struktury danych asset-ów
- **Obsługa folderów specjalnych**: tex, textures, maps
- **Zapisywanie JSON**: Integracja z core/json_utils.py
- **Obsługa thumbnail**: Integracja z core/thumbnail.py

#### Kluczowe rozszerzenia plików

```python
FILE_EXTENSIONS = {
    "archives": ["zip", "rar", "sbsar", "7z"],
    "images": ["png", "jpg", "jpeg", "webp"],
}
```

#### Struktura danych Asset

```python
{
    "name": str,
    "archive_path": str,
    "image_path": str,
    "folder_path": str,
    "archive_size_mb": float,
    "texture_in_archive": bool,
    "thumbnail_path": str (optional)
}
```

## Architektura Rust + PyO3

### 1. Struktura projektu

```
scanner_rust/
├── Cargo.toml              # Konfiguracja Rust
├── pyproject.toml          # Konfiguracja Python
├── src/
│   ├── lib.rs             # Główny moduł PyO3
│   ├── scanner.rs         # Implementacja logiki skanowania
│   ├── file_utils.rs      # Narzędzia do operacji na plikach
│   ├── asset_builder.rs   # Budowniczy struktur Asset
│   └── types.rs           # Definicje typów danych
└── tests/
    └── test_scanner.rs    # Testy jednostkowe
```

### 2. Konfiguracja Cargo.toml

```toml
[package]
name = "scanner-rust"
version = "0.1.0"
edition = "2021"

[dependencies]
pyo3 = { version = "0.20", features = ["extension-module"] }
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"
walkdir = "2.4"
rayon = "1.8"          # Przetwarzanie równoległe
anyhow = "1.0"         # Obsługa błędów
once_cell = "1.19"     # Lazy static
thiserror = "1.0"      # Definiowanie błędów

[lib]
name = "scanner_rust"
crate-type = ["cdylib"]

[profile.release]
lto = true
codegen-units = 1
panic = "abort"
```

### 3. Definicje typów (types.rs)

```rust
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

/// Struktura reprezentująca asset
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Asset {
    pub name: String,
    pub archive_path: String,
    pub image_path: String,
    pub folder_path: String,
    pub archive_size_mb: f64,
    pub texture_in_archive: bool,
    pub thumbnail_path: Option<String>,
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
```

### 4. Narzędzia do operacji na plikach (file_utils.rs)

```rust
use std::collections::{HashMap, HashSet};
use std::path::{Path, PathBuf};
use std::fs;
use anyhow::Result;

/// Sprawdza czy plik ma prawidłowe rozszerzenie
pub fn has_valid_extension(file_path: &Path, extensions: &HashSet<String>) -> bool {
    if let Some(ext) = file_path.extension() {
        if let Some(ext_str) = ext.to_str() {
            return extensions.contains(&ext_str.to_lowercase());
        }
    }
    false
}

/// Pobiera pliki z określonymi rozszerzeniami
pub fn get_files_by_extensions(
    folder_path: &Path,
    extensions: &HashSet<String>
) -> Result<Vec<PathBuf>> {
    let mut files = Vec::new();

    for entry in fs::read_dir(folder_path)? {
        let entry = entry?;
        let path = entry.path();

        if path.is_file() && has_valid_extension(&path, extensions) {
            files.push(path);
        }
    }

    Ok(files)
}

/// Pobiera rozmiar pliku w MB
pub fn get_file_size_mb(file_path: &Path) -> Result<f64> {
    let metadata = fs::metadata(file_path)?;
    let size_bytes = metadata.len() as f64;
    let size_mb = size_bytes / (1024.0 * 1024.0);
    Ok((size_mb * 100.0).round() / 100.0) // Zaokrąglenie do 2 miejsc po przecinku
}

/// Grupuje pliki według nazw (case-insensitive)
pub fn group_files_by_name(files: Vec<PathBuf>) -> HashMap<String, PathBuf> {
    let mut grouped = HashMap::new();

    for file in files {
        if let Some(stem) = file.file_stem() {
            if let Some(name) = stem.to_str() {
                let key = name.to_lowercase();
                grouped.insert(key, file);
            }
        }
    }

    grouped
}

/// Sprawdza obecność folderów tekstur
pub fn check_texture_folders_presence(folder_path: &Path) -> bool {
    let texture_folders = ["tex", "textures", "maps"];

    for folder_name in &texture_folders {
        let texture_path = folder_path.join(folder_name);
        if texture_path.is_dir() {
            return false; // Znaleziono folder tekstur - tekstury zewnętrzne
        }
    }

    true // Brak folderów tekstur - tekstury w archiwum
}

/// Skanuje w poszukiwaniu folderów specjalnych
pub fn scan_for_special_folders(folder_path: &Path) -> Result<Vec<crate::types::SpecialFolder>> {
    let mut special_folders = Vec::new();
    let special_names = ["tex", "textures", "maps"];

    for name in &special_names {
        let special_path = folder_path.join(name);
        if special_path.is_dir() {
            special_folders.push(crate::types::SpecialFolder {
                folder_type: "special_folder".to_string(),
                name: name.to_string(),
                folder_path: special_path.to_string_lossy().to_string(),
            });
        }
    }

    Ok(special_folders)
}
```

### 5. Budowniczy Asset-ów (asset_builder.rs)

```rust
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
```

### 6. Główna implementacja Scanner (scanner.rs)

```rust
use pyo3::prelude::*;
use pyo3::types::PyDict;
use std::collections::{HashMap, HashSet};
use std::path::Path;
use rayon::prelude::*;
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
        let (archive_by_name, image_by_name) = self.scan_and_group_files(folder_path)?;

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
                        let py_dict = PyDict::new(py);
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
            let py_dict = PyDict::new(py);
            py_dict.set_item("type", &special_folder.folder_type)?;
            py_dict.set_item("name", &special_folder.name)?;
            py_dict.set_item("folder_path", &special_folder.folder_path)?;
            created_assets.push(py_dict.into());
        }

        // Utwórz plik z niesparowanymi plikami
        self.create_unpaired_files_json(folder_path, &archive_by_name, &image_by_name, &common_names)?;

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
                        let py_dict = PyDict::new(py);
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
            let py_dict = PyDict::new(py);
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
        let (archive_by_name, image_by_name) = self.scan_and_group_files(folder_path)?;

        // Konwersja do Python dict
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
}

impl RustAssetRepository {
    /// Wewnętrzna funkcja skanowania i grupowania plików
    fn scan_and_group_files(&self, folder_path: &Path) -> Result<(HashMap<String, std::path::PathBuf>, HashMap<String, std::path::PathBuf>), Box<dyn std::error::Error>> {
        // Znajdź pliki archiwów i obrazów
        let archive_files = get_files_by_extensions(folder_path, &self.file_extensions.archives)?;
        let image_files = get_files_by_extensions(folder_path, &self.file_extensions.images)?;

        // Grupuj według nazw
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
        let unpaired_archives: Vec<String> = archive_by_name
            .iter()
            .filter(|(name, _)| !common_names.contains(*name))
            .map(|(_, path)| path.to_string_lossy().to_string())
            .collect();

        let unpaired_images: Vec<String> = image_by_name
            .iter()
            .filter(|(name, _)| !common_names.contains(*name))
            .map(|(_, path)| path.to_string_lossy().to_string())
            .collect();

        let unpaired_data = UnpairedFiles {
            archives: unpaired_archives,
            images: unpaired_images,
        };

        let json_content = serde_json::to_string_pretty(&unpaired_data)?;
        let unpaired_file_path = folder_path.join("unpaired_files.json");
        std::fs::write(unpaired_file_path, json_content)?;

        Ok(())
    }
}
```

### 7. Moduł główny PyO3 (lib.rs)

```rust
use pyo3::prelude::*;

mod scanner;
mod file_utils;
mod asset_builder;
mod types;

use scanner::RustAssetRepository;

/// Moduł Rust Scanner dla PyO3
#[pymodule]
fn scanner_rust(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<RustAssetRepository>()?;
    Ok(())
}
```

### 8. Integracja z Python

#### Plik integracyjny (core/rust_scanner.py)

```python
"""
Wrapper dla Rust Scanner - zapewnia kompatybilność z istniejącym API
"""
import scanner_rust
from typing import List, Dict, Optional, Callable
import logging

logger = logging.getLogger(__name__)

class RustAssetRepository:
    """
    Wrapper dla Rust implementacji AssetRepository
    Zachowuje kompatybilność z istniejącym API Python
    """

    def __init__(self):
        self._rust_scanner = scanner_rust.RustAssetRepository()
        logger.info("Rust scanner zainicjalizowany")

    def find_and_create_assets(
        self,
        folder_path: str,
        progress_callback: Optional[Callable] = None,
        use_async_thumbnails: bool = False
    ) -> List[Dict]:
        """
        Znajdź i utwórz asset-y w określonym folderze

        Args:
            folder_path: Ścieżka do folderu
            progress_callback: Callback postępu
            use_async_thumbnails: Nieużywane w wersji Rust

        Returns:
            Lista asset-ów
        """
        try:
            return self._rust_scanner.find_and_create_assets(folder_path, progress_callback)
        except Exception as e:
            logger.error(f"Błąd Rust scanner: {e}")
            return []

    def load_existing_assets(self, folder_path: str) -> List[Dict]:
        """
        Ładuj istniejące asset-y z folderu

        Args:
            folder_path: Ścieżka do folderu

        Returns:
            Lista asset-ów
        """
        try:
            return self._rust_scanner.load_existing_assets(folder_path)
        except Exception as e:
            logger.error(f"Błąd ładowania asset-ów: {e}")
            return []

    def scan_folder_for_files(self, folder_path: str) -> tuple:
        """
        Skanuj folder w poszukiwaniu plików

        Args:
            folder_path: Ścieżka do folderu

        Returns:
            Tuple (archive_by_name, image_by_name)
        """
        try:
            return self._rust_scanner.scan_folder_for_files(folder_path)
        except Exception as e:
            logger.error(f"Błąd skanowania folderu: {e}")
            return ({}, {})

    # Metody pomocnicze dla kompatybilności
    def _validate_folder_path_static(self, folder_path: str) -> bool:
        """Walidacja ścieżki folderu"""
        import os
        return bool(folder_path and os.path.exists(folder_path) and os.path.isdir(folder_path))

    def create_thumbnail_for_asset(self, asset_path: str, image_path: str) -> Optional[str]:
        """
        Tworzenie thumbnail - pozostaje w Python
        (integracja z istniejącym kodem thumbnail)
        """
        try:
            from core.thumbnail import generate_thumbnail
            result = generate_thumbnail(image_path)
            if result and len(result) == 2:
                return result[0]
            return None
        except Exception as e:
            logger.error(f"Błąd tworzenia thumbnail: {e}")
            return None
```

#### Modyfikacja głównego scanera (core/scanner.py)

```python
# Na początku pliku, dodaj flagę konfiguracyjną
USE_RUST_SCANNER = True  # Flaga do włączenia/wyłączenia Rust scanner

# W klasie AssetRepository, dodaj metodę wyboru implementacji
class AssetRepository:
    def __init__(self, use_rust: bool = USE_RUST_SCANNER):
        self.use_rust = use_rust

        if self.use_rust:
            try:
                from core.rust_scanner import RustAssetRepository
                self._rust_repo = RustAssetRepository()
                logger.info("Używa Rust scanner")
            except ImportError as e:
                logger.warning(f"Nie można załadować Rust scanner: {e}")
                logger.info("Przechodzi na Python scanner")
                self.use_rust = False
                self._rust_repo = None

    def find_and_create_assets(
        self, folder_path: str, progress_callback=None, use_async_thumbnails=False
    ) -> list:
        """Główna metoda skanowania z automatycznym wyborem implementacji"""
        if self.use_rust and self._rust_repo:
            return self._rust_repo.find_and_create_assets(
                folder_path, progress_callback, use_async_thumbnails
            )
        else:
            # Oryginalny kod Python
            return self._python_find_and_create_assets(
                folder_path, progress_callback, use_async_thumbnails
            )

    def _python_find_and_create_assets(self, folder_path: str, progress_callback=None, use_async_thumbnails=False) -> list:
        """Oryginalna implementacja Python - zmieniona nazwa dla jasności"""
        # Tutaj pozostaje cały oryginalny kod Python
        # ... (reszta oryginalnego kodu)
```

## Instalacja i konfiguracja

### 1. Instalacja narzędzi

```bash
# Instalacja Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Instalacja maturin
pip install maturin

# Instalacja narzędzi do generowania type hints
pip install pyo3-stub-gen
```

### 2. Tworzenie projektu

```bash
# Utwórz folder projektu
mkdir scanner_rust
cd scanner_rust

# Inicjalizuj projekt Rust
cargo init --lib

# Skopiuj pliki konfiguracyjne
# (Cargo.toml i pyproject.toml z dokumentacji)
```

### 3. Build i instalacja

```bash
# Development build
maturin develop

# Release build
maturin develop --release

# Wheel build
maturin build --release
```

### 4. Generowanie type hints

```bash
# Generuj type hints dla IDE
pyo3-stub-gen scanner_rust --out stubs/
```

## Testy wydajności

### Script benchmarkowy

```python
"""
Benchmark Python vs Rust scanner
"""
import time
import os
import logging
from pathlib import Path

# Test folders setup
def create_test_data(base_path: str, num_files: int = 1000):
    """Tworzy testowe dane do benchmarku"""
    test_folder = Path(base_path) / "test_scan_data"
    test_folder.mkdir(exist_ok=True)

    # Utwórz testowe pliki
    for i in range(num_files):
        # Pliki archiwum
        archive_file = test_folder / f"test_asset_{i:04d}.zip"
        archive_file.touch()

        # Pliki obrazów
        image_file = test_folder / f"test_asset_{i:04d}.png"
        image_file.touch()

        # Niektóre niesparowane
        if i % 10 == 0:
            unpaired_archive = test_folder / f"unpaired_{i:04d}.zip"
            unpaired_archive.touch()

    return str(test_folder)

def benchmark_scanners():
    """Porównuje wydajność Python vs Rust scanner"""
    logging.basicConfig(level=logging.INFO)

    # Przygotuj dane testowe
    test_folder = create_test_data(".", 1000)

    # Import scanners
    from core.scanner import AssetRepository as PythonScanner
    from core.rust_scanner import RustAssetRepository as RustScanner

    # Benchmark Python scanner
    print("=== Python Scanner ===")
    python_scanner = PythonScanner(use_rust=False)

    start_time = time.time()
    python_results = python_scanner.find_and_create_assets(test_folder)
    python_time = time.time() - start_time

    print(f"Czas Python: {python_time:.2f}s")
    print(f"Znalezione asset-y: {len(python_results)}")

    # Benchmark Rust scanner
    print("\n=== Rust Scanner ===")
    rust_scanner = RustScanner()

    start_time = time.time()
    rust_results = rust_scanner.find_and_create_assets(test_folder)
    rust_time = time.time() - start_time

    print(f"Czas Rust: {rust_time:.2f}s")
    print(f"Znalezione asset-y: {len(rust_results)}")

    # Porównanie
    print(f"\n=== Porównanie ===")
    if rust_time > 0:
        speedup = python_time / rust_time
        print(f"Przyspieszenie: {speedup:.2f}x")

    # Cleanup
    import shutil
    shutil.rmtree(test_folder)

if __name__ == "__main__":
    benchmark_scanners()
```

## Oczekiwane korzyści

### Wydajność

- **5-10x szybsze** skanowanie dużych folderów
- **Równoległe przetwarzanie** plików z rayon
- **Zoptymalizowane operacje I/O**

### Pamięć

- **Niższe zużycie RAM** dzięki efektywnym strukturom Rust
- **Brak garbage collection** - deterministyczne zarządzanie pamięcią
- **Stack allocation** dla małych struktur

### Niezawodność

- **Kompilacja sprawdza błędy** - eliminacja runtime errors
- **Bezpieczeństwo pamięci** - brak segfaultów
- **Obsługa błędów** z Result<T, E>

### Kompatybilność

- **Zachowanie API** - drop-in replacement
- **Stopniowa migracja** - można włączać/wyłączać
- **Integracja z istniejącym kodem** - thumbnail, JSON utils

## Migracja krok po kroku

### Faza 1: Podstawowa implementacja

1. Utwórz projekt Rust
2. Implementuj podstawowe typy danych
3. Zaimplementuj skanowanie plików
4. Testy podstawowej funkcjonalności

### Faza 2: Integracja z Python

1. Dodaj wrapper PyO3
2. Implementuj progress callback
3. Dodaj obsługę błędów
4. Testy integracji

### Faza 3: Optymalizacja

1. Dodaj przetwarzanie równoległe
2. Zoptymalizuj operacje I/O
3. Benchmarki wydajności
4. Tuning parametrów

### Faza 4: Wdrożenie

1. Dodaj flagę konfiguracyjną
2. Testy regresji
3. Dokumentacja użytkowa
4. Monitoring w produkcji

## Troubleshooting

### Problemy z kompilacją

```bash
# Sprawdź wersję Rust
rustc --version

# Aktualizuj Rust
rustup update

# Wyczyść cache
cargo clean
```

### Problemy z PyO3

```bash
# Sprawdź wersję Python
python --version

# Reinstaluj maturin
pip uninstall maturin
pip install maturin

# Debug build
maturin develop --debug
```

### Problemy z wydajnością

```bash
# Profile build
cargo build --release
perf record target/release/scanner_rust
perf report
```

## Dalszy rozwój

### Możliwe rozszerzenia

- **Async I/O** z tokio
- **Cached scanning** - incremental updates
- **Distributed scanning** - network folders
- **Plugin system** - custom file types

### Integracja z innymi komponentami

- **Thumbnail generation** w Rust
- **JSON serialization** z serde
- **Compression** detection
- **Metadata extraction**

## Podsumowanie

Migracja scanera do Rust z PyO3 oferuje znaczące korzyści wydajnościowe przy zachowaniu pełnej kompatybilności z istniejącym kodem Python. Stopniowa migracja pozwala na bezpieczne wdrożenie bez ryzyka dla stabilności aplikacji.

**Kluczowe punkty:**

- Zachowanie API dla bezproblemowej integracji
- Znaczące przyspieszenie operacji I/O
- Lepsza niezawodność i bezpieczeństwo
- Możliwość dalszego rozwoju i optymalizacji
  </rewritten_file>
