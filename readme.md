# CFAB Browser - System Zarządzania Zasobami Cyfrowymi

> **Dla deweloperów:** [docs/DEVELOPER_GUIDE.md](docs/DEVELOPER_GUIDE.md) – szybki start, struktura projektu, budowanie.

## 📋 Opis Aplikacji

**CFAB Browser** to zaawansowany system zarządzania zasobami cyfrowymi zaprojektowany specjalnie do organizowania i przeglądania sparowanych kolekcji plików. Aplikacja koncentruje się na efektywnym zarządzaniu zasobami składającymi się z plików archiwów (ZIP, RAR, SBSAR) sparowanych z obrazami podglądu (PNG, JPG, WEBP).

## 🎯 Główne Funkcjonalności Biznesowe

### 1. **Automatyczne Parowanie Zasobów**

- **Algorytm parowania**: Automatyczne łączenie plików archiwów z odpowiadającymi im obrazami podglądu na podstawie nazw plików
- **Walidacja integralności**: Sprawdzanie poprawności sparowanych plików i śledzenie niesparowanych elementów
- **Generowanie metadanych**: Automatyczne tworzenie plików `.asset` zawierających informacje o rozmiarze, nazwie, podglądzie i dodatkowych metadanych

### 2. **System Galerii Wizualnej**

- **Responsywny interfejs**: Dynamiczne dostosowywanie układu kafelków do rozmiaru okna
- **Szybkie przeglądanie**: Optymalizowane ładowanie miniatur z systemem cache
- **Nawigacja folderowa**: Hierarchiczna struktura folderów z możliwością drag & drop
- **Filtrowanie i sortowanie**: Zaawansowane opcje organizacji zasobów

### 3. **Przetwarzanie Obrazów i Miniatury**

- **Inteligentny cache**: System cache'owania miniatur z walidacją integralności
- **Optymalizacja wydajności**: Automatyczne czyszczenie starych miniatur i zarządzanie pamięcią
- **Obsługa wielu formatów**: Wsparcie dla PNG, JPG, WEBP, BMP, TIFF, TGA
- **Atomic operations**: Bezpieczne zapisywanie miniatur z ochroną przed uszkodzeniem

### 4. **Zarządzanie Konfiguracją**

- **Centralizowana konfiguracja**: System zarządzania ustawieniami z cache'owaniem
- **Graceful degradation**: Fallback do domyślnych wartości przy błędach konfiguracji
- **Dynamiczne ustawienia**: Możliwość zmiany rozmiaru miniatur w czasie rzeczywistym

## 🏗️ Architektura Systemu

### **Główne Komponenty**

#### 1. **MainWindow** (`core/main_window.py`)

- **Rola**: Orkiestrator całej aplikacji
- **Funkcje biznesowe**:
  - Koordynacja wszystkich modułów aplikacji
  - Zarządzanie konfiguracją z proper error handling
  - Inicjalizacja interfejsu użytkownika
  - Graceful degradation przy błędach

#### 2. **Scanner** (`core/scanner.py`)

- **Rola**: Główny algorytm biznesowy parowania zasobów
- **Funkcje biznesowe**:
  - `find_and_create_assets()` - Główny algorytm parowania plików
  - `create_thumbnail_for_asset()` - Integracja generowania miniatur
  - `create_unpair_files_json()` - Śledzenie niesparowanych plików
  - `get_file_size_mb()` - Ekstrakcja metadanych

#### 3. **GalleryTab** (`core/gallery_tab.py`)

- **Rola**: Główny interfejs przeglądania zasobów
- **Funkcje biznesowe**:
  - `AssetScanner` - Skanowanie plików .asset w tle
  - `GridManager` - Dynamiczne generowanie siatki miniatur z debouncing
  - `ConfigManager` - Centralizacja konfiguracji z cache'owaniem
  - Drag & drop między folderami

#### 4. **Thumbnail** (`core/thumbnail.py`)

- **Rola**: Przetwarzanie obrazów i zarządzanie miniaturami
- **Funkcje biznesowe**:
  - `ThumbnailProcessor` - Główny algorytm przetwarzania obrazów
  - `ThumbnailCacheManager` - Inteligentne zarządzanie cache
  - `ThumbnailConfigManager` - Konfiguracja z cache'owaniem
  - Walidacja integralności miniatur

### **Struktura Danych**

#### Pliki `.asset`

