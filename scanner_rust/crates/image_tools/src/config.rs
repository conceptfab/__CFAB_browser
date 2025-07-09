use std::sync::OnceLock;

/// Konfiguracja modułu image_tools
pub struct ImageToolsConfig {
    /// Domyślny rozmiar miniatur
    pub thumbnail_size: u32,

    /// Domyślna jakość WebP dla obrazów bez przezroczystości
    pub webp_quality: u8,

    /// Domyślna jakość WebP dla obrazów z przezroczystością
    pub webp_alpha_quality: u8,

    /// Domyślny filtr do zmniejszania obrazów
    pub default_filter: image::imageops::FilterType,

    /// Nazwa folderu cache dla miniatur
    pub cache_dir_name: String,
}

impl Default for ImageToolsConfig {
    fn default() -> Self {
        Self {
            thumbnail_size: 256,
            webp_quality: 75,
            webp_alpha_quality: 80,
            default_filter: image::imageops::FilterType::Lanczos3,
            cache_dir_name: ".cache".to_string(),
        }
    }
}

/// Globalna konfiguracja modułu
static CONFIG: OnceLock<ImageToolsConfig> = OnceLock::new();

/// Pobiera globalną konfigurację modułu
pub fn get_config() -> &'static ImageToolsConfig {
    CONFIG.get_or_init(|| ImageToolsConfig::default())
}

/// Ustawia własną konfigurację modułu (tylko jeśli nie została jeszcze zainicjalizowana)
pub fn try_set_config(config: ImageToolsConfig) -> bool {
    CONFIG.set(config).is_ok()
}
