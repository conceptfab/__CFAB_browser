import logging
import os
import time
from pathlib import Path
from typing import Callable, Optional, Tuple

from PIL import Image, ImageFile, UnidentifiedImageError
from PyQt6.QtCore import QObject, Qt, pyqtSignal, QThreadPool, QRunnable, QTimer
from PyQt6.QtGui import QPixmap

from core.json_utils import load_from_file

# Dodanie loggera dla modułu
logger = logging.getLogger(__name__)

# Alias dla skrócenia długich linii
LANCZOS = Image.Resampling.LANCZOS

# Włączenie obsługi truncated images
ImageFile.LOAD_TRUNCATED_IMAGES = True

# Obsługiwane formaty obrazów
SUPPORTED_FORMATS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff", ".tga"}


class ThumbnailLoaderWorker(QObject):
    """Worker do asynchronicznego ładowania i skalowania miniatur"""

    thumbnail_loaded = pyqtSignal(str, QPixmap)  # path, pixmap
    loading_error = pyqtSignal(str, str)  # path, error_message

    def __init__(self):
        super().__init__()

    def load_thumbnail(self, path: str, size: int):
        """Ładuje i skaluje miniaturkę asynchronicznie"""
        try:
            if not os.path.exists(path):
                self.loading_error.emit(path, f"Plik nie istnieje: {path}")
                return

            pixmap = QPixmap(path)
            if pixmap.isNull():
                self.loading_error.emit(path, f"Nie można załadować obrazu: {path}")
                return

            scaled_pixmap = pixmap.scaled(
                size,
                size,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            self.thumbnail_loaded.emit(path, scaled_pixmap)
            logger.debug(f"Załadowano i przeskalowano miniaturkę: {path}")
        except Exception as e:
            logger.error(f"Błąd podczas ładowania miniaturki {path}: {e}")
            self.loading_error.emit(path, f"Błąd ładowania miniaturki: {e}")


class ThumbnailCache:
    """LRU cache dla załadowanych miniatur QPixmap"""

    def __init__(self, maxsize=100):
        self._cache = {}
        self._maxsize = maxsize
        self._access_order = []

    def get(self, key: str) -> Optional[QPixmap]:
        """Pobiera miniaturkę z cache"""
        if key in self._cache:
            # Przenieś na koniec listy (ostatnio używane)
            self._access_order.remove(key)
            self._access_order.append(key)
            return self._cache[key]
        return None

    def put(self, key: str, pixmap: QPixmap):
        """Dodaje miniaturkę do cache"""
        if key in self._cache:
            # Aktualizuj pozycję w liście
            self._access_order.remove(key)
        else:
            # Sprawdź czy cache jest pełny
            if len(self._cache) >= self._maxsize:
                # Usuń najstarszy element
                oldest_key = self._access_order.pop(0)
                del self._cache[oldest_key]

        self._cache[key] = pixmap
        self._access_order.append(key)

    def clear(self):
        """Czyści cache"""
        self._cache.clear()
        self._access_order.clear()

    def size(self) -> int:
        """Zwraca rozmiar cache"""
        return len(self._cache)


# Globalna instancja cache
_thumbnail_cache = ThumbnailCache(maxsize=200)


class ThumbnailConfigManager:
    """Menedżer konfiguracji z cache'owaniem dla thumbnail processing"""

    _instance = None
    _config_cache = None
    _config_timestamp = None
    _cache_settings = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_thumbnail_config(self, force_reload=False):
        """
        Pobiera konfigurację thumbnail z cache'owaniem

        Args:
            force_reload (bool): Wymusza ponowne ładowanie konfiguracji

        Returns:
            dict: Konfiguracja thumbnail lub domyślna konfiguracja
        """
        config_path = Path(__file__).parent.parent / "config.json"

        try:
            # Sprawdź czy cache jest aktualny
            if not force_reload and self._is_cache_valid(config_path):
                return self._cache_settings

            # Załaduj konfigurację
            config = load_from_file(config_path)

            # Walidacja i przygotowanie ustawień thumbnail
            thumbnail_size = config.get("thumbnail", 256)
            if not isinstance(thumbnail_size, int) or thumbnail_size <= 0:
                logger.warning(
                    f"Invalid thumbnail size in config: {thumbnail_size}, using default 256"
                )
                thumbnail_size = 256

            # Przygotuj complete settings
            self._cache_settings = {
                "size": thumbnail_size,
                "quality": config.get("thumbnail_quality", 85),
                "format": config.get("thumbnail_format", "WEBP"),
                "cache_dir_name": config.get("cache_dir_name", ".cache"),
                "progressive": config.get("thumbnail_progressive", False),
            }

            # Zapisz timestamp cache
            self._config_timestamp = config_path.stat().st_mtime

            logger.debug(f"Thumbnail config loaded: size={thumbnail_size}")
            return self._cache_settings

        except FileNotFoundError:
            logger.warning(f"Config file not found: {config_path}, using defaults")
            return self._get_default_config()
        except (ValueError, UnicodeDecodeError) as e:
            logger.error(f"Invalid JSON in config: {e}, using defaults")
            return self._get_default_config()
        except Exception as e:
            logger.error(f"Error loading thumbnail config: {e}, using defaults")
            return self._get_default_config()

    def _is_cache_valid(self, config_path):
        """Sprawdza czy cache konfiguracji jest aktualny"""
        if self._cache_settings is None or self._config_timestamp is None:
            return False

        try:
            current_timestamp = config_path.stat().st_mtime
            return current_timestamp == self._config_timestamp
        except OSError:
            return False

    def _get_default_config(self):
        """Zwraca domyślną konfigurację thumbnail"""
        return {
            "size": 256,
            "quality": 85,
            "format": "WEBP",
            "cache_dir_name": ".cache",
            "progressive": False,
        }


class ThumbnailCacheManager:
    """Menedżer cache dla thumbnails z intelligent validation"""

    def __init__(self, cache_dir_name=".cache"):
        self.cache_dir_name = cache_dir_name

    def get_cache_path(self, image_path: Path) -> Path:
        """Zwraca ścieżkę do cache directory dla danego obrazu"""
        work_dir = image_path.parent
        cache_dir = work_dir / self.cache_dir_name
        return cache_dir

    def get_thumbnail_path(self, image_path: Path) -> Path:
        """Zwraca ścieżkę do thumbnail file"""
        cache_dir = self.get_cache_path(image_path)
        thumbnail_filename = image_path.stem + ".thumb"
        return cache_dir / thumbnail_filename

    def ensure_cache_dir(self, cache_dir: Path) -> bool:
        """
        Zapewnia że cache directory istnieje

        Args:
            cache_dir (Path): Ścieżka do cache directory

        Returns:
            bool: True jeśli directory istnieje lub został utworzony
        """
        try:
            if not cache_dir.exists():
                cache_dir.mkdir(parents=True, exist_ok=True)
                logger.debug(f"Created cache directory: {cache_dir}")
            return True
        except PermissionError:
            logger.error(f"Permission denied creating cache directory: {cache_dir}")
            return False
        except Exception as e:
            logger.error(f"Error creating cache directory {cache_dir}: {e}")
            return False

    def is_thumbnail_current(self, image_path: Path, thumbnail_size: int) -> bool:
        """
        Sprawdza czy thumbnail jest aktualny

        Args:
            image_path (Path): Ścieżka do obrazu źródłowego
            thumbnail_size (int): Wymagany rozmiar thumbnail

        Returns:
            bool: True jeśli thumbnail jest aktualny
        """
        try:
            thumbnail_path = self.get_thumbnail_path(image_path)

            # Sprawdź czy thumbnail istnieje
            if not thumbnail_path.exists():
                return False

            # Sprawdź czy źródło jest nowsze niż thumbnail
            source_mtime = image_path.stat().st_mtime
            thumbnail_mtime = thumbnail_path.stat().st_mtime

            if source_mtime > thumbnail_mtime:
                logger.debug(f"Source image newer than thumbnail: {image_path.name}")
                return False

            # Sprawdź czy thumbnail ma poprawny rozmiar
            try:
                with Image.open(thumbnail_path) as thumb_img:
                    if thumb_img.size != (thumbnail_size, thumbnail_size):
                        logger.debug(
                            f"Thumbnail size mismatch for {image_path.name}: {thumb_img.size} vs {(thumbnail_size, thumbnail_size)}"
                        )
                        return False
            except Exception as e:
                logger.warning(f"Cannot verify thumbnail {thumbnail_path}: {e}")
                return False

            logger.debug(f"Thumbnail is current: {thumbnail_path.name}")
            return True

        except Exception as e:
            logger.error(f"Error checking thumbnail currency for {image_path}: {e}")
            return False

    def cleanup_old_thumbnails(self, cache_dir: Path, current_size: int):
        """
        Czyści stare thumbnails które mają inny rozmiar

        Args:
            cache_dir (Path): Cache directory
            current_size (int): Aktualny wymagany rozmiar
        """
        try:
            if not cache_dir.exists():
                return

            for thumb_file in cache_dir.glob("*.thumb"):
                try:
                    with Image.open(thumb_file) as img:
                        if img.size != (current_size, current_size):
                            thumb_file.unlink()
                            logger.debug(
                                f"Removed outdated thumbnail: {thumb_file.name}"
                            )
                except Exception as e:
                    logger.warning(f"Error checking thumbnail {thumb_file}: {e}")

        except Exception as e:
            logger.error(f"Error during thumbnail cleanup: {e}")


class ThumbnailProcessor:
    """Procesor thumbnails z optimized image processing"""

    def __init__(self):
        self.config_manager = ThumbnailConfigManager()
        self.cache_manager = None  # Będzie zainicjalizowany przy pierwszym użyciu

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

        # Inicjalizuj cache manager jeśli potrzebny
        if self.cache_manager is None:
            self.cache_manager = ThumbnailCacheManager(config["cache_dir_name"])

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

    def _validate_input(self, filename: str) -> Path:
        """Waliduje input parameters"""
        if not filename or not isinstance(filename, str):
            raise ValueError(f"Invalid filename parameter: {filename}")

        image_path = Path(filename)

        if not image_path.exists():
            raise FileNotFoundError(f"Image file does not exist: {filename}")

        if image_path.suffix.lower() not in SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported image format: {image_path.suffix}")

        return image_path

    def _process_and_save_thumbnail(self, image_path: Path, config: dict):
        """Przetwarza i zapisuje thumbnail z atomic operations"""
        thumbnail_size = config["size"]
        quality = config["quality"]
        output_format = config["format"]

        # Upewnij się że cache_manager jest zainicjalizowany
        if self.cache_manager is None:
            self.cache_manager = ThumbnailCacheManager(config["cache_dir_name"])

        # Określ ścieżki
        thumbnail_path = self.cache_manager.get_thumbnail_path(image_path)
        temp_path = thumbnail_path.with_suffix(".tmp")

        try:
            # Otwórz i przetwórz obraz
            with Image.open(image_path) as img:
                # Konwertuj format jeśli potrzeba
                processed_img = self._convert_image_format(img)

                # Przeskaluj i przyciąć
                thumbnail_img = self._resize_and_crop(processed_img, thumbnail_size)

                # Zapisz atomically (najpierw do temp file, potem rename)
                self._save_thumbnail_atomic(
                    thumbnail_img, temp_path, thumbnail_path, output_format, quality
                )

        except UnidentifiedImageError:
            raise ValueError(f"Cannot identify image format: {image_path}")
        except Image.DecompressionBombError:
            raise ValueError(
                f"Image too large (decompression bomb protection): {image_path}"
            )
        except MemoryError:
            raise RuntimeError(f"Insufficient memory to process image: {image_path}")
        except Exception as e:
            # Cleanup temp file jeśli istnieje
            if temp_path.exists():
                try:
                    temp_path.unlink()
                except OSError:
                    pass
            raise RuntimeError(f"Image processing error: {e}")

    def _convert_image_format(self, img: Image.Image) -> Image.Image:
        """Konwertuje obraz do odpowiedniego formatu z zachowaniem przezroczystości"""
        # Zachowaj przezroczystość dla formatów które ją obsługują
        if img.mode in ("RGBA", "LA"):
            # RGBA i LA już mają alpha channel - zachowaj jak jest
            return img
        elif img.mode == "P":
            # Konwertuj palette do RGBA aby zachować przezroczystość
            return img.convert("RGBA")
        elif img.mode == "L":
            # Grayscale konwertuj do RGB (nie ma alpha)
            return img.convert("RGB")
        elif img.mode not in ("RGB", "RGBA"):
            # Inne formaty konwertuj do RGB
            return img.convert("RGB")

        return img

    def _resize_and_crop(self, img: Image.Image, thumbnail_size: int) -> Image.Image:
        """
        Przeskalowuje i przycina obraz do kwadratu z intelligent cropping

        UWAGA: Ta funkcja nie podlega audytowi!

        Args:
            img: Obraz PIL
            thumbnail_size: Docelowy rozmiar (kwadrat)

        Returns:
            Przetworzony obraz
        """
        original_width, original_height = img.size

        # Oblicz scale factor aby mniejszy wymiar pasował do thumbnail_size
        scale_factor = thumbnail_size / min(original_width, original_height)
        new_width = int(original_width * scale_factor)
        new_height = int(original_height * scale_factor)

        # Przeskaluj obraz
        img = img.resize((new_width, new_height), LANCZOS)

        # Wyznacz obszar do przycięcia
        if new_width > thumbnail_size:
            # Obraz szerszy - przyciąć od lewej strony
            crop_box = (0, 0, thumbnail_size, thumbnail_size)
        elif new_height > thumbnail_size:
            # Obraz wyższy - przyciąć od góry
            crop_box = (0, 0, thumbnail_size, thumbnail_size)
        else:
            # Obraz już ma odpowiedni rozmiar
            crop_box = (0, 0, thumbnail_size, thumbnail_size)

        return img.crop(crop_box)

    def _save_thumbnail_atomic(
        self,
        img: Image.Image,
        temp_path: Path,
        final_path: Path,
        output_format: str,
        quality: int,
    ):
        """Zapisuje thumbnail atomically z obsługą przezroczystości"""
        try:
            # Zapisz do temp file
            save_kwargs = {"format": output_format, "quality": quality}

            if output_format.upper() == "WEBP":
                save_kwargs["method"] = 6  # Najlepsza kompresja WebP
                save_kwargs["lossless"] = False
                # WebP obsługuje przezroczystość - nie dodawaj dodatkowych parametrów
                # które mogłyby ją zniszczyć
            elif output_format.upper() in ("JPEG", "JPG"):
                save_kwargs["optimize"] = True
                save_kwargs["progressive"] = True
                # JPEG nie obsługuje przezroczystości - jeśli obraz ma alpha,
                # PIL automatycznie użyje białego tła

            img.save(temp_path, **save_kwargs)

            # Atomic rename
            temp_path.replace(final_path)

        except Exception as e:
            # Cleanup temp file
            if temp_path.exists():
                try:
                    temp_path.unlink()
                except OSError:
                    pass
            raise


# Globalna instancja processora dla performance
_thumbnail_processor = None


def process_thumbnail(filename: str, async_mode: bool = False) -> Tuple[str, int]:
    """
    Funkcja przetwarzająca thumbnail dla podanego pliku.

    UWAGA: To jest wrapper function dla backward compatibility.
    Rzeczywiste przetwarzanie odbywa się w ThumbnailProcessor.

    Args:
        filename (str): Nazwa pliku do przetworzenia
        async_mode (bool): Jeśli True, przetwarzanie odbywa się asynchronicznie
                          w QThreadPool (dla nowych implementacji)

    Returns:
        tuple[str, int]: Krotka zawierająca nazwę pliku i wartość thumbnail
        z config.json
        
        UWAGA: W trybie asynchronicznym zwraca natychmiast (filename, 0),
        a rzeczywisty wynik będzie dostępny przez sygnał thumbnail_generated
        w AsyncThumbnailManager

    Raises:
        FileNotFoundError: Gdy plik nie istnieje (tylko tryb synchroniczny)
        ValueError: Gdy plik ma nieprawidłowy format (tylko tryb synchroniczny)
        RuntimeError: Przy błędach przetwarzania lub I/O (tylko tryb synchroniczny)
    """
    global _thumbnail_processor

    # Lazy initialization processora
    if _thumbnail_processor is None:
        _thumbnail_processor = ThumbnailProcessor()

    # Tryb asynchroniczny - deleguj do AsyncThumbnailManager
    if async_mode:
        async_manager = get_async_thumbnail_manager()
        async_manager.process_thumbnail_async(filename)
        # W trybie async zwracamy natychmiast - rzeczywisty wynik przez sygnał
        return (filename, 0)

    # Tryb synchroniczny - zachowuje pełną kompatybilność wsteczną
    try:
        return _thumbnail_processor.process_image(filename)
    except (FileNotFoundError, ValueError) as e:
        # Re-raise validation errors bez zmiany
        logger.error(f"Thumbnail processing failed for {filename}: {e}")
        raise
    except Exception as e:
        # Wrap unexpected errors w RuntimeError dla consistency
        logger.error(f"Unexpected error processing thumbnail {filename}: {e}")
        raise RuntimeError(f"Thumbnail processing failed: {e}")


def process_thumbnails_batch(
    filenames: list[str], progress_callback: Optional[Callable] = None, async_mode: bool = False
) -> list[Tuple[str, int, bool]]:
    """
    Przetwarza wiele thumbnails w batch z progress tracking

    Args:
        filenames: Lista ścieżek do plików obrazów
        progress_callback: Opcjonalna funkcja callback (current, total, filename)
        async_mode: Jeśli True, używa asynchronicznego przetwarzania

    Returns:
        Lista krotek (filename, thumbnail_size, success)
        
        UWAGA: W trybie asynchronicznym zwraca natychmiast listę (filename, 0, True)
        dla wszystkich plików, a rzeczywiste rezultaty będą dostępne przez sygnały
    """
    global _thumbnail_processor

    if _thumbnail_processor is None:
        _thumbnail_processor = ThumbnailProcessor()

    if not filenames:
        return []

    # Tryb asynchroniczny - deleguj wszystkie pliki do AsyncThumbnailManager
    if async_mode:
        async_manager = get_async_thumbnail_manager()
        results = []
        total_files = len(filenames)
        
        logger.debug(f"Starting async batch thumbnail processing: {total_files} files")
        
        for i, filename in enumerate(filenames):
            if progress_callback:
                progress_callback(i + 1, total_files, filename)
            
            async_manager.process_thumbnail_async(filename)
            results.append((filename, 0, True))  # Placeholder results
        
        logger.debug(f"Scheduled {total_files} thumbnails for async processing")
        return results

    # Tryb synchroniczny - zachowuje pełną kompatybilność wsteczną
    results = []
    total_files = len(filenames)

    logger.debug(f"Starting batch thumbnail processing: {total_files} files")

    for i, filename in enumerate(filenames):
        try:
            if progress_callback:
                progress_callback(i + 1, total_files, filename)

            result_filename, thumbnail_size = _thumbnail_processor.process_image(
                filename
            )
            results.append((result_filename, thumbnail_size, True))

        except Exception as e:
            logger.warning(f"Failed to process {filename}: {e}")
            results.append((filename, 0, False))

    successful = sum(1 for _, _, success in results if success)
    logger.debug(f"Batch processing completed: {successful}/{total_files} successful")

    return results


def get_thumbnail_cache_stats(work_folder: str) -> dict:
    """
    Zwraca statystyki cache dla danego folderu

    Args:
        work_folder: Ścieżka do folderu roboczego

    Returns:
        Słownik ze statystykami cache
    """
    try:
        work_path = Path(work_folder)
        cache_dir = work_path / ".cache"

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
        work_path = Path(work_folder)
        cache_dir = work_path / ".cache"

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
            except OSError as e:
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
        work_path = Path(work_folder)
        cache_dir = work_path / ".cache"

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


class ThumbnailGeneratorWorker(QRunnable):
    """Worker dla asynchronicznego generowania miniatur w QThreadPool"""
    
    def __init__(self, filename: str, processor: 'ThumbnailProcessor', callback_signal: QObject = None):
        super().__init__()
        self.filename = filename
        self.processor = processor
        self.callback_signal = callback_signal
        self.setAutoDelete(True)
    
    def run(self):
        """Wykonuje generowanie miniatury w tle"""
        try:
            result = self.processor.process_image(self.filename)
            if self.callback_signal:
                # Emituj sygnał o zakończeniu
                self.callback_signal.thumbnail_generated.emit(self.filename, result[0], result[1], True, None)
        except Exception as e:
            logger.error(f"Async thumbnail generation failed for {self.filename}: {e}")
            if self.callback_signal:
                self.callback_signal.thumbnail_generated.emit(self.filename, None, 0, False, str(e))


class AsyncThumbnailManager(QObject):
    """Manager dla asynchronicznego generowania miniatur"""
    
    # Sygnał: filename, result_filename, thumbnail_size, success, error_message
    thumbnail_generated = pyqtSignal(str, str, int, bool, str)
    
    def __init__(self):
        super().__init__()
        self.thread_pool = QThreadPool()
        self.thread_pool.setMaxThreadCount(4)  # Maksymalnie 4 wątki dla generowania miniatur
        self.processor = None  # Będzie zainicjalizowany lazy
        
    def process_thumbnail_async(self, filename: str):
        """
        Procesuje miniaturę asynchronicznie w QThreadPool
        
        Args:
            filename (str): Ścieżka do pliku obrazu
        """
        if self.processor is None:
            self.processor = ThumbnailProcessor()
            
        worker = ThumbnailGeneratorWorker(filename, self.processor, self)
        self.thread_pool.start(worker)
        logger.debug(f"Scheduled async thumbnail generation for: {filename}")
    
    def wait_for_completion(self, timeout_ms: int = 30000):
        """
        Czeka na zakończenie wszystkich zadań w puli wątków
        
        Args:
            timeout_ms (int): Timeout w milisekundach
            
        Returns:
            bool: True jeśli wszystkie zadania zostały zakończone
        """
        return self.thread_pool.waitForDone(timeout_ms)
    
    def active_thread_count(self) -> int:
        """Zwraca liczbę aktywnych wątków"""
        return self.thread_pool.activeThreadCount()


# Globalna instancja managera asynchronicznego
_async_thumbnail_manager = None


def get_async_thumbnail_manager() -> AsyncThumbnailManager:
    """Pobiera globalną instancję managera asynchronicznego (singleton)"""
    global _async_thumbnail_manager
    if _async_thumbnail_manager is None:
        _async_thumbnail_manager = AsyncThumbnailManager()
    return _async_thumbnail_manager


# Przykład użycia:
if __name__ == "__main__":
    test_filename = "example.jpg"
    try:
        filename, thumbnail_size = process_thumbnail(test_filename)
        print(f"Plik: {filename}")
        print(f"Rozmiar thumbnail: {thumbnail_size}")
    except Exception as e:
        print(f"Błąd: {e}")
