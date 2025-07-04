import logging
import os

from core.json_utils import load_from_file, save_to_file
from core.performance_monitor import measure_operation
from core.thumbnail import generate_thumbnail
from core.utilities import get_file_size_mb

# Dodanie loggera dla modułu
logger = logging.getLogger(__name__)

# Konfiguracja rozszerzeń plików obsługiwanych przez aplikację
FILE_EXTENSIONS = {
    "archives": ["zip", "rar", "sbsar", "7z"],
    "images": ["png", "jpg", "jpeg", "webp"],
}


class AssetRepository:
    """
    Implementacja repozytorium assetów.

    Enkapsuluje logikę skanowania, tworzenia i ładowania assetów.
    Implementuje interfejs IAssetRepository.
    """

    def __init__(self):
        """Inicjalizuje repozytorium assetów."""
        pass

    def _handle_error(self, operation: str, error: Exception, file_path: str = None):
        """DODAJ bazową metodę dla obsługi błędów"""
        error_msg = f"Błąd podczas {operation}"
        if file_path:
            error_msg += f" dla {file_path}"
        error_msg += f": {error}"
        logger.error(error_msg)
        return None

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

    @staticmethod
    def _check_texture_folders_presence(folder_path: str) -> bool:
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
        # Walidacja ścieżki folderu
        if not AssetRepository._validate_folder_path_static(folder_path):
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

    @staticmethod
    def _validate_folder_path_static(folder_path: str) -> bool:
        """Statyczna walidacja ścieżki folderu"""
        return bool(folder_path and os.path.exists(folder_path))

    def _scan_for_named_folders(
        self, folder_path: str, folder_names: list[str]
    ) -> list:
        """Skanuje folder w poszukiwaniu podfolderów o zadanych nazwach."""
        found_folders = []
        for folder_name in folder_names:
            full_path = os.path.join(folder_path, folder_name)
            if os.path.isdir(full_path):
                found_folders.append(
                    {
                        "type": "special_folder",
                        "name": folder_name,
                        "folder_path": full_path,
                    }
                )
                logger.debug(f"Found special folder: {full_path}")
        return found_folders

    def _scan_for_special_folders(self, folder_path: str) -> list:
        """Skanuje folder w poszukiwaniu specjalnych folderów (tex, textures, maps)."""
        special_folder_names = ["tex", "textures", "maps"]
        return self._scan_for_named_folders(folder_path, special_folder_names)

    def _create_single_asset(
        self, name: str, archive_path: str, image_path: str, folder_path: str
    ) -> dict | None:
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
        # Walidacja ścieżki folderu na początku
        if not AssetRepository._validate_folder_path_static(folder_path):
            logger.error(f"Nieprawidłowa ścieżka folderu: {folder_path}")
            return None
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
        """Pobiera rozmiar pliku w megabajtach"""
        return get_file_size_mb(file_path)

    def create_thumbnail_for_asset(
        self, asset_path: str, image_path: str
    ) -> str | None:
        """
        Tworzy miniaturę dla assetu

        Args:
            asset_path (str): Ścieżka do pliku .asset
            image_path (str): Ścieżka do pliku obrazu

        Returns:
            str: Ścieżka do utworzonej miniatury lub None przy błędzie
        """
        # Walidacja ścieżki pliku obrazu na początku
        if not image_path or not os.path.exists(image_path):
            logger.error(f"Plik obrazu nie istnieje: {image_path}")
            return None
        try:
            asset_name = os.path.splitext(os.path.basename(asset_path))[0]
            logger.debug(
                f"Creating thumbnail for asset: {asset_name}, image: {image_path}"
            )

            # Generuj miniaturę
            result = generate_thumbnail(image_path)
            logger.debug(f"generate_thumbnail result: {result}")

            if isinstance(result, tuple) and len(result) >= 1:
                thumbnail_path = result[0]  # Pierwszy element to ścieżka do miniatury
                logger.debug(f"Extracted thumbnail path: {thumbnail_path}")
            else:
                thumbnail_path = None
                logger.warning(f"Invalid result from generate_thumbnail: {result}")

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
            return self._handle_error("tworzenia miniatury", e, asset_path)

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
            # Znajdź nieparowane pliki (nazwy bez rozszerzeń)
            unpaired_archive_names = set(archive_by_name.keys()) - common_names
            unpaired_image_names = set(image_by_name.keys()) - common_names

            # Pobierz pełne nazwy plików z rozszerzeniami
            unpaired_archives = [
                os.path.basename(archive_by_name[name])
                for name in unpaired_archive_names
            ]
            unpaired_images = [
                os.path.basename(image_by_name[name]) for name in unpaired_image_names
            ]

            unpaired_data = {
                "unpaired_archives": unpaired_archives,
                "unpaired_images": unpaired_images,
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
            self._handle_error("tworzenia pliku unpair_files.json", e)

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
        with measure_operation(
            "scanner.find_and_create_assets",
            {"folder_path": folder_path, "use_async_thumbnails": use_async_thumbnails},
        ):
            # Walidacja ścieżki folderu
            if not AssetRepository._validate_folder_path_static(folder_path):
                return []

            try:
                logger.info(f"Rozpoczęto skanowanie folderu: {folder_path}")

                # Skanuj i grupuj pliki
                file_groups = self._scan_and_group_files(folder_path)

                # Skanuj specjalne foldery
                special_folders = self._scan_for_special_folders(folder_path)

                # Utwórz assety z grup plików
                created_assets = self._create_assets_from_groups(
                    file_groups, folder_path, progress_callback
                )

                # Utwórz plik z nieparowanymi plikami
                self._create_unpair_files_json(folder_path, *file_groups)

                # Połącz specjalne foldery z utworzonymi assetami
                all_assets = special_folders + created_assets

                logger.info(
                    f"Zakończono skanowanie. Utworzono {len(all_assets)} assetów "
                    f"(w tym {len(special_folders)} specjalnych folderów)."
                )
                return all_assets

            except Exception as e:
                logger.error(f"Błąd podczas skanowania folderu {folder_path}: {e}")
                return []

    def _scan_and_group_files(self, folder_path: str) -> tuple:
        """Skanuje folder i grupuje pliki według nazw"""
        # Skanuj folder w poszukiwaniu plików
        archive_by_name, image_by_name = self._scan_folder_for_files(folder_path)

        # Znajdź wspólne nazwy (case-insensitive)
        common_names = set(archive_by_name.keys()) & set(image_by_name.keys())

        if not common_names:
            logger.warning(f"Nie znaleziono sparowanych plików w: {folder_path}")

        return archive_by_name, image_by_name, common_names

    def _create_assets_from_groups(
        self, file_groups: tuple, folder_path: str, progress_callback=None
    ) -> list:
        """Tworzy assety z pogrupowanych plików"""
        archive_by_name, image_by_name, common_names = file_groups

        if not common_names:
            return []

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
                self.create_thumbnail_for_asset(asset_file_path, image_path)

        return created_assets

    def load_existing_assets(self, folder_path: str) -> list:
        """
        Ładuje istniejące assety z określonego folderu

        Args:
            folder_path (str): Ścieżka do folderu

        Returns:
            list: Lista słowników reprezentujących załadowane assety
        """
        # Walidacja ścieżki folderu na początku
        if not AssetRepository._validate_folder_path_static(folder_path):
            logger.error(f"Nieprawidłowa ścieżka folderu: {folder_path}")
            return []
        with measure_operation(
            "scanner.load_existing_assets", {"folder_path": folder_path}
        ):
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

                # Dodaj specjalne foldery (textures, tex, maps) NA POCZĄTKU
                special_folders = self._scan_for_special_folders(folder_path)
                assets = special_folders + assets  # Dodaj na początku
                logger.debug(
                    f"Dodano {len(special_folders)} specjalnych folderów na początku"
                )

                logger.info(f"Załadowano {len(assets)} assetów z {folder_path}")
                return assets

            except Exception as e:
                logger.error(f"Błąd podczas ładowania assetów z {folder_path}: {e}")
                return []
