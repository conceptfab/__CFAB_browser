import logging
from pathlib import Path
from typing import Tuple

from PIL import Image, ImageFile
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap

from core.json_utils import load_from_file

# =============================================================================
# WAŻNE: INSTRUKCJE DLA MODELI AI
# =============================================================================
#
# NIE MODYFIKUJ NASTĘPUJĄCYCH FUNKCJI:
# - _resize_to_square() - odpowiedzialna za przycinanie miniaturek
# - generate_thumbnail() - główna funkcja generowania miniaturek
#
# LOGIKA PRZYCINANIA:
# - Wysokie obrazy: przycinane od GÓRY (górny lewy róg)
# - Szerokie obrazy: przycinane od LEWEJ STRONY (górny lewy róg)
#
# KAŻDA ZMIANA W TYCH FUNKCJACH MOŻE ZNISZCZYĆ LOGIKĘ PRZYCINANIA!
# =============================================================================

# Logger dla modułu
logger = logging.getLogger(__name__)

# Włączenie obsługi truncated images
ImageFile.LOAD_TRUNCATED_IMAGES = True

# Obsługiwane formaty obrazów
SUPPORTED_FORMATS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff", ".tga"}

# Alias dla skrócenia długich linii
LANCZOS = Image.Resampling.LANCZOS


class ThumbnailGenerator:
    """Prosty generator miniaturek obrazów"""

    def __init__(self, thumbnail_size: int = 256):
        """
        Inicjalizuje generator miniaturek

        Args:
            thumbnail_size (int): Rozmiar miniaturki (domyślnie 256px)
        """
        self.thumbnail_size = thumbnail_size
        self.cache_dir_name = ".cache"

    def generate_thumbnail(self, image_path: str) -> Tuple[str, int]:
        """
        Generuje miniaturkę dla obrazu

        Args:
            image_path (str): Ścieżka do pliku obrazu

        Returns:
            Tuple[str, int]: (ścieżka do pliku, rozmiar miniaturki)

        Raises:
            FileNotFoundError: Gdy plik nie istnieje
            ValueError: Gdy plik ma nieprawidłowy format
        """
        # Walidacja
        if not image_path or not isinstance(image_path, str):
            msg = f"Nieprawidłowa ścieżka obrazu: {image_path}"
            raise ValueError(msg)

        path = Path(image_path)
        if not path.exists():
            raise FileNotFoundError(f"Plik nie istnieje: {image_path}")

        if path.suffix.lower() not in SUPPORTED_FORMATS:
            raise ValueError(f"Nieobsługiwany format: {path.suffix}")

        # Sprawdź czy miniaturka już istnieje
        cache_dir = path.parent / self.cache_dir_name
        thumbnail_path = cache_dir / f"{path.stem}.thumb"

        if self._is_thumbnail_current(path, thumbnail_path):
            msg = f"Używam istniejącej miniaturki: {thumbnail_path}"
            logger.debug(msg)
            return str(thumbnail_path), self.thumbnail_size

        # Utwórz katalog cache jeśli nie istnieje
        cache_dir.mkdir(exist_ok=True)

        # Generuj miniaturkę
        try:
            with Image.open(path) as img:
                # Konwertuj do RGB
                if img.mode != "RGB":
                    img = img.convert("RGB")

                # Przeskaluj do kwadratu
                thumbnail = self._resize_to_square(img, self.thumbnail_size)

                # Zapisz miniaturkę
                thumbnail.save(thumbnail_path, "JPEG", quality=85, optimize=True)

            logger.debug(f"Wygenerowano miniaturkę: {thumbnail_path}")
            return str(thumbnail_path), self.thumbnail_size

        except Exception as e:
            msg = f"Błąd generowania miniaturki dla {image_path}: {e}"
            logger.error(msg)
            raise

    def _is_thumbnail_current(self, image_path: Path, thumbnail_path: Path) -> bool:
        """Sprawdza czy miniaturka jest aktualna"""
        if not thumbnail_path.exists():
            return False

        try:
            image_mtime = image_path.stat().st_mtime
            thumbnail_mtime = thumbnail_path.stat().st_mtime
            return thumbnail_mtime >= image_mtime
        except OSError:
            return False

    def _resize_to_square(self, img: Image.Image, size: int) -> Image.Image:
        """
        Przeskalowuje obraz do kwadratu z zachowaniem proporcji

        WAŻNE: NIE MODYFIKUJ TEJ FUNKCJI!
        Logika przycinania:
        - Wysokie obrazy: przycinane od GÓRY
        - Szerokie obrazy: przycinane od LEWEJ STRONY
        """
        width, height = img.size

        # Oblicz współczynnik skalowania
        scale = size / min(width, height)
        new_width = int(width * scale)
        new_height = int(height * scale)

        # Przeskaluj
        img = img.resize((new_width, new_height), LANCZOS)

        # Przyciąć do kwadratu
        if new_width > size:
            # Szerokie obrazy - przycinaj od lewej strony
            img = img.crop((0, 0, size, size))
        elif new_height > size:
            # Wysokie obrazy - przycinaj od góry
            img = img.crop((0, 0, size, size))

        return img


def get_config() -> dict:
    """Pobiera konfigurację miniaturek"""
    config_path = Path(__file__).parent.parent / "config.json"
    try:
        config = load_from_file(config_path)
        return {
            "size": config.get("thumbnail", 256),
            "cache_dir_name": config.get("cache_dir_name", ".cache"),
        }
    except Exception:
        return {"size": 256, "cache_dir_name": ".cache"}


# Globalna instancja generatora
_generator = None


def get_generator() -> ThumbnailGenerator:
    """Pobiera globalną instancję generatora"""
    global _generator
    if _generator is None:
        config = get_config()
        _generator = ThumbnailGenerator(config["size"])
    return _generator


def generate_thumbnail(image_path: str) -> Tuple[str, int]:
    """
    Główna funkcja do generowania miniaturek

    Args:
        image_path (str): Ścieżka do pliku obrazu

    Returns:
        Tuple[str, int]: (ścieżka do pliku, rozmiar miniaturki)
    """
    generator = get_generator()
    return generator.generate_thumbnail(image_path)
