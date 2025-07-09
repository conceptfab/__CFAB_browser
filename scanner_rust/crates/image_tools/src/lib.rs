use pyo3::prelude::*;
use image::{imageops::FilterType, GenericImageView};
use anyhow::{Result, anyhow};
use log::{debug, info, error};

mod build_info;
use build_info::{get_build_info, get_build_number, get_build_datetime, get_git_commit, get_module_number, get_module_info, get_log_prefix, format_log_message};

/// Resizes an image based on specific rules.
#[pyfunction]
fn resize_image(py: Python, file_path: String) -> PyResult<bool> {
    py.allow_threads(|| {
        debug!("Resizing image: {}", file_path);

        let img = image::open(&file_path)
            .map_err(|e| {
                error!("Failed to open image {}: {}", file_path, e);
                PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("Failed to open image {}: {}", file_path, e))
            })?;

        let (original_width, original_height) = img.dimensions();
        let (new_width, new_height) = calculate_new_size(original_width, original_height);

        if new_width >= original_width && new_height >= original_height {
            debug!("No resize needed for {}: {}x{}", file_path, original_width, original_height);
            return Ok(false);
        }

        info!("Resizing image {} from {}x{} to {}x{}", file_path, original_width, original_height, new_width, new_height);

        // Wybierz odpowiedni filtr w zależności od rozmiaru obrazu
        let filter = if new_width < 512 || new_height < 512 {
            FilterType::Triangle  // Szybszy dla mniejszych obrazów
        } else {
            FilterType::Lanczos3  // Lepsza jakość dla większych obrazów
        };

        let resized_img = img.resize(new_width, new_height, filter);

        resized_img.save(&file_path)
            .map_err(|e| {
                error!("Failed to save resized image {}: {}", file_path, e);
                PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("Failed to save resized image {}: {}", file_path, e))
            })?;

        debug!("Successfully resized image: {}", file_path);
        Ok(true)
    })
}

/// Converts an image to WebP format with optimized quality.
#[pyfunction]
#[pyo3(signature = (input_path, output_path, quality=None))]
fn convert_to_webp(py: Python, input_path: String, output_path: String, quality: Option<u8>) -> PyResult<bool> {
    py.allow_threads(|| {
        debug!("Converting image to WebP: {} -> {}", input_path, output_path);

        let img = image::open(&input_path)
            .map_err(|e| {
                error!("Failed to open image {}: {}", input_path, e);
                PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("Failed to open image {}: {}", input_path, e))
            })?;

        let dimensions = img.dimensions();
        let has_alpha = img.color().has_alpha();

        // Determine quality - default: 80 for images with alpha, 75 for others
        let webp_quality = quality.unwrap_or(if has_alpha { 80 } else { 75 }) as f32;

        info!("Converting {}x{} image to WebP (quality: {})", dimensions.0, dimensions.1, webp_quality);

        // Użyj biblioteki webp dla lepszej kontroli jakości
        if has_alpha {
            let rgba = img.to_rgba8();
            let encoder = webp::Encoder::from_rgba(rgba.as_raw(), rgba.width(), rgba.height());
            let webp_data = encoder.encode(webp_quality);
            std::fs::write(&output_path, &*webp_data)
                .map_err(|e| {
                    error!("Failed to save WebP image {}: {}", output_path, e);
                    PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("Failed to save WebP image {}: {}", output_path, e))
                })?;
        } else {
            // Bez przezroczystości, konwertuj do RGB dla mniejszego rozmiaru pliku
            let rgb = img.to_rgb8();
            let encoder = webp::Encoder::from_rgb(rgb.as_raw(), rgb.width(), rgb.height());
            let webp_data = encoder.encode(webp_quality);
            std::fs::write(&output_path, &*webp_data)
                .map_err(|e| {
                    error!("Failed to save WebP image {}: {}", output_path, e);
                    PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("Failed to save WebP image {}: {}", output_path, e))
                })?;
        }

        debug!("Successfully converted image to WebP: {}", output_path);
        Ok(true)
    })
}

