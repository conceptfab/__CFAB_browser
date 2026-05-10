# CFAB Browser – Przewodnik dla deweloperów

Dokumentacja umożliwiająca szybkie wdrożenie do projektu. Folder `do_usuniecia/` jest pomijany – nie jest częścią kodu produkcyjnego.

---

## Szybki start (5 minut)

### 1. Wymagania

- **Python 3.8+**
- **Rust** (dla modułu skanera) – [rustup.rs](https://rustup.rs/)
- **Maturin** – `pip install maturin`

### 2. Instalacja

```bash
# Klonowanie repozytorium
git clone <repo-url>
cd __CFAB_browser

# Środowisko wirtualne (zalecane)
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate  # Linux/macOS

# Zależności
pip install -r requirements.txt
```

### 3. Moduł Rust (wymagany do działania)

Aplikacja używa modułu Rust do skanowania zasobów. Skompilowane pliki `.pyd` znajdują się w `core/__rust/`. Jeśli ich brakuje:

```bash
python rebuild_rust.py
```

### 4. Uruchomienie

```bash
# macOS / Linux
python3 cfab_browser.py

# Windows (bez okna konsoli)
pythonw cfab_browser.py
```

### 5. Konfiguracja minimalna

Utwórz lub edytuj `config.json` w katalogu głównym:

```json
{
  "work_folder1": {
    "path": "C:/sciezka/do/folderu",
    "name": "Moja kolekcja",
    "icon": "workfolder_icon.png",
    "color": "#2c2e40"
  },
  "thumbnail": 256,
  "logger_level": "INFO",
  "use_styles": true
}
```

---

## Struktura projektu

> **Szczegółowe drzewo z opisami:** [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)

```
__CFAB_browser/
├── cfab_browser.py      # Punkt wejścia aplikacji
├── config.json          # Konfiguracja użytkownika
├── requirements.txt
├── rebuild_rust.py      # Budowanie modułu Rust
├── build_pyinstaller.py # Budowanie exe (PyInstaller)
│
├── core/                # Główny kod aplikacji
│   ├── main_window.py   # Okno główne, menu, zakładki
│   ├── amv_tab.py       # Zakładka galerii zasobów (AMV)
│   ├── pairing_tab.py   # Zakładka parowania
│   ├── tools_tab.py     # Zakładka narzędzi
│   ├── scanner.py       # Wrapper na moduł Rust (AssetRepository)
│   ├── thumbnail_cache.py
│   ├── json_utils.py
│   ├── file_utils.py
│   │
│   ├── amv_models/      # Modele MVC
│   ├── amv_views/       # Widoki (UI)
│   ├── amv_controllers/ # Kontrolery
│   ├── workers/         # Wątki robocze (miniatury, rebuilder, rozdzielczość)
│   ├── tools/           # Narzędzia (konwerter WebP, zmiana rozmiaru, itp.)
│   ├── managers/        # StatusBarManager
│   ├── resources/       # style.qss, ikony
│   └── __rust/          # Skompilowane moduły Rust (.pyd)
│
├── scanner_rust/        # Źródła modułu Rust (build)
│   ├── build.py
│   └── ...
│
├── docs/                # Dokumentacja
└── logs/                # Logi (performance.log)
```

---

## Architektura

### Przepływ uruchomienia

1. `cfab_browser.py` → `main()` → logger, QApplication, splash, style
2. `MainWindow` → zakładki: **AmvTab**, **PairingTab**, **ToolsTab**
3. **AmvTab** → `AmvController` + `AmvModel` + `AmvView` (MVC)

### Kluczowe komponenty

| Komponent | Plik | Opis |
|-----------|------|------|
| MainWindow | `core/main_window.py` | Okno główne, menu, status bar |
| AmvTab | `core/amv_tab.py` | Galeria zasobów (siatka miniatur, drzewo folderów) |
| PairingTab | `core/pairing_tab.py` | Parowanie archiwów z podglądami |
| ToolsTab | `core/tools_tab.py` | Narzędzia (WebP, resize, duplikaty, itp.) |
| AssetRepository | `core/scanner.py` | Skanowanie zasobów (backend Rust) |
| ThumbnailCache | `core/thumbnail_cache.py` | Cache miniatur w pamięci |

### Moduł Rust

- **Lokalizacja:** `core/__rust/` (scanner_rust.pyd, hash_utils.pyd, image_tools.pyd)
- **Źródła:** `scanner_rust/`
- **Ładowanie:** `core/scanner.py` → `_load_scanner_rust()` → import z `core/__rust/` lub fallback na site-packages
- **Bez Rust:** Aplikacja uruchomi się z mock backendem (pusta lista zasobów)

---

## Budowanie

### Moduł Rust

```bash
python rebuild_rust.py
```

Wymaga: `rustc`, `cargo`, `maturin`.

### Aplikacja standalone (PyInstaller)

```bash
python build_pyinstaller.py --release
# lub
python build_pyinstaller.py --debug   # z konsolą
```

Plik spec: `CFAB_Browser.spec`.

---

## Konfiguracja (config.json)

| Klucz | Opis |
|-------|------|
| `work_folder1` … `work_folder9` | Foldery robocze (path, name, icon, color) |
| `thumbnail` | Rozmiar miniatur w px (np. 256) |
| `logger_level` | DEBUG, INFO, WARNING, ERROR |
| `use_styles` | true/false – ładowanie styles.qss |

---

## Logowanie i debugowanie

- **Logi:** `logs/performance.log` (performance monitor)
- **Poziom:** ustawiany w `config.json` → `logger_level`
- **Format:** `%(asctime)s - %(name)s - %(levelname)s - %(message)s`

---

## Rozwiązywanie problemów

| Problem | Rozwiązanie |
|---------|-------------|
| Brak modułu `scanner_rust` | Uruchom `python rebuild_rust.py` |
| Brak PyQt6 | `pip install PyQt6` |
| Błąd przy imporcie `core` | Uruchom z katalogu głównego projektu |
| Puste galerie | Sprawdź `config.json` – ścieżki `work_folder*` |
| Brak miniatur | Sprawdź czy pliki `.asset` i obrazy podglądu istnieją |

---

## Technologie

- **UI:** PyQt6
- **Obrazy:** Pillow (PIL), moduł Rust (image_tools)
- **JSON:** orjson
- **Skanowanie:** moduł Rust (scanner_rust, hash_utils)
- **Build:** Maturin (Rust), PyInstaller (exe)
- **Rust:** pyo3 0.27, image 0.25, edition 2021
