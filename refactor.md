Raport analizy kodu Rust - Rekomendacje poprawek
1. Duplikaty - build.rs
Problem: Identyczne pliki build.rs w trzech modułach
Rozwiązanie:
rust// Utwórz wspólny plik: build_common/build.rs

3. Nieużywane struktury
Problem: ScannerConfig w types.rs jest zdefiniowane ale nieużywane
Rozwiązanie: Usuń lub zaimplementuj:
rust// Usuń z src/types.rs lub zastosuj:
impl RustAssetRepository {
    pub fn new_with_config(config: ScannerConfig) -> Self {
        // implementacja
    }
}
4. Nieużywane funkcje
Problem: get_git_commit() zawsze zwraca "unknown"
Rozwiązanie: Dodaj do build.rs:
rust// W build.rs dodaj:
*config.git_mut().sha_mut() = true;
*config.git_mut().dirty_mut() = true;

// W build_info.rs:
pub fn get_git_commit() -> String {
    format!("{}{}", 
        env!("VERGEN_GIT_SHA"),
        if env!("VERGEN_GIT_DIRTY") == "true" { "-dirty" } else { "" }
    )
}

6. Słabe error handling
Problem: Używanie eprintln! zamiast proper loggingu
Rozwiązanie: W scanner.rs zastąp:
rust// Zamiast:
eprintln!("🦀 Error creating asset {}: {:?}", name, e);
// Użyj:
log::error!("🦀 Error creating asset {}: {:?} [build: {}, module: 1]", name, e, env!("VERGEN_BUILD_TIMESTAMP"));
7. Niepotrzebna publiczność funkcji
Problem: validate_asset_inputs w AssetBuilder jest publiczna ale używana tylko wewnętrznie
Rozwiązanie: W asset_builder.rs:
rust// Zmień z pub na prywatną:
fn validate_asset_inputs(&self, ...) -> Result<()> {
    // ...
}
8. Logger initialization
Problem: let _ = env_logger::try_init(); ignoruje błędy
Rozwiązanie: W lib.rs:
rust// Dodaj proper error handling:
if let Err(e) = env_logger::try_init() {
    eprintln!("Warning: Could not initialize logger: {}", e);
}

10. Optymalizacja thumbnail cache
Problem: Częste sprawdzanie cache może być wolne
Rozwiązanie: W thumbnail.rs dodaj cache w pamięci:
rustuse std::collections::HashMap;
use std::sync::Mutex;

static THUMBNAIL_CACHE: Mutex<HashMap<String, bool>> = Mutex::new(HashMap::new());
Priorytet: Punkty 1-5 (wysoki), 6-8 (średni), 9-10 (niski)