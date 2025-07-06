# Szybki start - Rust Scanner

## Krok 1: Instalacja wymaganych narzędzi

### Windows

```cmd
# Uruchom install_rust.bat
install_rust.bat
```

### Linux/macOS

```bash
# Zainstaluj Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source ~/.cargo/env

# Zainstaluj maturin
pip install maturin
```

## Krok 2: Budowanie projektu

```cmd
# Windows
build.bat

# Linux/macOS
maturin develop --release
```

## Krok 3: Test

```python
# Uruchom test
python benchmark.py
```

## Rozwiązywanie problemów

### Problem: "rustc nie jest rozpoznawany"

```cmd
# Restart terminala lub uruchom:
%USERPROFILE%\.cargo\bin\rustup.exe update
```

### Problem: "maturin nie jest rozpoznawany"

```cmd
pip install --upgrade maturin
```

### Problem: Błąd kompilacji

```cmd
# Wyczyść i przebuduj
cargo clean
build.bat
```

## Sprawdzenie instalacji

```cmd
# Sprawdź wersje
rustc --version
maturin --version
python --version
```

## Pierwsze użycie

```python
import scanner_rust

# Utwórz scanner
scanner = scanner_rust.RustAssetRepository()

# Skanuj folder
assets = scanner.find_and_create_assets("C:/path/to/your/folder")
print(f"Znaleziono {len(assets)} asset-ów")
```

## Wskazówki

- Używaj build.bat do przebudowy po zmianach
- Uruchom benchmark.py do testowania wydajności
- Sprawdź logi błędów w przypadku problemów
- Restart terminala po instalacji Rust
