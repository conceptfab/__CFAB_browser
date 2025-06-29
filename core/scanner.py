import logging
import os

from core.amv_models.repository_interfaces import IAssetRepository
from core.json_utils import load_from_file, save_to_file
from core.thumbnail import process_thumbnail

# Dodanie loggera dla modułu
logger = logging.getLogger(__name__)

# Konfiguracja rozszerzeń plików obsługiwanych przez aplikację
FILE_EXTENSIONS = {
    "archives": ["zip", "rar", "sbsar"],
    "images": ["png", "jpg", "jpeg", "webp"],
}


class AssetRepository(IAssetRepository):
    """
    Implementacja repozytorium assetów.

    Enkapsuluje logikę skanowania, tworzenia i ładowania assetów.
    Implementuje interfejs IAssetRepository.
    """

    def __init__(self):
        """Inicjalizuje repozytorium assetów."""
        pass

    def _get_files_by_extensions(self, folder_path: str, extensions: list) -> list:
        """
        Pomocnicza funkcja do wyszukiwania plików o określonych rozszerzeniach

        Args:
            folder_path (str): Ścieżka do folderu
            extensions (list): Lista rozszerzeń (bez kropki)

        Returns:
            list: Lista ścieżek do znalezionych plików
        """
        files = []
        ext_set = set(ext.lower() for ext in extensions)
        for entry in os.listdir(folder_path):
            full_path = os.path.join(folder_path, entry)
            if os.path.isfile(full_path):
                _, ext = os.path.splitext(entry)
                if ext and ext[1:].lower() in ext_set:
                    files.append(full_path)
        return files

    def _scan_folder_for_files(self, folder_path: str) -> tuple:
        """
        Skanuje folder w poszukiwaniu plików archiwów i obrazów

        Args:
            folder_path (str): Ścieżka do folderu

        Returns:
            tuple: (archive_by_name, image_by_name) - słowniki plików według nazw
        """
        # Znajdź wszystkie pliki archiwum i obrazów
        archive_files = self._get_files_by_extensions(
            folder_path, FILE_EXTENSIONS["archives"]
        )
        image_files = self._get_files_by_extensions(
            folder_path, FILE_EXTENSIONS["images"]
        )

        # Słownik do przechowywania plików według nazwy (bez rozszerzenia) - case-insensitive
        archive_by_name = {}
        image_by_name = {}

        # Grupuj pliki archiwum według nazwy (case-insensitive)
        for archive_file in archive_files:
            name_without_ext = os.path.splitext(os.path.basename(archive_file))[0]
            name_lower = (
                name_without_ext.lower()
            )  # Konwertuj na małe litery dla porównania
            archive_by_name[name_lower] = archive_file

        # Grupuj pliki obrazów według nazwy (case-insensitive)
        for image_file in image_files:
            name_without_ext = os.path.splitext(os.path.basename(image_file))[0]
            name_lower = (
                name_without_ext.lower()
            )  # Konwertuj na małe litery dla porównania
            image_by_name[name_lower] = image_file

        logger.debug(
            f"Found {len(archive_files)} archive files and "
            f"{len(image_files)} image files"
        )
        return archive_by_name, image_by_name

    def _check_texture_folders_presence(self, folder_path: str) -> bool:
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

    def _scan_for_special_folders(self, folder_path: str) -> list:
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
                special_folders_data.append(
                    {
                        "type": "special_folder",
                        "name": folder_name,
                        "folder_path": full_path,
                    }
                )
                logger.debug(f"Found special folder: {full_path}")
        return special_folders_data

    def _create_single_asset(
        self, name: str, archive_path: str, image_path: str, folder_path: str
    ) -> dict:
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
            # Sprawdź czy plik .asset już istnieje
            existing_asset_data = None
            if os.path.exists(asset_file_path):
                existing_asset_data = load_from_file(asset_file_path)
                logger.debug(f"Znaleziono istniejący plik .asset: {name}.asset")

            # Pobierz rozmiar pliku archiwum w MB
            archive_size_mb = self._get_file_size_mb(archive_path)

            # Sprawdź obecność folderów tekstur
            textures_in_archive = self._check_texture_folders_presence(folder_path)

            # Utwórz nowe dane assetu
            asset_data = {
                "type": "asset",  # Dodano typ
                "name": name,
                "archive": os.path.basename(archive_path),
                "preview": os.path.basename(image_path),
                "size_mb": archive_size_mb,
                "thumbnail": None,
                "stars": None,
                "color": None,
                "textures_in_the_archive": textures_in_archive,
                "meta": {},
            }

            # Jeśli istnieje poprzedni plik, zachowaj ważne dane użytkownika
            if existing_asset_data:
                # Zachowaj gwiazdki, kolor i inne dane użytkownika
                if (
                    "stars" in existing_asset_data
                    and existing_asset_data["stars"] is not None
                ):
                    asset_data["stars"] = existing_asset_data["stars"]
                    logger.debug(
                        f"Zachowano gwiazdki: {existing_asset_data['stars']} dla {name}"
                    )

                if (
                    "color" in existing_asset_data
                    and existing_asset_data["color"] is not None
                ):
                    asset_data["color"] = existing_asset_data["color"]
                    logger.debug(
                        f"Zachowano kolor: {existing_asset_data['color']} dla {name}"
                    )

                # Zachowaj miniaturę jeśli istnieje
                if (
                    "thumbnail" in existing_asset_data
                    and existing_asset_data["thumbnail"] is not None
                ):
                    asset_data["thumbnail"] = existing_asset_data["thumbnail"]
                    logger.debug(
                        f"Zachowano miniaturę: {existing_asset_data['thumbnail']} dla {name}"
                    )

                # Zachowaj meta dane
                if "meta" in existing_asset_data:
                    asset_data["meta"] = existing_asset_data["meta"]

            # Zapisz plik .asset
            save_to_file(asset_data, asset_file_path)
            logger.debug(f"Utworzono plik .asset: {name}.asset")

            return asset_data

        except Exception as e:
            logger.error(f"Błąd podczas tworzenia assetu {name}: {e}")
            return None

    def _get_file_size_mb(self, file_path: str) -> float:
        """
        Pobiera rozmiar pliku w megabajtach

        Args:
            file_path (str): Ścieżka do pliku

        Returns:
            float: Rozmiar pliku w MB
        """
        try:
            if os.path.exists(file_path):
                size_bytes = os.path.getsize(file_path)
                size_mb = size_bytes / (1024 * 1024)  # Konwersja na MB
                return round(size_mb, 2)
            else:
                logger.warning(f"Plik nie istnieje: {file_path}")
                return 0.0
        except Exception as e:
            logger.error(f"Błąd podczas pobierania rozmiaru pliku {file_path}: {e}")
            return 0.0

    def create_thumbnail_for_asset(
        self, asset_path: str, image_path: str, async_mode: bool = False
    ) -> str:
        """
        Tworzy miniaturę dla assetu

        Args:
            asset_path (str): Ścieżka do pliku .asset
            image_path (str): Ścieżka do pliku obrazu
            async_mode (bool): Czy używać trybu asynchronicznego

        Returns:
            str: Ścieżka do utworzonej miniatury lub None przy błędzie
        """
        try:
            # Pobierz nazwę assetu z ścieżki
            asset_name = os.path.splitext(os.path.basename(asset_path))[0]

            # Utwórz miniaturę - process_thumbnail zwraca tuple (filename, thumbnail_size)
            result = process_thumbnail(image_path, async_mode)
            if isinstance(result, tuple) and len(result) >= 1:
                thumbnail_path = result[0]  # Pierwszy element to ścieżka do miniatury
            else:
                thumbnail_path = None

            if thumbnail_path:
                logger.debug(f"Utworzono miniaturę: {thumbnail_path}")

                # Zaktualizuj plik .asset z ścieżką do miniatury
                asset_data = load_from_file(asset_path)
                if asset_data:
                    asset_data["thumbnail"] = thumbnail_path
                    save_to_file(asset_data, asset_path)
                    logger.debug(
                        f"Zaktualizowano plik .asset z miniaturą: {asset_path}"
                    )

                return thumbnail_path
            else:
                logger.warning(f"Nie udało się utworzyć miniatury dla: {asset_name}")
                return None

        except Exception as e:
            logger.error(f"Błąd podczas tworzenia miniatury dla {asset_path}: {e}")
            return None

    def _create_unpair_files_json(
        self,
        folder_path: str,
        archive_by_name: dict,
        image_by_name: dict,
        common_names: set,
    ) -> None:
        """
        Tworzy plik JSON z nieparowanymi plikami

        Args:
            folder_path (str): Ścieżka do folderu
            archive_by_name (dict): Słownik plików archiwum według nazw
            image_by_name (dict): Słownik plików obrazów według nazw
            common_names (set): Zbiór wspólnych nazw
        """
        try:
            # Znajdź nieparowane pliki
            unpaired_archives = set(archive_by_name.keys()) - common_names
            unpaired_images = set(image_by_name.keys()) - common_names

            unpaired_data = {
                "unpaired_archives": list(unpaired_archives),
                "unpaired_images": list(unpaired_images),
                "total_unpaired_archives": len(unpaired_archives),
                "total_unpaired_images": len(unpaired_images),
            }

            # Zapisz do pliku JSON
            unpaired_file_path = os.path.join(folder_path, "unpair_files.json")
            save_to_file(unpaired_data, unpaired_file_path)

            logger.info(
                f"Utworzono plik unpair_files.json: "
                f"{len(unpaired_archives)} nieparowanych archiwów, "
                f"{len(unpaired_images)} nieparowanych obrazów"
            )

        except Exception as e:
            logger.error(f"Błąd podczas tworzenia pliku unpair_files.json: {e}")

    def find_and_create_assets(
        self, folder_path: str, progress_callback=None, use_async_thumbnails=False
    ) -> list:
        """
        Wyszukuje i tworzy assety w określonym folderze

        Args:
            folder_path (str): Ścieżka do folderu do skanowania
            progress_callback (callable): Opcjonalna funkcja callback do raportowania postępu
            use_async_thumbnails (bool): Czy używać asynchronicznego generowania miniatur

        Returns:
            list: Lista słowników reprezentujących znalezione assety
        """
        if not folder_path or not os.path.exists(folder_path):
            logger.error(f"Nieprawidłowa ścieżka folderu: {folder_path}")
            return []

        try:
            logger.info(f"Rozpoczęto skanowanie folderu: {folder_path}")

            # Skanuj folder w poszukiwaniu plików
            archive_by_name, image_by_name = self._scan_folder_for_files(folder_path)

            # Znajdź wspólne nazwy (case-insensitive)
            common_names = set(archive_by_name.keys()) & set(image_by_name.keys())

            if not common_names:
                logger.warning(f"Nie znaleziono sparowanych plików w: {folder_path}")
                # Utwórz plik z nieparowanymi plikami
                self._create_unpair_files_json(
                    folder_path, archive_by_name, image_by_name, common_names
                )
                return []

            # Utwórz assety dla każdej sparowanej nazwy
            created_assets = []
            total_assets = len(common_names)

            for i, name in enumerate(common_names):
                if progress_callback:
                    progress_callback(i + 1, total_assets, f"Tworzenie assetu: {name}")

                archive_path = archive_by_name[name]
                image_path = image_by_name[name]

                # Utwórz asset
                asset_data = self._create_single_asset(
                    name, archive_path, image_path, folder_path
                )

                if asset_data:
                    created_assets.append(asset_data)
                    logger.debug(f"Utworzono asset: {name}")

                    # Utwórz miniaturę
                    asset_file_path = os.path.join(folder_path, f"{name}.asset")
                    self.create_thumbnail_for_asset(
                        asset_file_path, image_path, use_async_thumbnails
                    )

            # Utwórz plik z nieparowanymi plikami
            self._create_unpair_files_json(
                folder_path, archive_by_name, image_by_name, common_names
            )

            logger.info(
                f"Zakończono skanowanie. Utworzono {len(created_assets)} assetów."
            )
            return created_assets

        except Exception as e:
            logger.error(f"Błąd podczas skanowania folderu {folder_path}: {e}")
            return []

    def load_existing_assets(self, folder_path: str) -> list:
        """
        Ładuje istniejące assety z określonego folderu

        Args:
            folder_path (str): Ścieżka do folderu

        Returns:
            list: Lista słowników reprezentujących załadowane assety
        """
        if not folder_path or not os.path.exists(folder_path):
            logger.error(f"Nieprawidłowa ścieżka folderu: {folder_path}")
            return []

        try:
            logger.info(f"Ładowanie istniejących assetów z: {folder_path}")

            assets = []
            for entry in os.listdir(folder_path):
                if entry.endswith(".asset"):
                    asset_file_path = os.path.join(folder_path, entry)
                    try:
                        asset_data = load_from_file(asset_file_path)
                        if asset_data and isinstance(asset_data, dict):
                            assets.append(asset_data)
                            logger.debug(f"Załadowano asset: {entry}")
                        else:
                            logger.warning(f"Nieprawidłowe dane w pliku: {entry}")
                    except Exception as e:
                        logger.error(f"Błąd podczas ładowania assetu {entry}: {e}")

            logger.info(f"Załadowano {len(assets)} assetów z {folder_path}")
            return assets

        except Exception as e:
            logger.error(f"Błąd podczas ładowania assetów z {folder_path}: {e}")
            return []


