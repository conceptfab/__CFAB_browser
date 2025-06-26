# 💻 PATCH KODU: scanner.py

**Data:** 2024-05-22

**Link do zasad refaktoryzacji:** [`refactoring_rules.md`](../../doc/refactoring_rules.md)

---

## 📝 OPIS ZMIAN

Ten patch implementuje kluczowe optymalizacje i poprawki architektoniczne w module `scanner.py`, zgodnie z rekomendacjami z audytu.

1.  **Optymalizacja Skanowania Plików:** Funkcja `_get_files_by_extensions` została całkowicie przepisana. Zamiast wielokrotnego użycia `glob`, teraz jednokrotnie listuje zawartość katalogu za pomocą `os.listdir`, a następnie filtruje wyniki w pamięci. Zapewnia to znaczący wzrost wydajności w folderach z dużą liczbą plików.
2.  **Niezawodność Międzyplatformowa:** Wszystkie operacje na nazwach plików i ścieżkach używają teraz `os.path.normcase`, co gwarantuje poprawne parowanie plików niezależnie od ustawień wielkości liter systemu plików.
3.  **Transakcyjne Tworzenie Zasobów:** Funkcja `_create_single_asset` została zrefaktoryzowana, aby zapewnić atomowość operacji. Plik `.asset` jest najpierw zapisywany do tymczasowej lokalizacji (`.tmp`). Dopiero po pomyślnym utworzeniu miniaturki, plik tymczasowy jest przemianowywany na docelową nazwę. W przypadku błędu, plik tymczasowy jest usuwany, co zapobiega pozostawianiu niespójnych danych.
4.  **Redukcja Operacji I/O:** Logika z usuniętej funkcji `create_thumbnail_for_asset` została zintegrowana w `_create_single_asset`, eliminując potrzebę ponownego otwierania i zapisywania pliku `.asset`.
5.  **Wstrzykiwanie Zależności:** Główna funkcja `find_and_create_assets` przyjmuje teraz `thumbnail_processor` jako argument, co odwraca zależność i uniezależnia `scanner` od konkretnej implementacji tworzenia miniaturek z modułu `thumbnail`.

---

## ✂️ FRAGMENTY KODU DO ZASTOSOWANIA

### 1. Zmodyfikowane importy i stałe

```python
import glob
import json
import logging
import os
import tempfile # Dodany import
from typing import Callable # Dodany import

# Usunięto import 'process_thumbnail'
# from core.thumbnail import process_thumbnail

logger = logging.getLogger(__name__)

# Definicja typów dla podpowiedzi
PathDict = dict[str, str]

FILE_EXTENSIONS = {
    "archives": ["zip", "rar", "sbsar"],
    "images": ["png", "jpg", "jpeg", "webp"],
}
```

### 2. Zoptymalizowana funkcja `_get_files_by_extensions`

```python
def _get_files_by_extensions(folder_path: str, extensions: list[str]) -> list[str]:
    """
    Wyszukuje pliki o podanych rozszerzeniach w jednym przejściu, ignorując wielkość liter.
    """
    try:
        all_files = os.listdir(folder_path)
    except (FileNotFoundError, PermissionError) as e:
        logger.error(f"Cannot access folder {folder_path}: {e}")
        return []

    matched_files = []
    normalized_extensions = {f".{ext.lower()}" for ext in extensions}

    for filename in all_files:
        # Normalizacja wielkości liter dla rozszerzenia
        ext_lower = os.path.splitext(filename)[1].lower()
        if ext_lower in normalized_extensions:
            full_path = os.path.join(folder_path, filename)
            if os.path.isfile(full_path):
                matched_files.append(full_path)
    return matched_files
```

### 3. Zmodyfikowana `_scan_folder_for_files` z użyciem `os.path.normcase`

