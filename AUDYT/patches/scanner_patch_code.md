# PATCH-CODE DLA: SCANNER.PY

**Powiązany plik z analizą:** `../corrections/scanner_correction.md`
**Zasady ogólne:** `../refactoring_rules.md`

---

### PATCH 1: DODANIE PROPER ERROR HANDLING I LOGOWANIA

**Problem:** Funkcje łapią wszystkie wyjątki z `except Exception` ale nie logują błędów, co utrudnia debugging
**Rozwiązanie:** Dodanie importu logging i szczegółowego logowania błędów

```python
import glob
import json
import logging
import os

from core.thumbnail import process_thumbnail

# Dodanie loggera dla modułu
logger = logging.getLogger(__name__)
```

---

### PATCH 2: OPTYMALIZACJA GET_FILE_SIZE_MB Z BETTER ERROR HANDLING

**Problem:** Nieobsłużone wyjątki bez logowania, zwracanie 0 przy błędzie
**Rozwiązanie:** Proper logging błędów i obsługa konkretnych przypadków

```python
def get_file_size_mb(file_path):
    """
    Zwraca rozmiar pliku w MB
    
    Args:
        file_path (str): Ścieżka do pliku
        
    Returns:
        float: Rozmiar pliku w MB lub 0 w przypadku błędu
    """
    if not file_path or not isinstance(file_path, str):
        logger.warning(f"Invalid file_path parameter: {file_path}")
        return 0
        
    try:
        if not os.path.exists(file_path):
            logger.warning(f"File does not exist: {file_path}")
            return 0
            
        size_bytes = os.path.getsize(file_path)
        size_mb = size_bytes / (1024 * 1024)  # Konwersja bajtów na MB
        return round(size_mb, 2)  # Zaokrąglenie do 2 miejsc po przecinku
        
    except PermissionError:
        logger.error(f"Permission denied accessing file: {file_path}")
        return 0
    except OSError as e:
        logger.error(f"OS error accessing file {file_path}: {e}")
        return 0
    except Exception as e:
        logger.error(f"Unexpected error getting file size for {file_path}: {e}")
        return 0
```

---

### PATCH 3: OPTYMALIZACJA CREATE_THUMBNAIL_FOR_ASSET

**Problem:** Nieobsłużone wyjątki, brak walidacji parametrów
**Rozwiązanie:** Dodanie walidacji i proper error handling

```python
def create_thumbnail_for_asset(asset_path, image_path):
    """
    Tworzy thumbnail dla pliku asset i aktualizuje plik asset

    Args:
        asset_path (str): Ścieżka do pliku .asset
        image_path (str): Ścieżka do pliku obrazu (preview)

    Returns:
        bool: True jeśli thumbnail został utworzony pomyślnie,
              False w przeciwnym razie
    """
    # Walidacja parametrów
    if not asset_path or not isinstance(asset_path, str):
        logger.error(f"Invalid asset_path parameter: {asset_path}")
        return False
        
    if not image_path or not isinstance(image_path, str):
        logger.error(f"Invalid image_path parameter: {image_path}")
        return False
        
    if not os.path.exists(asset_path):
        logger.error(f"Asset file does not exist: {asset_path}")
        return False
        
    if not os.path.exists(image_path):
        logger.error(f"Image file does not exist: {image_path}")
        return False
    
    try:
        # Wywołaj funkcję process_thumbnail
        logger.debug(f"Processing thumbnail for image: {image_path}")
        process_thumbnail(image_path)

        # Jeśli funkcja się wykonała bez błędów, zaktualizuj plik asset
        with open(asset_path, "r", encoding="utf-8") as asset_file:
            asset_data = json.load(asset_file)

        # Ustaw thumbnail na True
        asset_data["thumbnail"] = True

        # Zapisz zaktualizowany plik asset
        with open(asset_path, "w", encoding="utf-8") as asset_file:
            json.dump(asset_data, asset_file, indent=2, ensure_ascii=False)

        logger.info(f"Thumbnail created successfully for asset: {os.path.basename(asset_path)}")
        return True

    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in asset file {asset_path}: {e}")
        return False
    except PermissionError as e:
        logger.error(f"Permission denied accessing files: {e}")
        return False
    except Exception as e:
        logger.error(f"Error creating thumbnail for asset {asset_path}: {e}")
        return False
```

---

### PATCH 4: OPTYMALIZACJA CREATE_UNPAIR_FILES_JSON

**Problem:** Zwraca None przy błędzie bez informacji o problemie
**Rozwiązanie:** Proper error handling i logowanie

