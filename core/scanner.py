import glob
import logging
import os
import shutil

from core.json_utils import load_from_file, save_to_file
from core.thumbnail import process_thumbnail

# Dodanie loggera dla modułu
logger = logging.getLogger(__name__)

# Konfiguracja rozszerzeń plików obsługiwanych przez aplikację
FILE_EXTENSIONS = {
    "archives": ["zip", "rar", "sbsar"],
    "images": ["png", "jpg", "jpeg", "webp"],
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


def _scan_folder_for_files(folder_path):
    """
    Skanuje folder w poszukiwaniu plików archiwów i obrazów

    Args:
        folder_path (str): Ścieżka do folderu

    Returns:
        tuple: (archive_by_name, image_by_name) - słowniki plików według nazw
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
        logger.debug(f"Archive file: {archive_file} -> name: '{name_without_ext}' -> lower: '{name_lower}'")
        archive_by_name[name_lower] = archive_file

    # Grupuj pliki obrazów według nazwy (case-insensitive)
    for image_file in image_files:
        name_without_ext = os.path.splitext(os.path.basename(image_file))[0]
        name_lower = name_without_ext.lower()  # Konwertuj na małe litery dla porównania
        logger.debug(f"Image file: {image_file} -> name: '{name_without_ext}' -> lower: '{name_lower}'")
        image_by_name[name_lower] = image_file

    logger.debug(f"Archive by name: {list(archive_by_name.keys())}")
    logger.debug(f"Image by name: {list(image_by_name.keys())}")
    logger.debug(
        f"Found {len(archive_files)} archive files and {len(image_files)} image files"
    )
    return archive_by_name, image_by_name


def _check_texture_folders_presence(folder_path):
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


def _scan_for_special_folders(folder_path: str) -> list[dict]:
    """
    Skanuje folder w poszukiwaniu specjalnych folderów (tex, textures, maps).

    Args:
        folder_path (str): Ścieżka do folderu do skanowania.

    Returns:
        list: Lista słowników reprezentujących znalezione specjalne foldery.
    """
    special_folders_data = []
    special_folder_names = ["tex", "textures", "maps"]

    for folder_name in special_folder_names:
        full_path = os.path.join(folder_path, folder_name)
        if os.path.isdir(full_path):
            special_folders_data.append({
                "type": "special_folder",
                "name": folder_name,
                "folder_path": full_path
            })
            logger.debug(f"Found special folder: {full_path}")
    return special_folders_data


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
        textures_in_archive = _check_texture_folders_presence(folder_path)

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
            "unpaired_archives": sorted(
                unpaired_archives
            ),  # Sortowanie dla konsystencji
            "unpaired_previews": sorted(unpaired_previews),
        }

        # Ścieżka do pliku unpair_files.json
        unpair_file_path = os.path.join(folder_path, "unpair_files.json")

        # Zapisz plik JSON
        save_to_file(unpair_data, unpair_file_path, indent=True)

        logger.debug(
            f"Created unpair_files.json with {len(unpaired_archives)} unpaired archives and {len(unpaired_previews)} unpaired previews"
        )
        return unpair_file_path

    except PermissionError as e:
        logger.error(f"Permission denied creating unpair file in {folder_path}: {e}")
        return None
    except Exception as e:
        logger.error(f"Error creating unpair_files.json in {folder_path}: {e}")
        return None


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
        list: Lista słowników z danymi assetów i specjalnych folderów
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

    logger.debug(f"Starting asset scan in folder: {folder_path}")

    try:
        all_found_items = []

        # 1. Skanuj specjalne foldery
        special_folders = _scan_for_special_folders(folder_path)
        all_found_items.extend(special_folders)
        logger.debug(f"Found {len(special_folders)} special folders")

        # 2. Skanuj folder w poszukiwaniu plików asset
        archive_by_name, image_by_name = _scan_folder_for_files(folder_path)

        # Znajdź wspólne nazwy (pary plików)
        common_names = set(archive_by_name.keys()) & set(image_by_name.keys())
        
        logger.debug(f"Common names (pairs): {sorted(common_names)}")
        logger.debug(f"Archive names: {sorted(archive_by_name.keys())}")
        logger.debug(f"Image names: {sorted(image_by_name.keys())}")

        # Oblicz całkowitą liczbę operacji do wykonania
        total_operations = len(common_names)

        if progress_callback:
            progress_callback(
                0,
                total_operations,
                f"Znaleziono {total_operations} par plików do przetworzenia",
            )

        logger.debug(f"Found {total_operations} file pairs to process")

        current_operation = 0

        # Dla każdej pary utwórz plik .asset
        for name_lower in sorted(common_names):  # Sortowanie dla konsystencji
            current_operation += 1

            if progress_callback:
                progress_callback(
                    current_operation, total_operations, f"Przetwarzanie: {name_lower}"
                )

            archive_path = archive_by_name[name_lower]
            image_path = image_by_name[name_lower]

            # Użyj oryginalnej nazwy pliku (z zachowaniem wielkości liter) z pliku archiwum
            original_name = os.path.splitext(os.path.basename(archive_path))[0]

            # Utwórz plik .asset i pobierz jego dane
            asset_data = _create_single_asset(
                original_name, archive_path, image_path, folder_path
            )
            if asset_data:
                all_found_items.append(asset_data)
            else:
                logger.warning(f"Failed to create asset for: {original_name}")

        # Utwórz plik z plikami bez pary
        if progress_callback:
            progress_callback(
                total_operations,
                total_operations,
                "Tworzenie pliku z plikami bez pary...",
            )

        unpair_file_path = create_unpair_files_json(
            folder_path, archive_by_name, image_by_name, common_names
        )
        if unpair_file_path:
            logger.debug(f"Created unpair_files.json at: {unpair_file_path}")
        else:
            logger.warning("Failed to create unpair_files.json")

        # Finalne podsumowanie
        success_msg = f"Zakończono! Znaleziono {len(all_found_items)} elementów (assetów i folderów)"
        logger.debug(success_msg)
        if progress_callback:
            progress_callback(total_operations, total_operations, success_msg)

        return all_found_items

    except Exception as e:
        error_msg = f"Unexpected error during asset scanning: {e}"
        logger.error(error_msg)
        if progress_callback:
            progress_callback(0, 0, error_msg)
        return []


def load_existing_assets(folder_path: str) -> list[dict]:
    """
    Ładuje istniejące pliki .asset z danego folderu.

    Args:
        folder_path (str): Ścieżka do folderu do załadowania assetów.

    Returns:
        list: Lista słowników z danymi istniejących assetów.
    """
    if not folder_path or not os.path.exists(folder_path):
        logger.warning(f"Folder nie istnieje lub jest pusty: {folder_path}")
        return []

    loaded_assets = []
    special_folders = _scan_for_special_folders(folder_path)
    loaded_assets.extend(special_folders)

    for item in os.listdir(folder_path):
        if item.endswith(".asset"):
            asset_file_path = os.path.join(folder_path, item)
            try:
                asset_data = load_from_file(asset_file_path)
                if asset_data:
                    # Upewnij się, że folder_path jest dodany do danych assetu
                    asset_data["folder_path"] = folder_path
                    asset_data["type"] = "asset" # Upewnij się, że typ jest poprawny
                    loaded_assets.append(asset_data)
            except Exception as e:
                logger.error(f"Błąd ładowania pliku .asset {asset_file_path}: {e}")
    logger.debug(f"Załadowano {len(loaded_assets)} istniejących assetów z {folder_path}")
    return loaded_assets


# Przykład użycia
if __name__ == "__main__":
    # Przykład wywołania funkcji
    # find_and_create_assets("ścieżka/do/folderu")
    pass
