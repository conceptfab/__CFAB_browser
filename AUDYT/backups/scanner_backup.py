import logging
import os

from core.json_utils import load_from_file, save_to_file
from core.performance_monitor import measure_operation
from core.thumbnail import generate_thumbnail
from core.utilities import get_file_size_mb

# Adding logger for the module
logger = logging.getLogger(__name__)

# Configuration of file extensions supported by the application
FILE_EXTENSIONS = {
    "archives": ["zip", "rar", "sbsar", "7z"],
    "images": ["png", "jpg", "jpeg", "webp"],
}


class AssetRepository:
    """
    Implementation of the asset repository.

    Encapsulates logic for scanning, creating, and loading assets.
    Implements the IAssetRepository interface.
    """

    def __init__(self):
        """Initializes the asset repository."""
        pass

    @staticmethod
    def _validate_folder_path_static(folder_path: str) -> bool:
        """Static validation of folder path - centralized method"""
        return bool(folder_path and os.path.exists(folder_path) and os.path.isdir(folder_path))

    def _handle_error(self, operation: str, error: Exception, file_path: str = None):
        """Enhanced error handling with more detailed logging"""
        error_msg = f"Error during {operation}"
        if file_path:
            error_msg += f" for {file_path}"
        error_msg += f": {error}"
        
        # Enhanced error logging based on error type
        if isinstance(error, (FileNotFoundError, PermissionError)):
            logger.error(error_msg)
        elif isinstance(error, (ValueError, TypeError)):
            logger.error(f"Data validation error: {error_msg}")
        else:
            logger.error(f"Unexpected error: {error_msg}")
        
        return None

    def _get_files_by_extensions(self, folder_path: str, extensions: list) -> list:
        """
        Helper function for finding files with specific extensions

        Args:
            folder_path (str): Path to the folder
            extensions (list): List of extensions (without dot)

        Returns:
            list: List of found file paths
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
        Scans the folder for archive and image files

        Args:
            folder_path (str): Path to the folder

        Returns:
            tuple: (archive_by_name, image_by_name) - dictionaries of files by name
        """
        # Find all archive and image files
        archive_files = self._get_files_by_extensions(
            folder_path, FILE_EXTENSIONS["archives"]
        )
        image_files = self._get_files_by_extensions(
            folder_path, FILE_EXTENSIONS["images"]
        )

        # Dictionary to store files by name (without extension) - case-insensitive
        archive_by_name = {}
        image_by_name = {}

        # Group archive files by name (case-insensitive)
        for archive_file in archive_files:
            name_without_ext = os.path.splitext(os.path.basename(archive_file))[0]
            name_lower = (
                name_without_ext.lower()
            )  # Convert to lowercase for comparison
            archive_by_name[name_lower] = archive_file

        # Group image files by name (case-insensitive)
        for image_file in image_files:
            name_without_ext = os.path.splitext(os.path.basename(image_file))[0]
            name_lower = (
                name_without_ext.lower()
            )  # Convert to lowercase for comparison
            image_by_name[name_lower] = image_file

        logger.debug(
            f"Found {len(archive_files)} archive files and "
            f"{len(image_files)} image files"
        )
        return archive_by_name, image_by_name

    @staticmethod
    def _check_texture_folders_presence(folder_path: str) -> bool:
        """
        Checks for the presence of texture folders in the working folder

        Args:
            folder_path (str): Path to the working folder

        Returns:
            bool: True if NO texture folders found (textures are in archive),
                  False if texture folders found (textures are external)
        """
        if not folder_path or not isinstance(folder_path, str):
            logger.warning(f"Invalid folder_path parameter: {folder_path}")
            return True
        # Folder path validation
        if not AssetRepository._validate_folder_path_static(folder_path):
            logger.warning(f"Folder does not exist: {folder_path}")
            return True

        # List of folder names to check
        texture_folder_names = ["tex", "textures", "maps"]

        try:
            # Check each texture folder
            for folder_name in texture_folder_names:
                texture_folder_path = os.path.join(folder_path, folder_name)
                if os.path.isdir(texture_folder_path):
                    logger.debug(f"Found texture folder: {folder_name}")
                    return False  # Found texture folder - textures are external

            logger.debug("No texture folders found - textures are in archive")
            return True  # No texture folders found - textures are in archive

        except PermissionError:
            logger.error(f"Permission denied accessing folder: {folder_path}")
            return True
        except OSError as e:
            logger.error(f"OS error checking texture folders in {folder_path}: {e}")
            return True
        except FileNotFoundError:
            logger.error(f"Folder not found: {folder_path}")
            return True
        except Exception as e:
            logger.error(f"Unexpected error checking texture folders in {folder_path}: {e}")
            return True

    def _scan_for_named_folders(
        self, folder_path: str, folder_names: list[str]
    ) -> list:
        """Scans the folder for subfolders with given names."""
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
        """Scans the folder for special folders (tex, textures, maps)."""
        special_folder_names = ["tex", "textures", "maps"]
        return self._scan_for_named_folders(folder_path, special_folder_names)

    def _create_single_asset(
        self, name: str, archive_path: str, image_path: str, folder_path: str
    ) -> dict | None:
        """
        Creates a single .asset file

        Args:
            name (str): File name (without extension)
            archive_path (str): Path to archive file
            image_path (str): Path to image file
            folder_path (str): Path to target folder

        Returns:
            dict|None: Asset data dictionary or None on error
        """
        # Folder path validation at the beginning
        if not AssetRepository._validate_folder_path_static(folder_path):
            logger.error(f"Invalid folder path: {folder_path}")
            return None
        asset_file_path = os.path.join(folder_path, f"{name}.asset")

        try:
            # Check if .asset file already exists
            existing_asset_data = None
            if os.path.exists(asset_file_path):
                existing_asset_data = load_from_file(asset_file_path)
                logger.debug(f"Found existing .asset file: {name}.asset")

            # Get archive file size in MB
            archive_size_mb = self._get_file_size_mb(archive_path)

            # Check for texture folder presence
            textures_in_archive = self._check_texture_folders_presence(folder_path)

            # Create new asset data
            asset_data = {
                "type": "asset",  # Added type
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

            # If previous file exists, preserve important user data
            if existing_asset_data:
                # Preserve stars, color and other user data
                if (
                    "stars" in existing_asset_data
                    and existing_asset_data["stars"] is not None
                ):
                    asset_data["stars"] = existing_asset_data["stars"]
                    logger.debug(
                        f"Preserved stars: {existing_asset_data['stars']} for {name}"
                    )

                if (
                    "color" in existing_asset_data
                    and existing_asset_data["color"] is not None
                ):
                    asset_data["color"] = existing_asset_data["color"]
                    logger.debug(
                        f"Preserved color: {existing_asset_data['color']} for {name}"
                    )

                # Preserve thumbnail if exists
                if (
                    "thumbnail" in existing_asset_data
                    and existing_asset_data["thumbnail"] is not None
                ):
                    asset_data["thumbnail"] = existing_asset_data["thumbnail"]
                    logger.debug(
                        f"Preserved thumbnail: {existing_asset_data['thumbnail']} for {name}"
                    )

                # Preserve meta data
                if "meta" in existing_asset_data:
                    asset_data["meta"] = existing_asset_data["meta"]

            # Save .asset file
            save_to_file(asset_data, asset_file_path)
            logger.debug(f"Created .asset file: {name}.asset")

            return asset_data

        except FileNotFoundError as e:
            logger.error(f"File not found while creating asset {name}: {e}")
            return None
        except PermissionError as e:
            logger.error(f"Permission denied while creating asset {name}: {e}")
            return None
        except OSError as e:
            logger.error(f"System error while creating asset {name}: {e}")
            return None
        except (ValueError, TypeError) as e:
            logger.error(f"Data error while creating asset {name}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error while creating asset {name}: {e}")
            return None

    def _get_file_size_mb(self, file_path: str) -> float:
        """Gets file size in megabytes"""
        return get_file_size_mb(file_path)

    def create_thumbnail_for_asset(
        self, asset_path: str, image_path: str
    ) -> str | None:
        """
        Creates a thumbnail for an asset

        Args:
            asset_path (str): Path to the .asset file
            image_path (str): Path to the image file

        Returns:
            str: Path to the created thumbnail or None on error
        """
        # Image file path validation at the beginning
        if not image_path or not os.path.exists(image_path):
            logger.error(f"Image file does not exist: {image_path}")
            return None
        try:
            asset_name = os.path.splitext(os.path.basename(asset_path))[0]
            logger.debug(
                f"Creating thumbnail for asset: {asset_name}, image: {image_path}"
            )

            # Generate thumbnail
            result = generate_thumbnail(image_path)
            logger.debug(f"generate_thumbnail result: {result}")

            if isinstance(result, tuple) and len(result) >= 1:
                thumbnail_path = result[0]  # First element is thumbnail path
                logger.debug(f"Extracted thumbnail path: {thumbnail_path}")
            else:
                thumbnail_path = None
                logger.warning(f"Invalid result from generate_thumbnail: {result}")

            if thumbnail_path:
                logger.debug(f"Created thumbnail: {thumbnail_path}")

                # Update .asset file with thumbnail path
                asset_data = load_from_file(asset_path)
                if asset_data:
                    asset_data["thumbnail"] = thumbnail_path
                    save_to_file(asset_data, asset_path)
                    logger.debug(
                        f"Updated .asset file with thumbnail: {asset_path}"
                    )

                return thumbnail_path
            else:
                logger.warning(f"Failed to create thumbnail for: {asset_name}")
                return None

        except Exception as e:
            return self._handle_error("thumbnail creation", e, asset_path)

    def _create_unpair_files_json(
        self,
        folder_path: str,
        archive_by_name: dict,
        image_by_name: dict,
        common_names: set,
    ) -> None:
        """
        Creates a JSON file with unpaired files

        Args:
            folder_path (str): Path to the folder
            archive_by_name (dict): Dictionary of archive files by name
            image_by_name (dict): Dictionary of image files by name
            common_names (set): Set of common names
        """
        try:
            # Find unpaired files (names without extensions)
            unpaired_archive_names = set(archive_by_name.keys()) - common_names
            unpaired_image_names = set(image_by_name.keys()) - common_names

            # Get full filenames with extensions
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

            # Save to JSON file
            unpaired_file_path = os.path.join(folder_path, "unpair_files.json")
            save_to_file(unpaired_data, unpaired_file_path)

            logger.info(
                f"Created unpair_files.json: "
                f"{len(unpaired_archives)} unpaired archives, "
                f"{len(unpaired_images)} unpaired images"
            )

        except PermissionError as e:
            self._handle_error("creating unpair_files.json - permission denied", e)
        except OSError as e:
            self._handle_error("creating unpair_files.json - system error", e)
        except Exception as e:
            self._handle_error("creating unpair_files.json - unexpected error", e)

    def find_and_create_assets(
        self, folder_path: str, progress_callback=None, use_async_thumbnails=False
    ) -> list:
        """
        Finds and creates assets in the specified folder

        Args:
            folder_path (str): Path to the folder to scan
            progress_callback (callable): Optional callback function to report progress
            use_async_thumbnails (bool): Whether to use asynchronous thumbnail generation

        Returns:
            list: List of dictionaries representing found assets
        """
        with measure_operation(
            "scanner.find_and_create_assets",
            {"folder_path": folder_path, "use_async_thumbnails": use_async_thumbnails},
        ):
            # Folder path validation
            if not AssetRepository._validate_folder_path_static(folder_path):
                return []

            try:
                logger.info(f"Starting folder scan: {folder_path}")

                # Scan and group files
                file_groups = self._scan_and_group_files(folder_path)

                # Scan special folders
                special_folders = self._scan_for_special_folders(folder_path)

                # Create assets from file groups
                created_assets = self._create_assets_from_groups(
                    file_groups, folder_path, progress_callback
                )

                # Create file with unpaired files
                self._create_unpair_files_json(folder_path, *file_groups)

                # Combine special folders with created assets
                all_assets = special_folders + created_assets

                logger.info(
                    f"Scan completed. Created {len(all_assets)} assets "
                    f"(including {len(special_folders)} special folders)."
                )
                return all_assets

            except PermissionError as e:
                logger.error(f"Permission denied while scanning folder {folder_path}: {e}")
                return []
            except OSError as e:
                logger.error(f"System error while scanning folder {folder_path}: {e}")
                return []
            except Exception as e:
                logger.error(f"Unexpected error while scanning folder {folder_path}: {e}")
                return []

    def _scan_and_group_files(self, folder_path: str) -> tuple:
        """Scans the folder and groups files by name"""
        # Scan folder for files
        archive_by_name, image_by_name = self._scan_folder_for_files(folder_path)

        # Find common names (case-insensitive)
        common_names = set(archive_by_name.keys()) & set(image_by_name.keys())

        if not common_names:
            logger.warning(f"No paired files found in: {folder_path}")

        return archive_by_name, image_by_name, common_names

    def _create_assets_from_groups(
        self, file_groups: tuple, folder_path: str, progress_callback=None
    ) -> list:
        """Creates assets from grouped files"""
        archive_by_name, image_by_name, common_names = file_groups

        if not common_names:
            return []

        created_assets = []
        total_assets = len(common_names)

        for i, name in enumerate(common_names):
            if progress_callback:
                progress_callback(i + 1, total_assets, f"Creating asset: {name}")

            archive_path = archive_by_name[name]
            image_path = image_by_name[name]

            # Create asset
            asset_data = self._create_single_asset(
                name, archive_path, image_path, folder_path
            )

            if asset_data:
                created_assets.append(asset_data)
                logger.debug(f"Created asset: {name}")

                # Create thumbnail
                asset_file_path = os.path.join(folder_path, f"{name}.asset")
                self.create_thumbnail_for_asset(asset_file_path, image_path)

        return created_assets

    # ===============================================
    # NOWE METODY POMOCNICZE - REFAKTORYZACJA load_existing_assets
    # ===============================================
    
    def _validate_asset_data(self, asset_data) -> bool:
        """Validate loaded asset data
        
        Args:
            asset_data: Data loaded from .asset file
            
        Returns:
            bool: True if data is valid, False otherwise
        """
        return asset_data and isinstance(asset_data, dict)
    
    def _handle_asset_loading_errors(self, error: Exception, file_name: str) -> None:
        """Handle different types of asset loading errors with appropriate logging
        
        Args:
            error: Exception that occurred
            file_name: Name of the file being loaded
        """
        if isinstance(error, (FileNotFoundError, PermissionError)):
            logger.error(f"Error accessing asset file {file_name}: {error}")
        elif isinstance(error, (ValueError, TypeError)):
            logger.error(f"Data error in asset file {file_name}: {error}")
        else:
            logger.error(f"Unexpected error while loading asset {file_name}: {error}")
    
    def _load_single_asset_file(self, asset_file_path: str) -> dict | None:
        """Load single .asset file with error handling
        
        Args:
            asset_file_path: Full path to the .asset file
            
        Returns:
            dict: Loaded asset data or None if loading failed
        """
        try:
            asset_data = load_from_file(asset_file_path)
            
            if self._validate_asset_data(asset_data):
                entry = os.path.basename(asset_file_path)
                logger.debug(f"Loaded asset: {entry}")
                return asset_data
            else:
                entry = os.path.basename(asset_file_path)
                logger.warning(f"Invalid data in file: {entry}")
                return None
                
        except Exception as e:
            entry = os.path.basename(asset_file_path)
            self._handle_asset_loading_errors(e, entry)
            return None
    
    def _load_asset_files(self, folder_path: str) -> list:
        """Load all .asset files from folder
        
        Args:
            folder_path: Path to folder containing .asset files
            
        Returns:
            list: List of successfully loaded asset data dictionaries
        """
        assets = []
        
        for entry in os.listdir(folder_path):
            if entry.endswith(".asset"):
                asset_file_path = os.path.join(folder_path, entry)
                asset_data = self._load_single_asset_file(asset_file_path)
                
                if asset_data:
                    assets.append(asset_data)
        
        return assets
    
    def _combine_with_special_folders(self, assets: list, folder_path: str) -> list:
        """Add special folders at the beginning of assets list
        
        Args:
            assets: List of loaded asset data
            folder_path: Path to scan for special folders
            
        Returns:
            list: Combined list with special folders at the beginning
        """
        special_folders = self._scan_for_special_folders(folder_path)
        combined_assets = special_folders + assets
        
        logger.debug(
            f"Added {len(special_folders)} special folders at the beginning"
        )
        
        return combined_assets

    def load_existing_assets(self, folder_path: str) -> list:
        """
        Loads existing assets from the specified folder

        Args:
            folder_path (str): Path to the folder

        Returns:
            list: List of dictionaries representing loaded assets
        """
        # Folder path validation at the beginning
        if not AssetRepository._validate_folder_path_static(folder_path):
            logger.error(f"Invalid folder path: {folder_path}")
            return []
        with measure_operation(
            "scanner.load_existing_assets", {"folder_path": folder_path}
        ):
            try:
                logger.info(f"Loading existing assets from: {folder_path}")

                assets = self._load_asset_files(folder_path)

                # Add special folders (textures, tex, maps) AT THE BEGINNING
                assets = self._combine_with_special_folders(assets, folder_path)

                logger.info(f"Loaded {len(assets)} assets from {folder_path}")
                return assets

            except PermissionError as e:
                logger.error(f"Permission denied while loading assets from {folder_path}: {e}")
                return []
            except OSError as e:
                logger.error(f"System error while loading assets from {folder_path}: {e}")
                return []
            except Exception as e:
                logger.error(f"Unexpected error while loading assets from {folder_path}: {e}")
                return []
