# Rust Scanner dla CFAB Browser

Wysokowydajna implementacja scanera asset-ów w języku Rust z integracją Python poprzez PyO3.

## Przegląd

Ten projekt stanowi migrację logiki scanera z Python do Rust w celu znacznego poprawienia wydajności skanowania folderów, szczególnie przy dużych ilościach plików.

## Wymagania

- **Rust** 1.70+ (najlepiej najnowsza wersja stable)
- **Python** 3.8+
- **maturin** do budowania
- **PyO3** 0.20+

## Instalacja

### 1. Instalacja Rust

```bash
# Windows
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Linux/macOS
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

### 2. Instalacja Python dependencies

```bash
pip install maturin pyo3
```

### 3. Budowanie

#### Windows

```cmd
cd scanner_rust
build.bat
```

#### Linux/macOS

```bash
cd scanner_rust
maturin develop --release
```

## Struktura projektu

```
scanner_rust/
├── src/
│   ├── lib.rs              # Główny moduł PyO3
│   ├── types.rs            # Definicje typów danych
│   ├── file_utils.rs       # Narzędzia do operacji na plikach
│   ├── asset_builder.rs    # Budowniczy struktur Asset
│   └── scanner.rs          # Główna logika skanowania
├── Cargo.toml              # Konfiguracja Rust
├── pyproject.toml          # Konfiguracja Python
├── build.bat               # Skrypt budowania Windows
├── benchmark.py            # Benchmark wydajności
└── README.md               # Ta dokumentacja
```

## Użycie

### Podstawowe użycie

```python
import scanner_rust

# Utwórz instancję scanera
scanner = scanner_rust.RustAssetRepository()

# Skanuj folder i utwórz asset-y
assets = scanner.find_and_create_assets("/path/to/folder")

# Załaduj istniejące asset-y
existing_assets = scanner.load_existing_assets("/path/to/folder")

# Skanuj tylko pliki
archives, images = scanner.scan_folder_for_files("/path/to/folder")
```

### Z callback postępu

```python
def progress_callback(current, total, message):
    print(f"Postęp: {current}/{total} - {message}")

assets = scanner.find_and_create_assets(
    "/path/to/folder",
    progress_callback=progress_callback
)
```

### Integracja z istniejącym kodem

```python
# Użyj wrapper dla pełnej kompatybilności
from core.rust_scanner import RustAssetRepository

# Drop-in replacement dla istniejącego AssetRepository
repo = RustAssetRepository()
assets = repo.find_and_create_assets(folder_path)
```

## Funkcjonalności

- **Wysokowydajne skanowanie** - 5-10x szybsze od wersji Python
- **Przetwarzanie równoległe** - wykorzystuje wszystkie rdzenie CPU
- **Obsługa błędów** - bezpieczne zarządzanie błędami
- **Kompatybilność** - zachowuje API z wersją Python
- **Progress callback** - informacje o postępie skanowania
- **Foldery specjalne** - wykrywanie folderów tex, textures, maps
- **Niesparowane pliki** - generowanie raportu niepasujących plików

## Wydajność

Oczekiwane korzyści wydajnościowe:

- **5-10x szybsze** skanowanie dużych folderów
- **Niższe zużycie RAM** - efektywne struktury danych
- **Równoległe przetwarzanie** - wykorzystanie wielu rdzeni
- **Brak GIL** - prawdziwe równoległe wykonywanie

## Benchmark

Uruchom benchmark aby porównać wydajność:

```bash
cd scanner_rust
python benchmark.py
```

## Debugowanie

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
# Debug build
maturin develop --debug

# Sprawdź logi
RUST_LOG=debug maturin develop
```

## Rozwój

### Dodawanie nowych funkcjonalności

1. Dodaj nowe typy w `src/types.rs`
2. Implementuj logikę w odpowiednim module
3. Dodaj binding PyO3 w `src/scanner.rs`
4. Przetestuj z `benchmark.py`

### Testy

```bash
# Uruchom testy Rust
cargo test

# Benchmark
python benchmark.py
```

## Licencja

MIT License - zobacz plik głównego projektu CFAB Browser

## Wsparcie

W przypadku problemów:

1. Sprawdź wymagania systemowe
2. Uruchom `build.bat` ponownie
3. Sprawdź logi błędów
4. Porównaj z benchmark wynikami

## Changelog

### v0.1.0

- Podstawowa implementacja scanera
- Integracja PyO3
- Progress callback
- Obsługa folderów specjalnych
- Benchmark wydajności