```python
def create_unpair_files_json(folder_path, archive_by_name, image_by_name, common_names):
    """
    Tworzy plik unpair_files.json z listą plików bez pary

    Args:
        folder_path (str): Ścieżka do folderu
        archive_by_name (dict): Słownik plików archiwum według nazwy
        image_by_name (dict): Słownik plików obrazów według nazwy
        common_names (set): Zbiór nazw plików z parami

    Returns:
        str: Ścieżka do utworzonego pliku lub None w przypadku błędu
    """
    # Walidacja parametrów
    if not folder_path or not os.path.exists(folder_path):
        logger.error(f"Invalid or non-existent folder_path: {folder_path}")
        return None
        
    if not isinstance(archive_by_name, dict) or not isinstance(image_by_name, dict):
        logger.error("archive_by_name and image_by_name must be dictionaries")
        return None
        
    if not isinstance(common_names, set):
        logger.error("common_names must be a set")
        return None
    
    try:
        # Znajdź pliki bez pary
        unpaired_archives = []
        unpaired_previews = []

        # Pliki archiwum bez pary
        for name, archive_path in archive_by_name.items():
            if name not in common_names:
                unpaired_archives.append(os.path.basename(archive_path))

        # Pliki obrazów bez pary
        for name, image_path in image_by_name.items():
            if name not in common_names:
                unpaired_previews.append(os.path.basename(image_path))

        # Utwórz strukturę danych
        unpair_data = {
            "unpaired_archives": sorted(unpaired_archives),  # Sortowanie dla konsystencji
            "unpaired_previews": sorted(unpaired_previews),
        }

        # Ścieżka do pliku unpair_files.json
        unpair_file_path = os.path.join(folder_path, "unpair_files.json")

        # Zapisz plik JSON
        with open(unpair_file_path, "w", encoding="utf-8") as unpair_file:
            json.dump(unpair_data, unpair_file, indent=2, ensure_ascii=False)

        logger.info(f"Created unpair_files.json with {len(unpaired_archives)} unpaired archives and {len(unpaired_previews)} unpaired previews")
        return unpair_file_path

    except PermissionError as e:
        logger.error(f"Permission denied creating unpair file in {folder_path}: {e}")
        return None
    except Exception as e:
        logger.error(f"Error creating unpair_files.json in {folder_path}: {e}")
        return None
```

---

### PATCH 5: KONFIGURACJA ROZSZERZEŃ PLIKÓW

**Problem:** Hardkodowane rozszerzenia plików, duplikacja kodu
**Rozwiązanie:** Wydzielenie konfiguracji na początek pliku

```python
# Konfiguracja rozszerzeń plików obsługiwanych przez aplikację
FILE_EXTENSIONS = {
    'archives': ['zip', 'rar', 'sbsar'],
    'images': ['png', 'jpg', 'jpeg', 'webp']
}


def _get_files_by_extensions(folder_path, extensions):
    """
    Pomocnicza funkcja do wyszukiwania plików o określonych rozszerzeniach
    
    Args:
        folder_path (str): Ścieżka do folderu
        extensions (list): Lista rozszerzeń (bez kropki)
        
    Returns:
        list: Lista ścieżek do znalezionych plików
    """
    files = []
    for ext in extensions:
        # Małe litery
        pattern_lower = os.path.join(folder_path, f"*.{ext.lower()}")
        files.extend(glob.glob(pattern_lower))
        # Wielkie litery
        pattern_upper = os.path.join(folder_path, f"*.{ext.upper()}")
        files.extend(glob.glob(pattern_upper))
    return files
```

---

### PATCH 6: REFAKTORYZACJA GŁÓWNEJ FUNKCJI - CZĘŚĆ 1

**Problem:** find_and_create_assets() jest zbyt długa (129 linii), łamie Single Responsibility Principle
**Rozwiązanie:** Wydzielenie funkcji pomocniczych

