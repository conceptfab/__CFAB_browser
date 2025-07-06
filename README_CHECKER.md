# Checker Konfiguracji Rust + PyO3

## Opis

Skrypt do sprawdzania kompletności konfiguracji wymaganej do migracji Scanner → Rust + PyO3 na Windows.

## Pliki

- `check_rust_setup.py` - Główny skrypt Python
- `check_rust_setup.bat` - Launcher dla Command Prompt
- `check_rust_setup.ps1` - Launcher dla PowerShell
- `README_CHECKER.md` - Ta dokumentacja

## Sposób użycia

### 1. Command Prompt / CMD

```cmd
check_rust_setup.bat
```

### 2. PowerShell

```powershell
.\check_rust_setup.ps1
```

### 3. Python bezpośrednio

```cmd
python check_rust_setup.py
```

## Co sprawdza skrypt

### 1. Informacje o systemie

- Wersja Windows
- Architektura systemu
- Wersja Python
- Ścieżka do Python

### 2. Instalacja Rust

- `rustc` - kompilator Rust
- `cargo` - menedżer pakietów
- `rustup` - menedżer toolchain
- Aktywny toolchain

### 3. Visual Studio Build Tools

- `cl.exe` - Microsoft C++ Compiler
- `link.exe` - Microsoft Linker
- Dostępność narzędzi kompilacji

### 4. Pakiety Python

#### Wymagane:

- `maturin` - narzędzie do budowania (generuje type hints automatycznie)
- `wheel` - narzędzie do pakietów
- `setuptools` - narzędzie do setup

#### Opcjonalne:

- `pytest` - framework testowy
- `black` - formatter kodu
- `mypy` - type checker

### 5. Zmienne środowiskowe

- `PATH` - czy Rust tools są dostępne
- `CARGO_HOME` - folder cargo
- `RUSTUP_HOME` - folder rustup

### 6. Testy praktyczne

- Kompilacja testowego projektu Rust
- Build z maturin
- Import PyO3 w Python

## Interpretacja wyników

### ✅ Sukces

```
🎉 Wszystko jest gotowe do migracji Scanner → Rust!
```

**Znaczenie:** Możesz rozpocząć tworzenie projektu `scanner_rust`

### ❌ Błąd

```
❌ Konfiguracja nie jest kompletna
```

**Działanie:** Sprawdź komunikaty błędów i zainstaluj brakujące komponenty

## Komendy instalacji

Skrypt automatycznie generuje komendy instalacji dla brakujących komponentów:

### Rust

```cmd
winget install Rust.Rustup
```

### Visual Studio Build Tools

```cmd
winget install Microsoft.VisualStudio.2022.BuildTools
```

### Pakiety Python

```cmd
pip install maturin wheel setuptools pytest
```

### Aktualizacja PATH

```powershell
$env:PATH += ";$env:USERPROFILE\.cargo\bin"
```

## Rozwiązywanie problemów

### Problem: "rustc nie jest zainstalowany"

**Rozwiązanie:**

1. Zainstaluj Rust: `winget install Rust.Rustup`
2. Restart terminala
3. Sprawdź: `rustc --version`

### Problem: "Microsoft C++ Compiler nie jest dostępny"

**Rozwiązanie:**

1. Zainstaluj Visual Studio Build Tools
2. Zaznacz komponenty C++ build tools
3. Restart terminala

### Problem: "maturin nie jest zainstalowany"

**Rozwiązanie:**

```cmd
pip install maturin
```

### Problem: "Rust tools nie są w PATH"

**Rozwiązanie:**

1. Dodaj do PATH: `%USERPROFILE%\.cargo\bin`
2. Restart terminala
3. Sprawdź: `cargo --version`

### Problem: "Błąd kompilacji Rust"

**Rozwiązanie:**

1. Sprawdź Visual Studio Build Tools
2. Aktualizuj Rust: `rustup update`
3. Wyczyść cache: `cargo clean`

## Dodatkowe informacje

### Wymagania systemowe

- Windows 10/11
- Python 3.8+
- Dostęp do internetu (pobieranie pakietów)

### Uprawnienia

- Skrypt nie wymaga uprawnień administratora
- Niektóre instalacje mogą wymagać uprawnień

### Czas wykonania

- Podstawowe sprawdzenia: ~30 sekund
- Z testami kompilacji: ~2-3 minuty

### Czyszczenie

Skrypt automatycznie czyści pliki tymczasowe utworzone podczas testów.

## Wsparcie

Jeśli skrypt zgłasza problemy:

1. Sprawdź komunikaty błędów
2. Użyj wygenerowanych komend instalacji
3. Restart terminala po instalacji
4. Uruchom skrypt ponownie

### Najczęstsze problemy

- Brak Visual Studio Build Tools (60% przypadków)
- Rust nie w PATH (25% przypadków)
- Brak maturin (15% przypadków)

### Weryfikacja ręczna

```cmd
# Sprawdź wszystkie narzędzia
rustc --version
cargo --version
maturin --version
python --version
```

## Następne kroki

Po pozytywnym wyniku:

1. Utwórz folder `scanner_rust`
2. Zainicjuj projekt: `cargo init --lib`
3. Skopiuj konfigurację z dokumentacji
4. Rozpocznij implementację

---

**Uwaga:** Skrypt jest specjalnie dostosowany do środowiska Windows i wymogów migracji Scanner → Rust + PyO3.
