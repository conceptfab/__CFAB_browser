import json
from pathlib import Path

from PIL import Image

# Alias dla skrócenia długich linii
LANCZOS = Image.Resampling.LANCZOS


def process_thumbnail(filename: str) -> tuple[str, int]:
    """
    Funkcja przetwarzająca thumbnail dla podanego pliku.

    Args:
        filename (str): Nazwa pliku do przetworzenia

    Returns:
        tuple[str, int]: Krotka zawierająca nazwę pliku i wartość thumbnail
        z config.json
    """
    # Wczytaj config.json
    config_path = Path(__file__).parent.parent / "config.json"

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)

        # Pobierz wartość thumbnail z config
        thumbnail_size = config.get("thumbnail")

        if thumbnail_size is None:
            raise ValueError("Brak wartości 'thumbnail' w config.json")

        # Otwórz obraz
        image_path = Path(filename)
        if not image_path.exists():
            raise FileNotFoundError(f"Plik {filename} nie istnieje")

        # Ustal folder roboczy na podstawie lokalizacji pliku źródłowego
        work_dir = image_path.parent
        cache_dir = work_dir / ".cache"
        if not cache_dir.exists():
            cache_dir.mkdir()

        with Image.open(image_path) as img:
            # Konwertuj do RGB jeśli to PNG z przezroczystością
            if img.mode in ("RGBA", "LA", "P"):
                img = img.convert("RGB")

            # Pobierz oryginalne wymiary
            original_width, original_height = img.size

            # Określ proporcje obrazu
            if original_width > original_height:
                # Obraz szeroki - przeskaluj do wysokości thumbnail_size
                # i przyciąć od lewej strony
                scale_factor = thumbnail_size / original_height
                new_width = int(original_width * scale_factor)
                new_height = thumbnail_size

                # Przeskaluj obraz
                img = img.resize((new_width, new_height), LANCZOS)

                # Przyciąć od lewej strony do kwadratu
                img = img.crop((0, 0, thumbnail_size, thumbnail_size))

            elif original_height > original_width:
                # Obraz wysoki - przeskaluj do szerokości thumbnail_size
                # i przyciąć od góry
                scale_factor = thumbnail_size / original_width
                new_width = thumbnail_size
                new_height = int(original_height * scale_factor)

                # Przeskaluj obraz
                img = img.resize((new_width, new_height), LANCZOS)

                # Przyciąć od góry do kwadratu
                img = img.crop((0, 0, thumbnail_size, thumbnail_size))

            else:
                # Obraz kwadratowy - po prostu przeskaluj
                img = img.resize((thumbnail_size, thumbnail_size), LANCZOS)

            # Zapisz jako webp z rozszerzeniem .thumb
            output_filename = image_path.stem + ".thumb"
            output_path = cache_dir / output_filename

            img.save(output_path, "WEBP", quality=85)

        return filename, thumbnail_size

    except FileNotFoundError:
        raise
    except json.JSONDecodeError:
        raise
    except Exception:
        raise


# Przykład użycia:
if __name__ == "__main__":
    test_filename = "example.jpg"
    filename, thumbnail_size = process_thumbnail(test_filename)
    print(f"Plik: {filename}")
    print(f"Rozmiar thumbnail: {thumbnail_size}")
