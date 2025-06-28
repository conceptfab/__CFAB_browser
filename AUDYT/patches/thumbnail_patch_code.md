# PATCH CODE: thumbnail.py

**Wersja: 1.0**

**Data: 2025-06-28**

**Autor: Gemini**

---

## 🎯 OPIS ZMIAN

1.  **Użycie centralnej konfiguracji:** Funkcje pomocnicze teraz pobierają nazwę katalogu cache z `ThumbnailConfigManager`.
2.  **Poprawa obsługi wyjątków:** Zastąpiono goły `except:` w `_is_cache_valid`.
3.  **Optymalizacja inicjalizacji:** Uproszczono inicjalizację `ThumbnailCacheManager`.

## 💻 KOD

### Zmiana 1: Poprawa `_is_cache_valid`

```python
    def _is_cache_valid(self, config_path):
        """Sprawdza czy cache konfiguracji jest aktualny"""
        if self._cache_settings is None or self._config_timestamp is None:
            return False

        try:
            current_timestamp = config_path.stat().st_mtime
            return current_timestamp == self._config_timestamp
        except FileNotFoundError:
            return False
```

### Zmiana 2: Poprawa `ThumbnailProcessor`

```python
class ThumbnailProcessor:
    """Procesor thumbnails z optimized image processing"""

    def __init__(self):
        self.config_manager = ThumbnailConfigManager()
        config = self.config_manager.get_thumbnail_config()
        self.cache_manager = ThumbnailCacheManager(config["cache_dir_name"])

    def process_image(self, filename: str) -> Tuple[str, int]:
        """
        Główna metoda przetwarzania thumbnail

        Args:
            filename (str): Ścieżka do pliku obrazu

        Returns:
            Tuple[str, int]: Nazwa pliku i rozmiar thumbnail

        Raises:
            FileNotFoundError: Gdy plik nie istnieje
            ValueError: Gdy plik ma nieprawidłowy format
            RuntimeError: Przy błędach przetwarzania
        """
        # Walidacja input
        image_path = self._validate_input(filename)

        # Pobierz konfigurację
        config = self.config_manager.get_thumbnail_config()
        thumbnail_size = config["size"]

        # Sprawdź czy thumbnail już istnieje i jest aktualny
        if self.cache_manager.is_thumbnail_current(image_path, thumbnail_size):
            logger.debug(f"Using cached thumbnail for: {image_path.name}")
            return filename, thumbnail_size

        # Przygotuj cache directory
        cache_dir = self.cache_manager.get_cache_path(image_path)
        if not self.cache_manager.ensure_cache_dir(cache_dir):
            raise RuntimeError(f"Cannot create cache directory: {cache_dir}")

        # Wyczyść stare thumbnails o innym rozmiarze
        self.cache_manager.cleanup_old_thumbnails(cache_dir, thumbnail_size)

        # Przetwórz obraz
        try:
            self._process_and_save_thumbnail(image_path, config)
            logger.debug(f"Generated thumbnail for: {image_path.name}")
            return filename, thumbnail_size

        except Exception as e:
            logger.error(f"Failed to process thumbnail for {filename}: {e}")
            raise RuntimeError(f"Thumbnail processing failed: {e}")
```

### Zmiana 3: Poprawa funkcji pomocniczych

```python
def get_thumbnail_cache_stats(work_folder: str) -> dict:
    """
    Zwraca statystyki cache dla danego folderu

    Args:
        work_folder: Ścieżka do folderu roboczego

    Returns:
        Słownik ze statystykami cache
    """
    try:
        config = ThumbnailConfigManager().get_thumbnail_config()
        cache_dir_name = config["cache_dir_name"]
        work_path = Path(work_folder)
        cache_dir = work_path / cache_dir_name

        if not cache_dir.exists():
            return {"cache_exists": False, "thumbnail_count": 0, "total_size_mb": 0}

        thumb_files = list(cache_dir.glob("*.thumb"))
        total_size = sum(f.stat().st_size for f in thumb_files if f.exists())

        return {
            "cache_exists": True,
            "thumbnail_count": len(thumb_files),
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "cache_dir": str(cache_dir),
        }

    except Exception as e:
        logger.error(f"Error getting cache stats for {work_folder}: {e}")
        return {"error": str(e)}


def clear_thumbnail_cache(work_folder: str, older_than_days: int = 0) -> int:
    """
    Czyści cache thumbnails w danym folderze

    Args:
        work_folder: Ścieżka do folderu roboczego
        older_than_days: Usuń tylko pliki starsze niż X dni (0 = wszystkie)

    Returns:
        Liczba usuniętych plików
    """
    try:
        config = ThumbnailConfigManager().get_thumbnail_config()
        cache_dir_name = config["cache_dir_name"]
        work_path = Path(work_folder)
        cache_dir = work_path / cache_dir_name

        if not cache_dir.exists():
            return 0

        current_time = time.time()
        cutoff_time = current_time - (older_than_days * 24 * 60 * 60)

        removed_count = 0
        for thumb_file in cache_dir.glob("*.thumb"):
            try:
                if older_than_days == 0 or thumb_file.stat().st_mtime < cutoff_time:
                    thumb_file.unlink()
                    removed_count += 1
            except Exception as e:
                logger.warning(f"Could not remove {thumb_file}: {e}")

        logger.debug(f"Removed {removed_count} thumbnail files from cache")
        return removed_count

    except Exception as e:
        logger.error(f"Error clearing thumbnail cache: {e}")
        return 0


def validate_thumbnail_integrity(work_folder: str) -> dict:
    """
    Waliduje integralność thumbnails w cache

    Args:
        work_folder: Ścieżka do folderu roboczego

    Returns:
        Słownik z wynikami walidacji
    """
    try:
        config = ThumbnailConfigManager().get_thumbnail_config()
        cache_dir_name = config["cache_dir_name"]
        work_path = Path(work_folder)
        cache_dir = work_path / cache_dir_name

        if not cache_dir.exists():
            return {"valid": 0, "invalid": 0, "errors": []}

        valid_count = 0
        invalid_count = 0
        errors = []

        for thumb_file in cache_dir.glob("*.thumb"):
            try:
                with Image.open(thumb_file) as img:
                    # Sprawdź podstawowe właściwości
                    if img.size[0] > 0 and img.size[1] > 0:
                        valid_count += 1
                    else:
                        invalid_count += 1
                        errors.append(f"{thumb_file.name}: Invalid dimensions")
            except Exception as e:
                invalid_count += 1
                errors.append(f"{thumb_file.name}: {str(e)}")

        return {"valid": valid_count, "invalid": invalid_count, "errors": errors}

    except Exception as e:
        logger.error(f"Error validating thumbnail integrity: {e}")
        return {"error": str(e)}
```
