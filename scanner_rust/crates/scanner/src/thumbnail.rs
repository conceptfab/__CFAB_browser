use image::{DynamicImage, imageops::FilterType, GenericImageView};
use std::path::Path;
use std::fs;

use std::sync::OnceLock;
use anyhow::{Result, anyhow};

/// Thumbnail generator - exactly like in Python, but optimized
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
    // Function reserved for future use
    #[allow(dead_code)]
    pub fn new(thumbnail_size: u32) -> Self {
        Self {
            thumbnail_size,
            cache_dir_name: ".cache".to_string(),
        }
    }

    /// Checks if image has transparency
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

    /// Gets WebP compression parameters according to Python
    fn get_webp_quality(&self, has_alpha: bool) -> f32 {
        if has_alpha { 80.0 } else { 75.0 }
    }

    /// OPTIMIZED checking if thumbnail is current (newer than original)
    fn is_thumbnail_current(&self, image_path: &Path, thumbnail_path: &Path) -> bool {
        if !thumbnail_path.exists() {
            return false;
        }

        // Fast path - check only if file exists for better performance
        // In most cases cache is current
        match (
            fs::metadata(image_path).and_then(|m| m.modified()),
            fs::metadata(thumbnail_path).and_then(|m| m.modified())
        ) {
            (Ok(image_time), Ok(thumb_time)) => thumb_time >= image_time,
            _ => false, // In case of error, regenerate thumbnail
        }
    }

    /// CRITICAL FUNCTION: Resize to square with cropping
    /// OPTIMIZED VERSION - faster filtering
    fn resize_to_square(&self, img: DynamicImage, size: u32) -> Result<DynamicImage> {
        if size == 0 {
            return Err(anyhow!("Thumbnail size cannot be zero"));
        }
        
        let (width, height) = img.dimensions();
        
        if width == 0 || height == 0 {
            return Err(anyhow!("Image has invalid dimensions: {}x{}", width, height));
        }
        
        // Check if image already has proper size
        if width == size && height == size {
            return Ok(img);
        }
        
        // Calculate scaling factor so that shorter side has 'size' dimension
        let scale = size as f32 / (width.min(height) as f32);
        let new_width = (width as f32 * scale).round() as u32;
        let new_height = (height as f32 * scale).round() as u32;

        // Use faster filter for thumbnails - Triangle instead of Lanczos3
        let filter = if size <= 128 { 
            FilterType::Triangle  // Faster for small thumbnails
        } else { 
            FilterType::Lanczos3  // Better for larger ones
        };
        
        let resized = img.resize(new_width, new_height, filter);

        // FIXED cropping to square:
        // - Tall images: cropped from top (crop_y = 0)
        // - Wide images: cropped from left side (crop_x = 0)
        let crop_x = if new_width > size { 0 } else { 0 };
        let crop_y = if new_height > size { 0 } else { 0 };
        let crop_width = new_width.min(size);
        let crop_height = new_height.min(size);
        
        let result = resized.crop_imm(crop_x, crop_y, crop_width, crop_height);
        
        // If result is not a square of desired size, adjust
        if result.width() != size || result.height() != size {
            Ok(result.resize_exact(size, size, filter))
        } else {
            Ok(result)
        }
    }

    /// OPTIMIZED WebP saving - fewer color conversions
    fn save_webp_with_quality(&self, thumbnail: &DynamicImage, path: &Path, has_alpha: bool) -> Result<()> {
        let quality = self.get_webp_quality(has_alpha);
        
        // Create cache directories only when needed
        if let Some(parent) = path.parent() {
            if !parent.exists() {
                fs::create_dir_all(parent)?;
            }
        }
        
        if has_alpha {
            // With transparency: quality=80 (like in Python)
            let rgba_img = thumbnail.to_rgba8();
            let encoder = webp::Encoder::from_rgba(rgba_img.as_raw(), rgba_img.width(), rgba_img.height());
            let webp_data = encoder.encode(quality);
            fs::write(path, &*webp_data)
                .map_err(|e| anyhow!("WebP save error: {}", e))?;
        } else {
            // Without transparency: quality=75 (like in Python)
            let rgb_img = thumbnail.to_rgb8();
            let encoder = webp::Encoder::from_rgb(rgb_img.as_raw(), rgb_img.width(), rgb_img.height());
            let webp_data = encoder.encode(quality);
            fs::write(path, &*webp_data)
                .map_err(|e| anyhow!("WebP save error: {}", e))?;
        }
        
        Ok(())
    }

    /// OPTIMIZED main thumbnail generation function
    pub fn generate_thumbnail(&self, image_path: &str) -> Result<(String, u32)> {
        // Quick validation
        if image_path.is_empty() {
            return Err(anyhow!("Invalid image path: {}", image_path));
        }

        let path = Path::new(image_path);
        if !path.exists() {
            return Err(anyhow!("File does not exist: {}", image_path));
        }

        // Check extension - only supported formats
        let supported_formats = [".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff", ".tga"];
        let ext = path.extension()
            .and_then(|s| s.to_str())
            .map(|s| format!(".{}", s.to_lowercase()))
            .unwrap_or_default();
        
        if !supported_formats.contains(&ext.as_str()) {
            return Err(anyhow!("Unsupported format: {}", ext));
        }

        // Thumbnail path - simplified cache logic
        let file_stem = path.file_stem()
            .and_then(|s| s.to_str())
            .ok_or_else(|| anyhow!("Cannot get file name"))?;
        
        let cache_dir = path.parent()
            .ok_or_else(|| anyhow!("Cannot get parent directory"))?
            .join(&self.cache_dir_name);
        
        let thumbnail_path = cache_dir.join(format!("{}.thumb", file_stem));
        
        // OPTIMIZATION: Check cache BEFORE creating directory
        if self.is_thumbnail_current(path, &thumbnail_path) {
            return Ok((
                thumbnail_path.file_name()
                    .and_then(|s| s.to_str())
                    .unwrap_or("").to_string(),
                self.thumbnail_size
            ));
        }

        // Create cache directory only when need to generate new thumbnail
        fs::create_dir_all(&cache_dir)?;

        // Load image - use faster deserialization
        let img = image::open(path)
            .map_err(|e| anyhow!("Error loading image {}: {}", image_path, e))?;

        // Check transparency
        let has_alpha = self.has_transparency(&img);

        // OPTIMIZATION: Fewer color conversions - work directly on img
        let thumbnail = self.resize_to_square(img, self.thumbnail_size)?;

        // Save as WebP with controlled quality
        self.save_webp_with_quality(&thumbnail, &thumbnail_path, has_alpha)?;

        Ok((
            thumbnail_path.file_name()
                .and_then(|s| s.to_str())
                .unwrap_or("").to_string(),
            self.thumbnail_size
        ))
    }
}

/// Global generator instance (safe version)
static GENERATOR: OnceLock<ThumbnailGenerator> = OnceLock::new();

/// Gets global generator instance
pub fn get_generator() -> &'static ThumbnailGenerator {
    GENERATOR.get_or_init(|| ThumbnailGenerator::default())
}

/// Main thumbnail generation function (public API)
pub fn generate_thumbnail(image_path: &str) -> Result<(String, u32)> {
    let generator = get_generator();
    generator.generate_thumbnail(image_path)
} 