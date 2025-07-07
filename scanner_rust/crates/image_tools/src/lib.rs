use pyo3::prelude::*;
use image::{imageops::FilterType, DynamicImage, GenericImageView, RgbImage, Rgb};

/// Resizes an image based on specific rules.
#[pyfunction]
fn resize_image(py: Python, file_path: String) -> PyResult<bool> {
    py.allow_threads(|| {
        let img = image::open(&file_path)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("Failed to open image {}: {}", file_path, e)))?;

        let (original_width, original_height) = img.dimensions();
        let (new_width, new_height) = calculate_new_size(original_width, original_height);

        if new_width >= original_width && new_height >= original_height {
            return Ok(false); // No resize needed
        }

        let resized_img = img.resize(new_width, new_height, FilterType::Lanczos3);

        resized_img.save(&file_path)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("Failed to save resized image {}: {}", file_path, e)))?;

        Ok(true)
    })
}

/// Converts an image to WebP format.
#[pyfunction]
fn convert_to_webp(py: Python, input_path: String, output_path: String) -> PyResult<bool> {
    py.allow_threads(|| {
        let mut img = image::open(&input_path)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("Failed to open image {}: {}", input_path, e)))?;

        // Poprawna konwersja obrazów z alpha channel
        if img.color().has_alpha() {
            // Konwertuj RGBA do RGB z białym tłem
            let rgb_img = DynamicImage::ImageRgb8({
                let rgba = img.to_rgba8();
                let mut rgb_buffer = image::RgbImage::new(img.width(), img.height());
                
                for (x, y, pixel) in rgba.enumerate_pixels() {
                    let alpha = pixel[3] as f32 / 255.0;
                    let r = (pixel[0] as f32 * alpha + 255.0 * (1.0 - alpha)) as u8;
                    let g = (pixel[1] as f32 * alpha + 255.0 * (1.0 - alpha)) as u8;
                    let b = (pixel[2] as f32 * alpha + 255.0 * (1.0 - alpha)) as u8;
                    rgb_buffer.put_pixel(x, y, image::Rgb([r, g, b]));
                }
                
                rgb_buffer
            });
            img = rgb_img;
        } else if img.color().channel_count() != 3 {
            img = DynamicImage::ImageRgb8(img.to_rgb8());
        }

        img.save_with_format(&output_path, image::ImageFormat::WebP)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("Failed to save WebP image {}: {}", output_path, e)))?;

        Ok(true)
    })
}

fn calculate_new_size(width: u32, height: u32) -> (u32, u32) {
    let max_side = width.max(height);
    let min_side = width.min(height);
    let difference_percent = ((max_side - min_side) as f32 / max_side as f32) * 100.0;

    let (new_width, new_height) = if difference_percent <= 30.0 {
        if width <= height {
            (1024, (height as f32 * 1024.0 / width as f32) as u32)
        } else {
            ((width as f32 * 1024.0 / height as f32) as u32, 1024)
        }
    } else {
        if width >= height {
            (1600, (height as f32 * 1600.0 / width as f32) as u32)
        } else {
            ((width as f32 * 1600.0 / height as f32) as u32, 1600)
        }
    };

    if new_width > width || new_height > height {
        (width, height)
    } else {
        (new_width, new_height)
    }
}

#[pymodule]
fn image_tools(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(resize_image, m)?)?;
    m.add_function(wrap_pyfunction!(convert_to_webp, m)?)?;
    Ok(())
} 