```python
def _scan_folder_for_files(folder_path: str) -> tuple[PathDict, PathDict]:
    """
    Skanuje folder, używając os.path.normcase do normalizacji nazw plików.
    """
    archive_files = _get_files_by_extensions(folder_path, FILE_EXTENSIONS["archives"])
    image_files = _get_files_by_extensions(folder_path, FILE_EXTENSIONS["images"])

    archive_by_name: PathDict = {}
    image_by_name: PathDict = {}

    for file_path in archive_files:
        # Normalizacja nazwy dla klucza słownika
        base_name = os.path.basename(file_path)
        name_without_ext = os.path.splitext(base_name)[0]
        normalized_name = os.path.normcase(name_without_ext)
        if normalized_name in archive_by_name:
            logger.warning(f"Duplicate archive name found (case-insensitive): {name_without_ext}")
        archive_by_name[normalized_name] = file_path

    for file_path in image_files:
        base_name = os.path.basename(file_path)
        name_without_ext = os.path.splitext(base_name)[0]
        normalized_name = os.path.normcase(name_without_ext)
        if normalized_name in image_by_name:
            logger.warning(f"Duplicate image name found (case-insensitive): {name_without_ext}")
        image_by_name[normalized_name] = file_path

    logger.info(
        f"Found {len(archive_files)} archive files and {len(image_files)} image files"
    )
    return archive_by_name, image_by_name
```

### 4. Zrefaktoryzowana `_create_single_asset` i usunięcie `create_thumbnail_for_asset`

```python
def _create_single_asset(
    name: str,
    archive_path: str,
    image_path: str,
    folder_path: str,
    thumbnail_processor: Callable[[str], None]
) -> str | None:
    """
    Tworzy plik .asset i miniaturkę w sposób transakcyjny.
    """
    asset_path = os.path.join(folder_path, f"{name}.asset")
    tmp_asset_path = f"{asset_path}.{os.getpid()}.tmp"

    try:
        thumbnail_success = False
        try:
            thumbnail_processor(image_path)
            thumbnail_success = True
            logger.debug(f"Thumbnail processed for image: {image_path}")
        except Exception as e:
            logger.warning(f"Failed to create thumbnail for asset {name}: {e}")

        asset_data = {
            "name": name,
            "archive": os.path.basename(archive_path),
            "preview": os.path.basename(image_path),
            "size_mb": get_file_size_mb(archive_path),
            "thumbnail": thumbnail_success,
            "stars": None,
            "color": None,
            "textures_in_the_archive": _check_texture_folders_presence(folder_path),
            "meta": {},
        }

        # Zapis do pliku tymczasowego
        with open(tmp_asset_path, "w", encoding="utf-8") as asset_file:
            json.dump(asset_data, asset_file, indent=2, ensure_ascii=False)

        # Przemianowanie na docelową nazwę
        os.rename(tmp_asset_path, asset_path)

        logger.debug(f"Created asset file: {os.path.basename(asset_path)}")
        return asset_path

    except Exception as e:
        logger.error(f"Error creating asset file for {name}: {e}")
        # Sprzątanie pliku tymczasowego w razie błędu
        if os.path.exists(tmp_asset_path):
            try:
                os.remove(tmp_asset_path)
            except OSError as unlink_error:
                logger.error(f"Failed to remove temporary asset file {tmp_asset_path}: {unlink_error}")
        return None

# Usunąć całą funkcję create_thumbnail_for_asset(asset_path, image_path)
```

### 5. Zmodyfikowana funkcja `find_and_create_assets`

```python
def find_and_create_assets(
    folder_path: str,
    thumbnail_processor: Callable[[str], None],
    progress_callback: Callable[[int], None] | None = None
) -> dict[str, list[str]]:
    """
    Znajduje i tworzy pliki .asset, wstrzykując zależność do tworzenia miniaturek.
    """
    logger.info(f"Starting asset creation in folder: {folder_path}")
    archive_by_name, image_by_name = _scan_folder_for_files(folder_path)

    # ... (logika znajdowania wspólnych nazw pozostaje bez zmian)

    created_assets = []
    for i, name in enumerate(common_names):
        archive_path = archive_by_name[name]
        image_path = image_by_name[name]

        asset_file = _create_single_asset(
            os.path.splitext(os.path.basename(archive_path))[0],
            archive_path,
            image_path,
            folder_path,
            thumbnail_processor # Wstrzyknięta zależność
        )
        if asset_file:
            created_assets.append(asset_file)

        if progress_callback:
            progress = int(((i + 1) / len(common_names)) * 100)
            progress_callback(progress)

    # ... (reszta logiki bez zmian)
```
