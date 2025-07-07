Główne problemy do naprawienia:
1. Problem z thread safety w thumbnail.rs
Plik: scanner_rust/src/thumbnail.rs
Problem: Użycie unsafe static bez synchronizacji
rust// OBECNY KOD (niebezpieczny)
static mut GENERATOR: Option<ThumbnailGenerator> = None;
static INIT: std::sync::Once = std::sync::Once::new();

pub fn get_generator() -> &'static ThumbnailGenerator {
    unsafe {
        INIT.call_once(|| {
            GENERATOR = Some(ThumbnailGenerator::default());
        });
        GENERATOR.as_ref().unwrap()
    }
}

// POPRAWIONY KOD (bezpieczny)
use std::sync::OnceLock;

static GENERATOR: OnceLock<ThumbnailGenerator> = OnceLock::new();

pub fn get_generator() -> &'static ThumbnailGenerator {
    GENERATOR.get_or_init(|| ThumbnailGenerator::default())
}
2. Optymalizacja obsługi błędów w scanner.rs
Plik: scanner_rust/src/scanner.rs
Funkcja: find_and_create_assets
rust// OBECNY KOD (verbose)
.map_err(|e| PyErr::new::<PyRuntimeError, _>(format!("Scan error: {}", e)))?;

// POPRAWIONY KOD (używając makra)
macro_rules! py_runtime_error {
    ($msg:expr) => {
        PyErr::new::<PyRuntimeError, _>($msg)
    };
    ($fmt:expr, $($arg:tt)*) => {
        PyErr::new::<PyRuntimeError, _>(format!($fmt, $($arg)*))
    };
}

// Użycie:
.map_err(|e| py_runtime_error!("Scan error: {}", e))?;
3. Dodanie walidacji w asset_builder.rs
Plik: scanner_rust/src/asset_builder.rs
Funkcja: create_single_asset
rust// DODAJ na początku funkcji create_single_asset
pub fn create_single_asset(
    &self,
    name: &str,
    archive_path: &Path,
    image_path: &Path,
    folder_path: &Path,
) -> Result<Asset> {
    // NOWA WALIDACJA
    self.validate_asset_inputs(name, archive_path, image_path, folder_path)?;
    
    let size_mb = file_utils::get_file_size_mb(archive_path)?;
    // ... reszta kodu bez zmian
}
4. Optymalizacja wydajności - parallel processing
Plik: scanner_rust/src/scanner.rs
Funkcja: find_and_create_assets
rust// DODAJ do Cargo.toml:
// rayon = "1.7"

// NOWY KOD z parallel processing
use rayon::prelude::*;

// W funkcji find_and_create_assets, zamień pętlę for na:
let created_assets: Vec<_> = common_names
    .par_iter()
    .enumerate()
    .filter_map(|(i, name)| {
        let current_progress = ((i as f32 / total_assets as f32) * 80.0) as i32 + 10;
        
        // Progress callback (zachowaj istniejący kod)
        if let Some(ref callback) = progress_callback {
            if let Err(e) = callback.call1(py, (current_progress, 100, format!("Creating asset: {}", name))) {
                eprintln!("Progress callback error: {:?}", e);
            }
        }

        if let (Some(archive_path), Some(image_path)) = 
            (archive_by_name.get(name), image_by_name.get(name)) {
            
            match self.asset_builder.create_single_asset(name, archive_path, image_path, folder_path) {
                Ok(asset) => {
                    // Zapisz asset (zachowaj istniejący kod)
                    let asset_file_path = folder_path.join(format!("{}.asset", name));
                    if let Err(e) = self.asset_builder.save_asset_to_file(&asset, &asset_file_path) {
                        eprintln!("Error saving asset {}: {:?}", name, e);
                        return None;
                    }
                    
                    // Konwersja do PyObject (zachowaj istniejący kod konwersji)
                    Some(create_py_dict_from_asset(py, &asset))
                }
                Err(e) => {
                    eprintln!("Error creating asset {}: {:?}", name, e);
                    None
                }
            }
        } else {
            None
        }
    })
    .collect();
5. Lepsze error handling w thumbnail.rs
Plik: scanner_rust/src/thumbnail.rs
Funkcja: resize_to_square
rust// POPRAWIONY KOD z lepszą obsługą błędów
fn resize_to_square(&self, img: DynamicImage, size: u32) -> Result<DynamicImage> {
    if size == 0 {
        return Err(anyhow!("Rozmiar miniaturki nie może być zerem"));
    }
    
    let (width, height) = img.dimensions();
    
    if width == 0 || height == 0 {
        return Err(anyhow!("Obraz ma nieprawidłowe wymiary: {}x{}", width, height));
    }
    
    // Reszta kodu bez zmian...
    let scale = size as f32 / (width.min(height) as f32);
    let new_width = (width as f32 * scale) as u32;
    let new_height = (height as f32 * scale) as u32;

    let resized = img.resize(new_width, new_height, FilterType::Lanczos3);

    let result = if new_width > size {
        resized.crop_imm(0, 0, size, size)
    } else if new_height > size {
        resized.crop_imm(0, 0, size, size)
    } else {
        resized
    };
    
    Ok(result)
}
6. Dodanie configuration struct
Plik: scanner_rust/src/types.rs
Dodaj nową strukturę:
rust// NOWA STRUKTURA konfiguracyjna
#[derive(Debug, Clone)]
pub struct ScannerConfig {
    pub thumbnail_size: u32,
    pub parallel_processing: bool,
    pub cache_dir_name: String,
    pub file_extensions: FileExtensions,
}

impl Default for ScannerConfig {
    fn default() -> Self {
        Self {
            thumbnail_size: 256,
            parallel_processing: true,
            cache_dir_name: ".cache".to_string(),
            file_extensions: FileExtensions::default(),
        }
    }
}
Wymagane zmiany w Cargo.toml:
toml[dependencies]
# Istniejące dependencies...
rayon = "1.7"  # dla parallel processing
Podsumowanie ulepszeń:

Bezpieczeństwo: Usunięcie unsafe kodu w thumbnail.rs
Wydajność: Parallel processing dla dużych folderów
Obsługa błędów: Lepsze error handling i walidacja
Czytelność: Makra dla powtarzającego się kodu
Konfigurowalność: Dodanie struktury konfiguracyjnej

Kod po tych zmianach będzie bardziej bezpieczny, wydajny i łatwiejszy w utrzymaniu.