/// Oblicza nowy rozmiar obrazu na podstawie specyficznych reguł.
/// 
/// # Reguły:
/// - Dla obrazów o podobnych proporcjach (różnica <= 30%): docelowo 1024px dla krótszego boku
/// - Dla obrazów o różnych proporcjach (różnica > 30%): docelowo 1600px dla dłuższego boku
/// - Nigdy nie powiększa obrazów, tylko zmniejsza je
fn calculate_new_size(width: u32, height: u32) -> (u32, u32) {
    // Obsługa edge case - małe obrazy
    if width == 0 || height == 0 || (width < 1024 && height < 1024) {
        return (width, height);
    }

    let max_side = width.max(height);
    let min_side = width.min(height);

    // Bezpieczne obliczanie procentu - unika dzielenia przez zero
    let difference_percent = if max_side > 0 {
        ((max_side - min_side) as f32 / max_side as f32) * 100.0
    } else {
        0.0
    };

    // Skorzystaj z wyższego poziomu optymalizacji dla często używanych warunków
    let (new_width, new_height) = match (difference_percent <= 30.0, width <= height) {
        // Podobne proporcje, szerokość <= wysokość
        (true, true) => {
            let scale = 1024.0 / width as f32;
            (1024, (height as f32 * scale).round() as u32)
        },
        // Podobne proporcje, szerokość > wysokość
        (true, false) => {
            let scale = 1024.0 / height as f32;
            ((width as f32 * scale).round() as u32, 1024)
        },
        // Różne proporcje, szerokość >= wysokość
        (false, false) => {
            let scale = 1600.0 / width as f32;
            (1600, (height as f32 * scale).round() as u32)
        },
        // Różne proporcje, szerokość < wysokość
        (false, true) => {
            let scale = 1600.0 / height as f32;
            ((width as f32 * scale).round() as u32, 1600)
        }
    };

    // Nigdy nie powiększaj, tylko zmniejszaj
    if new_width >= width || new_height >= height {
        (width, height)
    } else {
        (new_width, new_height)
    }
}

