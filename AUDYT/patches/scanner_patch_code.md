# PATCH-CODE DLA: core/scanner.py

**Powiązany plik z analizą:** `../corrections/scanner_correction.md`
**Zasady ogólne:** `../refactoring_rules.md`

---

### PATCH 1: Uproszczenie `_get_files_by_extensions`

**Problem:** Funkcja `_get_files_by_extensions` wyszukuje pliki dwukrotnie (dla małych i dużych liter rozszerzeń), co jest nieefektywne.
**Rozwiązanie:** Uproszczenie logiki wyszukiwania plików poprzez konwersję rozszerzeń na małe litery i użycie pojedynczego wywołania `glob.glob` z `os.path.join`.

```python
# ... istniejący kod ...

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
        # Użyj glob.glob z os.path.join dla lepszej kompatybilności
        # i wyszukuj pliki niezależnie od wielkości liter rozszerzenia
        files.extend(glob.glob(os.path.join(folder_path, f"*.{ext}"), recursive=False))
        files.extend(glob.glob(os.path.join(folder_path, f"*.{ext.upper()}"), recursive=False))
    return files


# ... reszta istniejącego kodu ...
```

---

### PATCH 2: Usunięcie nieużywanego importu `shutil`

**Problem:** Moduł `shutil` jest importowany, ale nieużywany w pliku `core/scanner.py`.
**Rozwiązanie:** Usunięcie niepotrzebnego importu.

```python
import glob
import logging
import os
# import shutil  # USUNIĘTO: Moduł nie jest używany

from core.json_utils import load_from_file, save_to_file
from core.thumbnail import process_thumbnail

# ... reszta istniejącego kodu ...
```

---

### PATCH 3: Optymalizacja logowania w `_scan_folder_for_files`

**Problem:** Logowanie pełnych list nazw plików w `_scan_folder_for_files` może generować bardzo długie linie w logach.
**Rozwiązanie:** Zmiana logowania na wyświetlanie tylko liczby znalezionych plików.

```python
# ... istniejący kod ...

def _scan_folder_for_files(folder_path):
    """
    Skanuje folder w poszukiwaniu plików archiwów i obrazów

    # ... istniejący docstring ...
    """
    # Znajdź wszystkie pliki archiwum i obrazów
    archive_files = _get_files_by_extensions(folder_path, FILE_EXTENSIONS["archives"])
    image_files = _get_files_by_extensions(folder_path, FILE_EXTENSIONS["images"])

    # Słownik do przechowywania plików według nazwy (bez rozszerzenia) - case-insensitive
    archive_by_name = {}
    image_by_name = {}

    # Grupuj pliki archiwum według nazwy (case-insensitive)
    for archive_file in archive_files:
        name_without_ext = os.path.splitext(os.path.basename(archive_file))[0]
        name_lower = name_without_ext.lower()  # Konwertuj na małe litery dla porównania
        # logger.debug(f"Archive file: {archive_file} -> name: '{name_without_ext}' -> lower: '{name_lower}'") # USUNIĘTO
        archive_by_name[name_lower] = archive_file

    # Grupuj pliki obrazów według nazwy (case-insensitive)
    for image_file in image_files:
        name_without_ext = os.path.splitext(os.path.basename(image_file))[0]
        name_lower = name_without_ext.lower()  # Konwertuj na małe litery dla porównania
        # logger.debug(f"Image file: {image_file} -> name: '{name_without_ext}' -> lower: '{name_lower}'") # USUNIĘTO
        image_by_name[name_lower] = image_file

    # logger.debug(f"Archive by name: {list(archive_by_name.keys())}") # USUNIĘTO
    # logger.debug(f"Image by name: {list(image_by_name.keys())}") # USUNIĘTO
    logger.debug(
        f"Found {len(archive_files)} archive files and {len(image_files)} image files"
    )
    return archive_by_name, image_by_name


# ... reszta istniejącego kodu ...
```

---

## ✅ CHECKLISTA WERYFIKACYJNA (DO WYPEŁNIENIA PRZED WDROŻENIEM)

#### **FUNKCJONALNOŚCI DO WERYFIKACJI:**

- [ ] **Funkcjonalność podstawowa** - czy plik nadal wykonuje swoją główną funkcję.
- [ ] **API kompatybilność** - czy wszystkie publiczne metody/klasy działają jak wcześniej.
- [ ] **Obsługa błędów** - czy mechanizmy obsługi błędów nadal działają.
- [ ] **Walidacja danych** - czy walidacja wejściowych danych działa poprawnie.
- [ ] **Logowanie** - czy system logowania działa bez spamowania.
- [ ] **Konfiguracja** - czy odczytywanie/zapisywanie konfiguracji działa.
- [ ] **Cache** - czy mechanizmy cache działają poprawnie.
- [ ] **Thread safety** - czy kod jest bezpieczny w środowisku wielowątkowym.
- [ ] **Memory management** - czy nie ma wycieków pamięci.
- [ ] **Performance** - czy wydajność nie została pogorszona.

#### **ZALEŻNOŚCI DO WERYFIKACJI:**

- [ ] **Importy** - czy wszystkie importy działają poprawnie.
- [ ] **Zależności zewnętrzne** - czy zewnętrzne biblioteki są używane prawidłowo.
- [ ] **Zależności wewnętrzne** - czy powiązania z innymi modułami działają.
- [ ] **Cykl zależności** - czy nie wprowadzono cyklicznych zależności.
- [ ] **Backward compatibility** - czy kod jest kompatybilny wstecz.
- [ ] **Interface contracts** - czy interfejsy są przestrzegane.
- [ ] **Event handling** - czy obsługa zdarzeń działa poprawnie.
- [ ] **Signal/slot connections** - czy połączenia Qt działają.
- [ ] **File I/O** - czy operacje na plikach działają.

#### **TESTY WERYFIKACYJNE:**

- [ ] **Test jednostkowy** - czy wszystkie funkcje działają w izolacji.
- [ ] **Test integracyjny** - czy integracja z innymi modułami działa.
- [ ] **Test regresyjny** - czy nie wprowadzono regresji.
- [ ] **Test wydajnościowy** - czy wydajność jest akceptowalna.

#### **KRYTERIA SUKCESU:**

- [ ] **WSZYSTKIE CHECKLISTY MUSZĄ BYĆ ZAZNACZONE** przed wdrożeniem.
- [ ] **BRAK FAILED TESTS** - wszystkie testy muszą przejść.
- [ ] **PERFORMANCE BUDGET** - wydajność nie pogorszona o więcej niż 5%.
- [ ] **CODE COVERAGE** - pokrycie kodu nie spadło poniżej 80%.