# Zachowanie kompatybilności wstecznej - funkcje globalne delegują do instancji
_asset_repository = AssetRepository()


def _get_files_by_extensions(folder_path, extensions):
    """Zachowanie kompatybilności wstecznej."""
    return _asset_repository._get_files_by_extensions(folder_path, extensions)


def _scan_folder_for_files(folder_path):
    """Zachowanie kompatybilności wstecznej."""
    return _asset_repository._scan_folder_for_files(folder_path)


def _check_texture_folders_presence(folder_path):
    """Zachowanie kompatybilności wstecznej."""
    return _asset_repository._check_texture_folders_presence(folder_path)


def _scan_for_special_folders(folder_path):
    """Zachowanie kompatybilności wstecznej."""
    return _asset_repository._scan_for_special_folders(folder_path)


def _create_single_asset(name, archive_path, image_path, folder_path):
    """Zachowanie kompatybilności wstecznej."""
    return _asset_repository._create_single_asset(
        name, archive_path, image_path, folder_path
    )


def get_file_size_mb(file_path):
    """Zachowanie kompatybilności wstecznej."""
    return _asset_repository._get_file_size_mb(file_path)


def create_thumbnail_for_asset(asset_path, image_path, async_mode=False):
    """Zachowanie kompatybilności wstecznej."""
    return _asset_repository.create_thumbnail_for_asset(
        asset_path, image_path, async_mode
    )


def create_unpair_files_json(folder_path, archive_by_name, image_by_name, common_names):
    """Zachowanie kompatybilności wstecznej."""
    return _asset_repository._create_unpair_files_json(
        folder_path, archive_by_name, image_by_name, common_names
    )


def find_and_create_assets(
    folder_path, progress_callback=None, use_async_thumbnails=False
):
    """Zachowanie kompatybilności wstecznej."""
    return _asset_repository.find_and_create_assets(
        folder_path, progress_callback, use_async_thumbnails
    )


def load_existing_assets(folder_path):
    """Zachowanie kompatybilności wstecznej."""
    return _asset_repository.load_existing_assets(folder_path)


# Przykład użycia
if __name__ == "__main__":
    # Przykład wywołania funkcji
    # find_and_create_assets("ścieżka/do/folderu")
    pass
