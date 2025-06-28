# PATCH CODE: scanner.py

**Wersja: 1.0**

**Data: 2025-06-28**

**Autor: Gemini**

---

## 🎯 OPIS ZMIAN

1.  **Zmiana nazwy funkcji:** Zmieniono nazwę `_check_texture_folders_presence` na `_are_textures_in_archive` dla lepszej czytelności.
2.  **Poprawa obsługi błędów:** Dodano obsługę wyjątków w `create_thumbnail_for_asset`.
3.  **Ujednolicenie nazewnictwa:** Zapewniono spójne użycie `original_name` w `_create_single_asset`.

## 💻 KOD

### Zmiana 1: Zmiana nazwy funkcji `_check_texture_folders_presence`

```python
def _are_textures_in_archive(folder_path):
    """
    Sprawdza obecność folderów tekstur w folderze roboczym

    Args:
        folder_path (str): Ścieżka do folderu roboczego

    Returns:
        bool: True jeśli NIE znaleziono folderów tekstur (tekstury są w archiwum),
              False jeśli znaleziono foldery tekstur (tekstury są na zewnątrz)
    """
    if not folder_path or not isinstance(folder_path, str):
        logger.warning(f"Invalid folder_path parameter: {folder_path}")
        return True

    if not os.path.exists(folder_path):
        logger.warning(f"Folder does not exist: {folder_path}")
        return True

    # Lista nazw folderów do sprawdzenia
    texture_folder_names = ["tex", "textures", "maps"]

    try:
        # Sprawdź każdy folder tekstur
        for folder_name in texture_folder_names:
            texture_folder_path = os.path.join(folder_path, folder_name)
            if os.path.isdir(texture_folder_path):
                logger.debug(f"Found texture folder: {folder_name}")
                return False  # Znaleziono folder tekstur - tekstury są na zewnątrz

        logger.debug("No texture folders found - textures are in archive")
        return True  # Nie znaleziono folderów tekstur - tekstury są w archiwum

    except PermissionError:
        logger.error(f"Permission denied accessing folder: {folder_path}")
        return True
    except Exception as e:
        logger.error(f"Error checking texture folders in {folder_path}: {e}")
        return True
```

### Zmiana 2: Poprawa `_create_single_asset`

```python
def _create_single_asset(name, archive_path, image_path, folder_path):
    """
    Tworzy pojedynczy plik .asset

    Args:
        name (str): Nazwa pliku (bez rozszerzenia)
        archive_path (str): Ścieżka do pliku archiwum
        image_path (str): Ścieżka do pliku obrazu
        folder_path (str): Ścieżka do folderu docelowego

    Returns:
        dict|None: Słownik z danymi assetu lub None przy błędzie
    """
    asset_file_path = os.path.join(folder_path, f"{name}.asset")

    try:
        # Pobierz rozmiar pliku archiwum w MB
        archive_size_mb = get_file_size_mb(archive_path)

        # Sprawdź obecność folderów tekstur
        textures_in_archive = _are_textures_in_archive(folder_path)

        asset_data = {
            "type": "asset", # Dodano typ
            "name": name,
            "archive": os.path.basename(archive_path),
            "preview": os.path.basename(image_path),
            "size_mb": archive_size_mb,
            "thumbnail": None,
            "stars": None,
            "color": None,
            "textures_in_the_archive": textures_in_archive,
            "meta": {},
            "folder_path": folder_path, # Dodano folder_path
        }

        save_to_file(asset_data, asset_file_path, indent=True)

        # Utwórz thumbnail dla tego asset
        thumbnail_success = create_thumbnail_for_asset(asset_file_path, image_path)
        if thumbnail_success:
            asset_data["thumbnail"] = True # Aktualizuj dane w pamięci
        else:
            logger.warning(f"Failed to create thumbnail for asset: {name}")

        logger.debug(
            f"Created asset file: {name}.asset with textures_in_the_archive: {textures_in_archive}"
        )
        return asset_data # Zwracamy słownik z danymi assetu

    except Exception as e:
        logger.error(f"Error creating asset file for {name}: {e}")
        return None
```

### Zmiana 3: Poprawa `create_thumbnail_for_asset`

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
        asset_data = load_from_file(asset_path)

        # Ustaw thumbnail na True
        asset_data["thumbnail"] = True

        # Zapisz zaktualizowany plik asset
        save_to_file(asset_data, asset_path, indent=True)

        logger.debug(
            f"Thumbnail created successfully for asset: {os.path.basename(asset_path)}"
        )
        return True

    except (ValueError, UnicodeDecodeError) as e:
        logger.error(f"Invalid JSON in asset file {asset_path}: {e}")
        return False
    except PermissionError as e:
        logger.error(f"Permission denied accessing files: {e}")
        return False
    except Exception as e:
        logger.error(f"Error creating thumbnail for asset {asset_path}: {e}")
        return False
```
