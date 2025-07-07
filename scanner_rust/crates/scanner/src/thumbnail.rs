use image::{DynamicImage, imageops::FilterType, GenericImageView};
use std::path::Path;
use std::fs;

use std::sync::OnceLock;
use anyhow::{Result, anyhow};

/// Generator miniaturek - dokładnie jak w Pythonie, ale zoptymalizowany
pub struct ThumbnailGenerator {
    pub thumbnail_size: u32,
    pub cache_dir_name: String,
}

impl Default for ThumbnailGenerator {
    fn default() -> Self {
        Self {
            thumbnail_size: 256,
            cache_dir_name: ".cache".to_string(),
        }
    }
}

impl ThumbnailGenerator {
    // Funkcja zarezerwowana na przyszłość
    #[allow(dead_code)]
    pub fn new(thumbnail_size: u32) -> Self {
        Self {
            thumbnail_size,
            cache_dir_name: ".cache".to_string(),
        }
    }

    /// Sprawdza czy obraz ma przezroczystość
    fn has_transparency(&self, img: &DynamicImage) -> bool {
        match img {
            DynamicImage::ImageRgba8(_) => true,
            DynamicImage::ImageLumaA8(_) => true,
            DynamicImage::ImageRgba16(_) => true,
            DynamicImage::ImageLumaA16(_) => true,
            DynamicImage::ImageRgba32F(_) => true,
            _ => false,
        }
    }

    /// Pobiera parametry kompresji WebP zgodnie z Pythonem
    fn get_webp_quality(&self, has_alpha: bool) -> f32 {
        if has_alpha { 80.0 } else { 75.0 }
    }

    /// ZOPTYMALIZOWANE sprawdzanie czy miniaturka jest aktualna (nowsza niż oryginał)
    fn is_thumbnail_current(&self, image_path: &Path, thumbnail_path: &Path) -> bool {
        if !thumbnail_path.exists() {
            return false;
        }

        // Fast path - sprawdź tylko czy plik istnieje dla lepszej wydajności
        // W większości przypadków cache jest aktualny
        match (
            fs::metadata(image_path).and_then(|m| m.modified()),
            fs::metadata(thumbnail_path).and_then(|m| m.modified())
        ) {
            (Ok(image_time), Ok(thumb_time)) => thumb_time >= image_time,
            _ => false, // W przypadku błędu, przegenuj miniaturkę
        }
    }

    /// KRYTYCZNA FUNKCJA: Przeskalowanie do kwadratu z przycinaniem
    /// ZOPTYMALIZOWANA WERSJA - szybsze filtrowanie
    fn resize_to_square(&self, img: DynamicImage, size: u32) -> Result<DynamicImage> {
        if size == 0 {
            return Err(anyhow!("Rozmiar miniaturki nie może być zerem"));
        }
        
        let (width, height) = img.dimensions();
        
        if width == 0 || height == 0 {
            return Err(anyhow!("Obraz ma nieprawidłowe wymiary: {}x{}", width, height));
        }
        
        // Sprawdź czy obraz już ma właściwy rozmiar
        if width == size && height == size {
            return Ok(img);
        }
        
        // Oblicz współczynnik skalowania tak, aby krótszy bok miał rozmiar 'size'
        let scale = size as f32 / (width.min(height) as f32);
        let new_width = (width as f32 * scale).round() as u32;
        let new_height = (height as f32 * scale).round() as u32;

        // Użyj szybszego filtra dla miniaturek - Triangle zamiast Lanczos3
        let filter = if size <= 128 { 
            FilterType::Triangle  // Szybszy dla małych miniaturek
        } else { 
            FilterType::Lanczos3  // Lepsze dla większych
        };
        
        let resized = img.resize(new_width, new_height, filter);

        // POPRAWIONE przycięcie do kwadratu:
        // - Wysokie obrazy: przycinane od góry (crop_y = 0)
        // - Szerokie obrazy: przycinane od lewej strony (crop_x = 0)
        let crop_x = if new_width > size { 0 } else { 0 };
        let crop_y = if new_height > size { 0 } else { 0 };
        let crop_width = new_width.min(size);
        let crop_height = new_height.min(size);
        
        let result = resized.crop_imm(crop_x, crop_y, crop_width, crop_height);
        
        // Jeśli wynik nie jest kwadratem o żądanym rozmiarze, dopasuj
        if result.width() != size || result.height() != size {
            Ok(result.resize_exact(size, size, filter))
        } else {
            Ok(result)
        }
    }