```python
def _scan_folder_for_files(folder_path):
    """
    Skanuje folder w poszukiwaniu plików archiwów i obrazów
    
    Args:
        folder_path (str): Ścieżka do folderu
        
    Returns:
        tuple: (archive_by_name, image_by_name) - słowniki plików według nazw
    """
    # Znajdź wszystkie pliki archiwum i obrazów
    archive_files = _get_files_by_extensions(folder_path, FILE_EXTENSIONS['archives'])
    image_files = _get_files_by_extensions(folder_path, FILE_EXTENSIONS['images'])

    # Słownik do przechowywania plików według nazwy (bez rozszerzenia)
    archive_by_name = {}
    image_by_name = {}

    # Grupuj pliki archiwum według nazwy
    for archive_file in archive_files:
        name_without_ext = os.path.splitext(os.path.basename(archive_file))[0]
        if name_without_ext in archive_by_name:
            logger.warning(f"Duplicate archive name found: {name_without_ext}")
        archive_by_name[name_without_ext] = archive_file

    # Grupuj pliki obrazów według nazwy
    for image_file in image_files:
        name_without_ext = os.path.splitext(os.path.basename(image_file))[0]
        if name_without_ext in image_by_name:
            logger.warning(f"Duplicate image name found: {name_without_ext}")
        image_by_name[name_without_ext] = image_file

    logger.info(f"Found {len(archive_files)} archive files and {len(image_files)} image files")
    return archive_by_name, image_by_name


def _create_single_asset(name, archive_path, image_path, folder_path):
    """
    Tworzy pojedynczy plik .asset
    
    Args:
        name (str): Nazwa pliku (bez rozszerzenia)
        archive_path (str): Ścieżka do pliku archiwum
        image_path (str): Ścieżka do pliku obrazu
        folder_path (str): Ścieżka do folderu docelowego
        
    Returns:
        str|None: Ścieżka do utworzonego pliku .asset lub None przy błędzie
    """
    asset_path = os.path.join(folder_path, f"{name}.asset")
    
    try:
        # Pobierz rozmiar pliku archiwum w MB
        archive_size_mb = get_file_size_mb(archive_path)

        asset_data = {
            "name": name,
            "archive": os.path.basename(archive_path),
            "preview": os.path.basename(image_path),
            "size_mb": archive_size_mb,
            "thumbnail": None,
            "stars": None,
            "color": None,
            "meta": {},
        }

        with open(asset_path, "w", encoding="utf-8") as asset_file:
            json.dump(asset_data, asset_file, indent=2, ensure_ascii=False)

        # Utwórz thumbnail dla tego asset
        thumbnail_success = create_thumbnail_for_asset(asset_path, image_path)
        if not thumbnail_success:
            logger.warning(f"Failed to create thumbnail for asset: {name}")

        logger.debug(f"Created asset file: {name}.asset")
        return asset_path

    except Exception as e:
        logger.error(f"Error creating asset file for {name}: {e}")
        return None
```

---

### PATCH 7: REFAKTORYZACJA GŁÓWNEJ FUNKCJI - CZĘŚĆ 2

**Problem:** Główna funkcja nadal zbyt długa po wydzieleniu pomocniczych funkcji
**Rozwiązanie:** Przepisanie głównej funkcji z wykorzystaniem pomocniczych funkcji

```python
def find_and_create_assets(folder_path, progress_callback=None):
    """
    Szuka par plików o tej samej nazwie w folderze:
    - pliki archiwum: zip, rar, sbsar
    - pliki obrazów: png, jpg, webp

    Dla każdej znalezionej pary tworzy plik .asset w formacie JSON
    Dodatkowo tworzy plik unpair_files.json z listą plików bez pary

    Args:
        folder_path (str): Ścieżka do folderu do skanowania
        progress_callback (callable): Funkcja callback do aktualizacji postępu
                                     Przyjmuje parametry: (current, total, message)
                                     
    Returns:
        list: Lista ścieżek do utworzonych plików .asset
    """
    # Walidacja parametrów wejściowych
    if not folder_path or not isinstance(folder_path, str):
        error_msg = f"Invalid folder_path parameter: {folder_path}"
        logger.error(error_msg)
        if progress_callback:
            progress_callback(0, 0, error_msg)
        return []

    # Sprawdź czy folder istnieje
    if not os.path.exists(folder_path):
        error_msg = f"Folder {folder_path} nie istnieje!"
        logger.error(error_msg)
        if progress_callback:
            progress_callback(0, 0, error_msg)
        return []

    logger.info(f"Starting asset scan in folder: {folder_path}")

    try:
        # Skanuj folder w poszukiwaniu plików
        archive_by_name, image_by_name = _scan_folder_for_files(folder_path)

        # Znajdź wspólne nazwy (pary plików)
        common_names = set(archive_by_name.keys()) & set(image_by_name.keys())

        # Oblicz całkowitą liczbę operacji do wykonania
        total_operations = len(common_names)

        if progress_callback:
            progress_callback(
                0,
                total_operations,
                f"Znaleziono {total_operations} par plików do przetworzenia",
            )

        logger.info(f"Found {total_operations} file pairs to process")
        
        created_assets = []
        current_operation = 0

        # Dla każdej pary utwórz plik .asset
        for name in sorted(common_names):  # Sortowanie dla konsystencji
            current_operation += 1

            if progress_callback:
                progress_callback(
                    current_operation, total_operations, f"Przetwarzanie: {name}"
                )

            archive_path = archive_by_name[name]
            image_path = image_by_name[name]

            # Utwórz plik .asset
            asset_path = _create_single_asset(name, archive_path, image_path, folder_path)
            if asset_path:
                created_assets.append(asset_path)
            else:
                logger.warning(f"Failed to create asset for: {name}")

        # Utwórz plik z plikami bez pary
        if progress_callback:
            progress_callback(
                total_operations, total_operations, "Tworzenie pliku z plikami bez pary..."
            )

        unpair_file_path = create_unpair_files_json(folder_path, archive_by_name, image_by_name, common_names)
        if unpair_file_path:
            logger.info(f"Created unpair_files.json at: {unpair_file_path}")
        else:
            logger.warning("Failed to create unpair_files.json")

        # Finalne podsumowanie
        success_msg = f"Zakończono! Utworzono {len(created_assets)} plików .asset"
        logger.info(success_msg)
        if progress_callback:
            progress_callback(total_operations, total_operations, success_msg)

        return created_assets

    except Exception as e:
        error_msg = f"Unexpected error during asset scanning: {e}"
        logger.error(error_msg)
        if progress_callback:
            progress_callback(0, 0, error_msg)
        return []
```

