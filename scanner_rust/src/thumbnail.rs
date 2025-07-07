use image::{DynamicImage, imageops::FilterType, GenericImageView};
use std::path::Path;
use std::fs;
use std::time::SystemTime;
use std::sync::OnceLock;
use anyhow::{Result, anyhow};

/// Generator miniaturek - dokładnie jak w Pythonie
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

    /// Sprawdza czy miniaturka jest aktualna (nowsza niż oryginał)
    fn is_thumbnail_current(&self, image_path: &Path, thumbnail_path: &Path) -> bool {
        if !thumbnail_path.exists() {
            return false;
        }

        match (fs::metadata(image_path), fs::metadata(thumbnail_path)) {
            (Ok(image_meta), Ok(thumb_meta)) => {
                match (image_meta.modified(), thumb_meta.modified()) {
                    (Ok(image_time), Ok(thumb_time)) => thumb_time >= image_time,
                    _ => false,
                }
            }
            _ => false,
        }
    }

    /// KRYTYCZNA FUNKCJA: Przeskalowanie do kwadratu z przycinaniem
    /// IDENTYCZNA LOGIKA JAK W PYTHONIE - NIE ZMIENIAĆ!
    fn resize_to_square(&self, img: DynamicImage, size: u32) -> Result<DynamicImage> {
        if size == 0 {
            return Err(anyhow!("Rozmiar miniaturki nie może być zerem"));
        }
        
        let (width, height) = img.dimensions();
        
        if width == 0 || height == 0 {
            return Err(anyhow!("Obraz ma nieprawidłowe wymiary: {}x{}", width, height));
        }
        
        // Oblicz współczynnik skalowania
        let scale = size as f32 / (width.min(height) as f32);
        let new_width = (width as f32 * scale) as u32;
        let new_height = (height as f32 * scale) as u32;

        // Przeskaluj używając Lanczos (jak w Pythonie)
        let resized = img.resize(new_width, new_height, FilterType::Lanczos3);

        // Przyciąć do kwadratu zgodnie z wymaganiami:
        // - Wysokie obrazy: przycięcie od GÓRY (górny lewy róg)
        // - Szerokie obrazy: przycięcie od LEWEJ (górny lewy róg)
        let result = if new_width > size {
            // Szerokie obrazy - przycinaj od lewej strony (górny lewy róg)
            resized.crop_imm(0, 0, size, size)
        } else if new_height > size {
            // Wysokie obrazy - przycinaj od góry (górny lewy róg)  
            resized.crop_imm(0, 0, size, size)
        } else {
            resized
        };
        
        Ok(result)
    }

    /// Zapisz miniaturkę jako WebP z kontrolą jakości (ZGODNIE Z PYTHONEM)
    fn save_webp_with_quality(&self, thumbnail: &DynamicImage, path: &Path, has_alpha: bool) -> Result<()> {
        let quality = self.get_webp_quality(has_alpha);
        
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

    /// Główna funkcja generowania miniaturki
    pub fn generate_thumbnail(&self, image_path: &str) -> Result<(String, u32)> {
        // Walidacja
        if image_path.is_empty() {
            return Err(anyhow!("Nieprawidłowa ścieżka obrazu: {}", image_path));
        }

        let path = Path::new(image_path);
        if !path.exists() {
            return Err(anyhow!("Plik nie istnieje: {}", image_path));
        }

        // Sprawdź rozszerzenie
        let supported_formats = [".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff", ".tga"];
        let ext = path.extension()
            .and_then(|s| s.to_str())
            .map(|s| format!(".{}", s.to_lowercase()))
            .unwrap_or_default();
        
        if !supported_formats.contains(&ext.as_str()) {
            return Err(anyhow!("Nieobsługiwany format: {}", ext));
        }

        // Utwórz katalog cache jeśli nie istnieje
        let cache_dir = path.parent()
            .ok_or_else(|| anyhow!("Nie można pobrać katalogu nadrzędnego"))?
            .join(&self.cache_dir_name);
        
        fs::create_dir_all(&cache_dir)?;

        // Ścieżka miniaturki
        let file_stem = path.file_stem()
            .and_then(|s| s.to_str())
            .ok_or_else(|| anyhow!("Nie można pobrać nazwy pliku"))?;
        
        let thumbnail_path = cache_dir.join(format!("{}.thumb", file_stem));

        // Sprawdź czy miniaturka już istnieje i jest aktualna
        if self.is_thumbnail_current(path, &thumbnail_path) {
            return Ok((
                thumbnail_path.file_name()
                    .and_then(|s| s.to_str())
                    .unwrap_or("").to_string(),
                self.thumbnail_size
            ));
        }

        // Wczytaj obraz
        let img = image::open(path)
            .map_err(|e| anyhow!("Błąd wczytywania obrazu {}: {}", image_path, e))?;

        // Sprawdź przezroczystość
        let has_alpha = self.has_transparency(&img);

        // Konwertuj do odpowiedniego formatu koloru
        let processed_img = if has_alpha {
            img.to_rgba8().into()
        } else {
            img.to_rgb8().into()
        };

        // Przeskaluj do kwadratu (KRYTYCZNA LOGIKA!)
        let thumbnail = self.resize_to_square(processed_img, self.thumbnail_size)?;

        // Zapisz jako WebP z kontrolowaną jakością (ZGODNIE Z PYTHONEM)
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