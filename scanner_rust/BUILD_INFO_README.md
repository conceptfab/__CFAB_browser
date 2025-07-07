# Informacje o Kompilacji Modułów Rust

## Przegląd

Wszystkie moduły Rust w projekcie zostały wyposażone w funkcje do pobierania informacji o kompilacji, numerze modułu i dacie/godzinie kompilacji.

## Numeracja Modułów

- **Moduł 1**: `scanner` - główny moduł skanowania zasobów
- **Moduł 2**: `hash_utils` - narzędzia do obliczania hashów
- **Moduł 3**: `image_tools` - narzędzia do przetwarzania obrazów

## Dostępne Funkcje

Każdy moduł udostępnia następujące funkcje:

### `get_build_info()`

Zwraca słownik z wszystkimi informacjami o kompilacji:

- `module_number` - numer modułu (1, 2, 3)
- `build_timestamp` - timestamp kompilacji
- `build_date` - data kompilacji
- `build_time` - godzina kompilacji
- `git_commit_hash` - hash commita Git
- `git_commit_date` - data commita
- `git_branch` - nazwa gałęzi Git
- `cargo_version` - wersja z Cargo.toml
- `cargo_name` - nazwa modułu
- `rust_version` - wersja Rust
- `target_arch` - architektura docelowa
- `target_os` - system operacyjny docelowy

### `get_build_number()`

Zwraca numer kompilacji (timestamp jako string).

### `get_build_datetime()`

Zwraca datę i godzinę kompilacji w czytelnym formacie.

### `get_git_commit()`

Zwraca hash commita Git.

### `get_module_number()`

Zwraca numer modułu (1, 2, 3).

### `get_module_info()`

Zwraca sformatowane informacje o module.

### `get_log_prefix()`

Zwraca prefiks logowania z numerem kompilacji i modułu.

### `format_log_message(message)`

Formatuje komunikat z prefiksem kompilacji i numerem modułu.

## Przykład Użycia

````python
import scanner_rust
import hash_utils
import image_tools

# Podstawowe informacje
print(f"Scanner: {scanner_rust.get_module_info()}")
print(f"Hash Utils: {hash_utils.get_module_info()}")
print(f"Image Tools: {image_tools.get_module_info()}")

# Numer modułu
print(f"Scanner module number: {scanner_rust.get_module_number()}")

# Data kompilacji
print(f"Scanner build date: {scanner_rust.get_build_datetime()}")

# Wszystkie informacje
info = scanner_rust.get_build_info()
for key, value in info.items():
    print(f"{key}: {value}")

# Funkcje logowania
print(f"Prefiks logowania: {scanner_rust.get_log_prefix()}")
print(f"Komunikat z prefiksem: {scanner_rust.format_log_message('Test message')}")

## Testowanie

Uruchom test wszystkich modułów:

```bash
cd scanner_rust
python test_build_info.py
````

## Implementacja Techniczna

### Pliki build.rs

Każdy moduł ma plik `build.rs`, który używa biblioteki `vergen` do generowania informacji o kompilacji podczas budowania.

### Moduły build_info.rs

Każdy moduł ma moduł `build_info.rs` z funkcjami PyO3 do eksportu informacji do Pythona.

### Cargo.toml

Dodano zależność `vergen` w sekcji `[build-dependencies]`.

## Logowanie z Numerem Kompilacji

### Automatyczne Logowanie

Moduły automatycznie wyświetlają numer kompilacji w komunikatach błędów:

```
🦀 Error saving asset example.zip: File not found [build: 1703123456, module: 1]
```

### Ręczne Formatowanie Komunikatów

Możesz użyć funkcji do formatowania własnych komunikatów:

```python
import scanner_rust

# Prefiks logowania
prefix = scanner_rust.get_log_prefix()  # "[build: 1703123456, module: 1]"

# Komunikat z prefiksem
message = scanner_rust.format_log_message("Custom error message")
# Wynik: "🦀 Custom error message [build: 1703123456, module: 1]"
```

## Kompatybilność

- Wszystkie funkcje są dostępne po skompilowaniu modułów
- Informacje są generowane podczas kompilacji, więc są zawsze aktualne
- Funkcje są bezpieczne wątkowo i mogą być wywoływane z Pythona
- Komunikaty błędów automatycznie zawierają numer kompilacji