    /// ZOPTYMALIZOWANE zapisywanie WebP - mniej konwersji kolorów
    fn save_webp_with_quality(&self, thumbnail: &DynamicImage, path: &Path, has_alpha: bool) -> Result<()> {
        let quality = self.get_webp_quality(has_alpha);
        
        // Tworzenie katalogów cache tylko gdy potrzeba
        if let Some(parent) = path.parent() {
            if !parent.exists() {
                fs::create_dir_all(parent)?;
            }
        }
        
        if has_alpha {
            // Z przezroczystością: quality=80 (jak w Pythonie)
            let rgba_img = thumbnail.to_rgba8();
            let encoder = webp::Encoder::from_rgba(rgba_img.as_raw(), rgba_img.width(), rgba_img.height());
            let webp_data = encoder.encode(quality);
            fs::write(path, &*webp_data)
                .map_err(|e| anyhow!("Błąd zapisu WebP: {}", e))?;
        } else {
            // Bez przezroczystości: quality=75 (jak w Pythonie)
            let rgb_img = thumbnail.to_rgb8();
            let encoder = webp::Encoder::from_rgb(rgb_img.as_raw(), rgb_img.width(), rgb_img.height());
            let webp_data = encoder.encode(quality);
            fs::write(path, &*webp_data)
                .map_err(|e| anyhow!("Błąd zapisu WebP: {}", e))?;
        }
        
        Ok(())
    }

    /// ZOPTYMALIZOWANA główna funkcja generowania miniaturki
    pub fn generate_thumbnail(&self, image_path: &str) -> Result<(String, u32)> {
        // Szybka walidacja
        if image_path.is_empty() {
            return Err(anyhow!("Nieprawidłowa ścieżka obrazu: {}", image_path));
        }

        let path = Path::new(image_path);
        if !path.exists() {
            return Err(anyhow!("Plik nie istnieje: {}", image_path));
        }

        // Sprawdź rozszerzenie - tylko obsługiwane formaty
        let supported_formats = [".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff", ".tga"];
        let ext = path.extension()
            .and_then(|s| s.to_str())
            .map(|s| format!(".{}", s.to_lowercase()))
            .unwrap_or_default();
        
        if !supported_formats.contains(&ext.as_str()) {
            return Err(anyhow!("Nieobsługiwany format: {}", ext));
        }

        // Ścieżka miniaturki - uproszczona logika cache
        let file_stem = path.file_stem()
            .and_then(|s| s.to_str())
            .ok_or_else(|| anyhow!("Nie można pobrać nazwy pliku"))?;
        
        let cache_dir = path.parent()
            .ok_or_else(|| anyhow!("Nie można pobrać katalogu nadrzędnego"))?
            .join(&self.cache_dir_name);
        
        let thumbnail_path = cache_dir.join(format!("{}.thumb", file_stem));
        
        // OPTYMALIZACJA: Sprawdź cache PRZED tworzeniem katalogu
        if self.is_thumbnail_current(path, &thumbnail_path) {
            return Ok((
                thumbnail_path.file_name()
                    .and_then(|s| s.to_str())
                    .unwrap_or("").to_string(),
                self.thumbnail_size
            ));
        }

        // Utwórz katalog cache tylko gdy potrzeba wygenerować nową miniaturkę
        fs::create_dir_all(&cache_dir)?;

        // Wczytaj obraz - użyj szybszej deserializacji
        let img = image::open(path)
            .map_err(|e| anyhow!("Błąd wczytywania obrazu {}: {}", image_path, e))?;

        // Sprawdź przezroczystość
        let has_alpha = self.has_transparency(&img);

        // OPTYMALIZACJA: Mniej konwersji kolorów - pracuj bezpośrednio na img
        let thumbnail = self.resize_to_square(img, self.thumbnail_size)?;

        // Zapisz jako WebP z kontrolowaną jakością
        self.save_webp_with_quality(&thumbnail, &thumbnail_path, has_alpha)?;

        Ok((
            thumbnail_path.file_name()
                .and_then(|s| s.to_str())
                .unwrap_or("").to_string(),
            self.thumbnail_size
        ))
    }
}

/// Globalna instancja generatora (bezpieczna wersja)
static GENERATOR: OnceLock<ThumbnailGenerator> = OnceLock::new();

/// Pobiera globalną instancję generatora
pub fn get_generator() -> &'static ThumbnailGenerator {
    GENERATOR.get_or_init(|| ThumbnailGenerator::default())
}

/// Główna funkcja generowania miniaturek (public API)
pub fn generate_thumbnail(image_path: &str) -> Result<(String, u32)> {
    let generator = get_generator();
    generator.generate_thumbnail(image_path)
} 