---

## ✅ CHECKLISTA WERYFIKACYJNA (DO WYPEŁNIENIA PRZED WDROŻENIEM)

#### **FUNKCJONALNOŚCI DO WERYFIKACJI:**

- [ ] **Funkcjonalność podstawowa** - czy scanner nadal prawidłowo paruje pliki archiwów z obrazami
- [ ] **API kompatybilność** - czy find_and_create_assets() działa identycznie jak wcześniej dla gallery_tab.py
- [ ] **Obsługa błędów** - czy błędy są teraz prawidłowo logowane i obsługiwane
- [ ] **Walidacja danych** - czy nieprawidłowe parametry są odrzucane z odpowiednimi komunikatami
- [ ] **Logowanie** - czy system logowania działa bez spamowania, INFO dla ważnych operacji, DEBUG dla szczegółów
- [ ] **Konfiguracja** - czy rozszerzenia plików są teraz łatwo konfigurowalne przez FILE_EXTENSIONS
- [ ] **Cache** - czy nie wprowadzono niepotrzebnego cache'owania (funkcje powinny być stateless)
- [ ] **Thread safety** - czy kod nadal jest thread-safe (nie używa globalnych zmiennych stanu)
- [ ] **Memory management** - czy nie ma wycieków pamięci, szczególnie przy dużych folderach
- [ ] **Performance** - czy wydajność skanowania nie została pogorszona przez dodatkowe logowanie

#### **ZALEŻNOŚCI DO WERYFIKACJI:**

- [ ] **Importy** - czy nowy import logging działa poprawnie
- [ ] **Zależności zewnętrzne** - czy core.thumbnail import nadal działa poprawnie
- [ ] **Zależności wewnętrzne** - czy gallery_tab.py nadal wywołuje scanner poprawnie
- [ ] **Cykl zależności** - czy nie wprowadzono cyklicznych importów
- [ ] **Backward compatibility** - czy API find_and_create_assets jest 100% kompatybilne wstecz
- [ ] **Interface contracts** - czy signature funkcji publicznych nie uległ zmianie
- [ ] **Event handling** - czy progress_callback jest wywoływany prawidłowo
- [ ] **Signal/slot connections** - nie dotyczy tego modułu
- [ ] **File I/O** - czy operacje na plikach .asset i unpair_files.json działają poprawnie

#### **TESTY WERYFIKACYJNE:**

- [ ] **Test jednostkowy** - czy _test/test_scanner.py przechodzi wszystkie testy
- [ ] **Test integracyjny** - czy integration z gallery_tab.py i thumbnail.py działa
- [ ] **Test regresyjny** - czy nie wprowadzono regresji w podstawowej funkcjonalności
- [ ] **Test wydajnościowy** - czy skanowanie dużego folderu (>100 plików) jest co najmniej tak samo szybkie

#### **KRYTERIA SUKCESU:**

- [ ] **WSZYSTKIE CHECKLISTY MUSZĄ BYĆ ZAZNACZONE** przed wdrożeniem
- [ ] **BRAK FAILED TESTS** - wszystkie testy muszą przejść
- [ ] **PERFORMANCE BUDGET** - wydajność nie pogorszona o więcej niż 5%
- [ ] **CODE COVERAGE** - pokrycie kodu nie spadło poniżej 80%