/// Generuje miniaturę obrazu w formacie WebP z dostosowanym rozmiarem.
#[pyfunction]
#[pyo3(signature = (image_path, size=None, cache_dir=None))]
fn generate_thumbnail(py: Python, image_path: String, size: Option<u32>, cache_dir: Option<String>) -> PyResult<(String, u32)> {
    py.allow_threads(|| {
        let size = size.unwrap_or(256);
        let cache_dir_name = cache_dir.unwrap_or(".cache".to_string());

        debug!("Generating thumbnail for {} (size: {}px, cache: {})", image_path, size, cache_dir_name);

        // Funkcja przetwarzająca błędy z anyhow na PyErr
        let process_result = || -> Result<(String, u32)> {
            // Walidacja parametrów
            if image_path.is_empty() {
                return Err(anyhow!("Image path cannot be empty"));
            }

            let path = std::path::Path::new(&image_path);
            if !path.exists() {
                return Err(anyhow!("File does not exist: {}", image_path));
            }

            // Sprawdź rozszerzenie pliku
            let supported_formats = [".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff", ".tga"];
            let ext = path.extension()
                .and_then(|s| s.to_str())
                .map(|s| format!(".{}", s.to_lowercase()))
                .unwrap_or_default();

            if !supported_formats.contains(&ext.as_str()) {
                return Err(anyhow!("Unsupported format: {}", ext));
            }

            // Ścieżka miniatury
            let file_stem = path.file_stem()
                .and_then(|s| s.to_str())
                .ok_or_else(|| anyhow!("Cannot get file name"))?;

            let cache_dir = path.parent()
                .ok_or_else(|| anyhow!("Cannot get parent directory"))?  
                .join(&cache_dir_name);

            let thumbnail_path = cache_dir.join(format!("{}.thumb", file_stem));

            // Sprawdź czy miniatura jest aktualna
            if thumbnail_path.exists() {
                if let (Ok(image_time), Ok(thumb_time)) = (
                    std::fs::metadata(path).and_then(|m| m.modified()),
                    std::fs::metadata(&thumbnail_path).and_then(|m| m.modified())
                ) {
                    if thumb_time >= image_time {
                        // Miniatura jest aktualna
                        return Ok((
                            thumbnail_path.file_name()
                                .and_then(|s| s.to_str())
                                .unwrap_or("").to_string(),
                            size
                        ));
                    }
                }
            }

            // Stwórz katalog cache jeśli nie istnieje
            std::fs::create_dir_all(&cache_dir)?;

            // Wczytaj obraz
            let img = image::open(path)?;
            let has_alpha = img.color().has_alpha();

            // Zmień rozmiar do kwadratu z przycinaniem
            let (width, height) = img.dimensions();

            // Oblicz skalę, aby krótsza strona miała rozmiar 'size'
            let scale = size as f32 / (width.min(height) as f32);
            let new_width = (width as f32 * scale).round() as u32;
            let new_height = (height as f32 * scale).round() as u32;

            // Wybierz filtr w zależności od rozmiaru
            let filter = if size <= 128 {
                FilterType::Triangle  // Szybszy dla małych miniatur
            } else {
                FilterType::Lanczos3   // Lepsza jakość dla większych
            };

            let resized = img.resize(new_width, new_height, filter);

            // Przytnij do kwadratu (od góry i od lewej)
            let crop_x = if new_width > size { 0 } else { 0 };
            let crop_y = if new_height > size { 0 } else { 0 };
            let crop_width = new_width.min(size);
            let crop_height = new_height.min(size);

            let thumbnail = resized.crop_imm(crop_x, crop_y, crop_width, crop_height);

            // Jeśli wynik nie jest kwadratem o żądanym rozmiarze, dostosuj
            let final_thumbnail = if thumbnail.width() != size || thumbnail.height() != size {
                thumbnail.resize_exact(size, size, filter)
            } else {
                thumbnail
            };

            // Zapisz jako WebP
            let quality = if has_alpha { 80.0 } else { 75.0 };

            if has_alpha {
                let rgba_img = final_thumbnail.to_rgba8();
                let encoder = webp::Encoder::from_rgba(rgba_img.as_raw(), rgba_img.width(), rgba_img.height());
                let webp_data = encoder.encode(quality);
                std::fs::write(&thumbnail_path, &*webp_data)?;
            } else {
                let rgb_img = final_thumbnail.to_rgb8();
                let encoder = webp::Encoder::from_rgb(rgb_img.as_raw(), rgb_img.width(), rgb_img.height());
                let webp_data = encoder.encode(quality);
                std::fs::write(&thumbnail_path, &*webp_data)?;
            }

            Ok((
                thumbnail_path.file_name()
                    .and_then(|s| s.to_str())
                    .unwrap_or("").to_string(),
                size
            ))
        };

        // Konwertuj Result<T, anyhow::Error> na PyResult<T>
        process_result().map_err(|e| {
            error!("Thumbnail generation error: {}", e);
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Failed to generate thumbnail: {}", e))
        })
    })
}

#[pymodule]
fn image_tools(m: &Bound<'_, PyModule>) -> PyResult<()> {
    // Inicjalizacja loggera
    let _ = env_logger::try_init();

    // Informacje o inicjalizacji modułu
    info!("🦀 Rust Image Tools module initialized [build: {}, module: {}]", 
          env!("VERGEN_BUILD_TIMESTAMP"), 3);

    // Add main functions
    m.add_function(wrap_pyfunction!(resize_image, m)?)?;
    m.add_function(wrap_pyfunction!(convert_to_webp, m)?)?;
    m.add_function(wrap_pyfunction!(generate_thumbnail, m)?)?;
    
    // Add build information functions
    m.add_function(wrap_pyfunction!(get_build_info, m)?)?;
    m.add_function(wrap_pyfunction!(get_build_number, m)?)?;
    m.add_function(wrap_pyfunction!(get_build_datetime, m)?)?;
    m.add_function(wrap_pyfunction!(get_git_commit, m)?)?;
    m.add_function(wrap_pyfunction!(get_module_number, m)?)?;
    m.add_function(wrap_pyfunction!(get_module_info, m)?)?;
    m.add_function(wrap_pyfunction!(get_log_prefix, m)?)?;
    m.add_function(wrap_pyfunction!(format_log_message, m)?)?;
    
    Ok(())
} 