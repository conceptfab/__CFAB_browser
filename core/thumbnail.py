import logging
from pathlib import Path
from typing import Tuple

from PIL import Image, ImageFile

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
# 
# AKTUALIZACJA 2025-01-07: Dodano obsługę przezroczystości
# - Obrazy z przezroczystością zapisywane jako PNG
# - Obrazy bez przezroczystości zapisywane jako JPEG (większa wydajność)
# =============================================================================

# Logger dla modułu
logger = logging.getLogger(__name__)

# Włączenie obsługi truncated images
ImageFile.LOAD_TRUNCATED_IMAGES = True

# Obsługiwane formaty obrazów
SUPPORTED_FORMATS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff", ".tga"}

# Usunięty niepotrzebny alias LANCZOS - używany tylko raz


class ThumbnailGenerator:
    """Simple image thumbnail generator with transparency support"""

    def __init__(self, thumbnail_size: int = 256):
        """
        Initializes the thumbnail generator

        Args:
            thumbnail_size (int): Thumbnail size (default 256px)
        """
        self.thumbnail_size = thumbnail_size
        self.cache_dir_name = ".cache"

    def _has_transparency(self, img: Image.Image) -> bool:
        """
        Efficiently checks if image has transparency (OPTIMIZED)
        
        Args:
            img (Image.Image): Image to check
            
        Returns:
            bool: True if image has transparency
        """
        # Szybkie sprawdzenie trybu - najczęstsze przypadki pierwsze
        if img.mode == 'RGB':
            return False  # RGB nigdy nie ma przezroczystości
        
        if img.mode in ('RGBA', 'LA'):
            return True
        
        # Sprawdź transparency info tylko jeśli potrzeba
        return 'transparency' in img.info

    def _get_optimal_format_and_path(self, base_path: Path, has_alpha: bool) -> tuple:
        """
        Gets optimal format and path for thumbnail (OPTIMIZED)
        
        Args:
            base_path (Path): Base path for thumbnail
            has_alpha (bool): Whether image has transparency
            
        Returns:
            tuple: (thumbnail_path, format, save_kwargs)
        """
        thumbnail_path = base_path.with_suffix('.thumb')
        format_name = "WEBP"
        
        # Zoptymalizowane parametry WebP dla szybszości
        if has_alpha:
            # Dla obrazów z przezroczystością - zachowaj jakość ale przyśpiesz
            save_kwargs = {"quality": 80, "method": 4, "exact": False}
        else:
            # Dla obrazów bez przezroczystości - maksymalna szybkość
            save_kwargs = {"quality": 75, "method": 2, "exact": False}
        
        return thumbnail_path, format_name, save_kwargs

    def generate_thumbnail(self, image_path: str) -> Tuple[str, int]:
        """
        Generates a thumbnail for an image with transparency support

        Args:
            image_path (str): Path to the image file

        Returns:
            Tuple[str, int]: (thumbnail filename, thumbnail size)

        Raises:
            FileNotFoundError: If the file does not exist
            ValueError: If the file has an invalid format
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

        # Utwórz katalog cache jeśli nie istnieje
        cache_dir = path.parent / self.cache_dir_name
        cache_dir.mkdir(exist_ok=True)

        # Sprawdź czy miniaturka już istnieje (WebP z .thumb)
        thumbnail_path = cache_dir / f"{path.stem}.thumb"
        
        if thumbnail_path.exists() and self._is_thumbnail_current(path, thumbnail_path):
            msg = f"Używam istniejącej miniaturki: {thumbnail_path}"
            logger.debug(msg)
            return thumbnail_path.name, self.thumbnail_size

        # Generuj miniaturkę
        try:
            with Image.open(path) as img:
                # Sprawdź czy obraz ma przezroczystość
                has_alpha = self._has_transparency(img)
                
                # Zoptymalizowana konwersja kolorów
                target_mode = "RGBA" if has_alpha else "RGB"
                if img.mode != target_mode:
                    # Użyj szybszej konwersji dla miniaturek
                    if has_alpha and img.mode == "P":
                        # Specjalna obsługa palette z przezroczystością
                        img = img.convert("RGBA")
                    elif not has_alpha and img.mode in ("RGBA", "LA", "P"):
                        # Konwertuj z białym tłem dla lepszej wydajności
                        background = Image.new("RGB", img.size, (255, 255, 255))
                        if img.mode == "P":
                            img = img.convert("RGBA")
                        background.paste(img, mask=img.split()[-1] if img.mode == "RGBA" else None)
                        img = background
                    else:
                        img = img.convert(target_mode)

                # Przeskaluj do kwadratu
                thumbnail = self._resize_to_square(img, self.thumbnail_size)

                # Pobierz ścieżkę i format (zawsze WebP .thumb)
                final_thumbnail_path, format_name, save_kwargs = self._get_optimal_format_and_path(
                    thumbnail_path, has_alpha
                )

                # Zapisz miniaturkę w formacie WebP
                thumbnail.save(final_thumbnail_path, format_name, **save_kwargs)

            logger.debug(f"Wygenerowano miniaturkę ({format_name}): {final_thumbnail_path}")
            return final_thumbnail_path.name, self.thumbnail_size

        except Exception as e:
            msg = f"Błąd generowania miniaturki dla {image_path}: {e}"
            logger.error(msg)
            raise

    def _is_thumbnail_current(self, image_path: Path, thumbnail_path: Path) -> bool:
        """Checks if the thumbnail is up to date"""
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
        Resizes the image to a square with cropping as required:
        - Tall images: cropped from the TOP (top left corner)
        - Wide images: cropped from the LEFT (top left corner)
        """
        width, height = img.size

        # Oblicz współczynnik skalowania
        scale = size / min(width, height)
        new_width = int(width * scale)
        new_height = int(height * scale)

        # Przeskaluj
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # Przyciąć do kwadratu zgodnie z wymaganiami
        if new_width > size:
            # Szerokie obrazy - przycinaj od lewej strony (górny lewy róg)
            left = 0
            top = 0
            right = size
            bottom = size
            img = img.crop((left, top, right, bottom))
        elif new_height > size:
            # Wysokie obrazy - przycinaj od góry (górny lewy róg)
            left = 0
            top = 0
            right = size
            bottom = size
            img = img.crop((left, top, right, bottom))

        return img




def get_config() -> dict: # Gets thumbnail configuration (EXTENDED)
    config_path = Path(__file__).parent.parent / "config.json"
    try:
        config = load_from_file(config_path)
        if config is None:
            return {
                "size": 256, 
                "cache_dir_name": ".cache",
                "fast_mode": False  # Nowa opcja
            }
        return {
            "size": config.get("thumbnail", 256),
            "cache_dir_name": config.get("cache_dir_name", ".cache"),
            "fast_mode": config.get("fast_mode", False),  # Nowa opcja
        }
    except Exception:
        return {
            "size": 256, 
            "cache_dir_name": ".cache",
            "fast_mode": False
        }


# Global generator instance
_generator = None


def get_generator() -> ThumbnailGenerator:
    """Gets the global generator instance"""
    global _generator
    if _generator is None:
        config = get_config()
        _generator = ThumbnailGenerator(config["size"])
    return _generator


def generate_thumbnail(image_path: str) -> Tuple[str, int]:
    """
    Main function for generating thumbnails

    Args:
        image_path (str): Path to the image file

    Returns:
        Tuple[str, int]: (thumbnail filename, thumbnail size)
    """
    generator = get_generator()
    return generator.generate_thumbnail(image_path)