```json
{
  "name": "nazwa_zasobu",
  "archive": "nazwa_archiwum.zip",
  "preview": "nazwa_obrazu.png",
  "size_mb": 15.5,
  "thumbnail": true,
  "stars": null,
  "color": null,
  "meta": {}
}
```

#### Konfiguracja Systemu (`config.json`)

```json
{
  "work_folder1": {
    "path": "ścieżka/do/folderu",
    "name": "nazwa_folderu",
    "icon": "",
    "color": ""
  },
  "thumbnail": 256,
  "logger_level": "INFO",
  "use_styles": true
}
```

## 🔄 Procesy Biznesowe

### 1. **Proces Skanowania i Parowania**

1. **Skanowanie folderu** - Wyszukiwanie plików archiwów i obrazów
2. **Grupowanie według nazw** - Łączenie plików o identycznych nazwach
3. **Walidacja par** - Sprawdzanie poprawności sparowanych plików
4. **Generowanie plików .asset** - Tworzenie metadanych dla każdej pary
5. **Tworzenie miniatur** - Generowanie podglądów wizualnych
6. **Raportowanie niesparowanych** - Dokumentowanie plików bez pary

### 2. **Proces Przeglądania Galerii**

1. **Ładowanie konfiguracji** - Pobieranie ustawień z cache
2. **Skanowanie plików .asset** - Wczytywanie metadanych zasobów
3. **Generowanie siatki** - Dynamiczne tworzenie układu kafelków
4. **Ładowanie miniatur** - Inteligentne cache'owanie obrazów
5. **Responsywne dostosowanie** - Automatyczne przeliczanie kolumn

### 3. **Proces Zarządzania Miniaturami**

1. **Walidacja cache** - Sprawdzanie aktualności miniatur
2. **Przetwarzanie obrazów** - Resize, crop i optymalizacja
3. **Atomic save** - Bezpieczne zapisywanie z backup
4. **Cleanup** - Usuwanie starych miniatur

## 📊 Metryki Wydajnościowe

### **Obsługiwane Formaty**

- **Archiwa**: ZIP, RAR, SBSAR
- **Obrazy**: PNG, JPG, JPEG, WEBP, BMP, TIFF, TGA
- **Metadane**: JSON (pliki .asset)

### **Ograniczenia Wydajnościowe**

- **Rozmiar miniatur**: Konfigurowalny (domyślnie 256px)
- **Cache**: Inteligentne zarządzanie z walidacją
- **Threading**: Asynchroniczne skanowanie i przetwarzanie
- **Memory management**: Optymalizacja użycia pamięci

## 🛠️ Technologie i Zależności

### **Framework UI**

- **PyQt6** - Główny framework interfejsu użytkownika
- **QThread** - Asynchroniczne operacje
- **QTimer** - Debouncing i optymalizacje

### **Przetwarzanie Obrazów**

- **Pillow (PIL)** - Manipulacja obrazami
- **ImageFile** - Obsługa truncated images
- **LANCZOS** - Algorytm resampling

### **Zarządzanie Danych**

- **JSON** - Konfiguracja i metadane
- **Pathlib** - Operacje na ścieżkach
- **Logging** - System logowania

## 🔧 Konfiguracja i Uruchomienie

### **Wymagania Systemowe**

- Python 3.8+
- PyQt6
- Pillow
- Windows 10/11 (testowane)

### **Uruchomienie**

```bash
python cfab_browser.py
```

### **Konfiguracja**

Edytuj plik `config.json` aby dostosować:

- Ścieżki do folderów roboczych
- Rozmiar miniatur
- Poziom logowania
- Style interfejsu

## 🎯 Przyszłe Rozszerzenia

### **Planowane Funkcjonalności**

- **PairingTab** - Zaawansowane narzędzia parowania
- **ToolsTab** - Dodatkowe narzędzia zarządzania
- **System ocen** - Gwiazdki i kolory dla zasobów
- **Eksport/Import** - Backup i migracja kolekcji

### **Optymalizacje**

- **Lazy loading** - Ładowanie miniatur na żądanie
- **Virtual scrolling** - Obsługa bardzo dużych kolekcji
- **Batch processing** - Masowe operacje na zasobach

## 📝 Logi i Debugowanie

Aplikacja wykorzystuje zaawansowany system logowania z konfigurowalnymi poziomami:

- **DEBUG** - Szczegółowe informacje o operacjach
- **INFO** - Standardowe informacje o procesach
- **WARNING** - Ostrzeżenia o potencjalnych problemach
- **ERROR** - Błędy wymagające uwagi

Logi są zapisywane w formacie: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`
