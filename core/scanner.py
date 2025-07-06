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

    def _handle_error(self, operation: str, error: Exception, file_path: str | None = None):
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

    def _has_valid_extension(self, file_path: str, extensions_set: set) -> bool:
        """
        Checks if file has a valid extension.
        
        Args:
            file_path (str): Path to the file
            extensions_set (set): Set of valid extensions (lowercase)
            
        Returns:
            bool: True if file has valid extension, False otherwise
        """
        _, ext = os.path.splitext(file_path)
        return bool(ext and ext[1:].lower() in extensions_set)

    def _get_files_by_extensions(self, folder_path: str, extensions: list) -> list:
        """
        Helper function for finding files with specific extensions.
        
        This method uses optimized list comprehension and helper functions
        for better performance and readability.

        Args:
            folder_path (str): Path to the folder
            extensions (list): List of extensions (without dot)

        Returns:
            list: List of found file paths
        """
        try:
            # Pre-convert extensions to lowercase set for O(1) lookup
            ext_set = set(ext.lower() for ext in extensions)
            
            # Use list comprehension with helper function for cleaner code
            return [
                os.path.join(folder_path, entry)
                for entry in os.listdir(folder_path)
                if (os.path.isfile(os.path.join(folder_path, entry)) and
                    self._has_valid_extension(entry, ext_set))
            ]
        except (OSError, PermissionError) as e:
            logger.error(f"Error scanning folder {folder_path}: {e}")
            return []

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
    def _validate_texture_check_inputs(folder_path: str) -> tuple[bool, str]:
        """
        Validates inputs for texture folder checking.
        
        Args:
            folder_path (str): Path to the working folder
            
        Returns:
            tuple[bool, str]: (is_valid, error_message)
        """
        if not folder_path or not isinstance(folder_path, str):
            return False, f"Invalid folder_path parameter: {folder_path}"
            
        if not AssetRepository._validate_folder_path_static(folder_path):
            return False, f"Folder does not exist: {folder_path}"
            
        return True, ""

    @staticmethod
    def _scan_texture_folders(folder_path: str) -> bool:
        """
        Scans for texture folders in the specified path.
        
        Args:
            folder_path (str): Path to scan
            
        Returns:
            bool: True if NO texture folders found, False if found
        """
        texture_folder_names = ["tex", "textures", "maps"]
        
        for folder_name in texture_folder_names:
            texture_folder_path = os.path.join(folder_path, folder_name)
            if os.path.isdir(texture_folder_path):
                logger.debug(f"Found texture folder: {folder_name}")
                return False  # Found texture folder - textures are external
        
        logger.debug("No texture folders found - textures are in archive")
        return True  # No texture folders found - textures are in archive

    @staticmethod
    def _check_texture_folders_presence(folder_path: str) -> bool:
        """
        Checks for the presence of texture folders in the working folder.
        
        This method uses specialized helper functions for better maintainability
        and follows the Single Responsibility Principle.

        Args:
            folder_path (str): Path to the working folder

        Returns:
            bool: True if NO texture folders found (textures are in archive),
                  False if texture folders found (textures are external)
        """
        # Step 1: Validate inputs
        is_valid, error_msg = AssetRepository._validate_texture_check_inputs(folder_path)
        if not is_valid:
            logger.warning(error_msg)
            return True  # Default to "textures in archive" on error
        
        # Step 2: Scan for texture folders with comprehensive error handling
        try:
            return AssetRepository._scan_texture_folders(folder_path)
        except (PermissionError, OSError, FileNotFoundError) as e:
            logger.error(f"Error checking texture folders in {folder_path}: {e}")
            return True  # Default to "textures in archive" on error
        except Exception as e:
            logger.error(f"Unexpected error checking texture folders in {folder_path}: {e}")
            return True  # Default to "textures in archive" on error

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

    def _validate_asset_creation_inputs(self, name: str, archive_path: str, image_path: str, folder_path: str) -> tuple[bool, str]:
        """
        Validates inputs for asset creation.
        
        Args:
            name (str): Asset name
            archive_path (str): Path to archive file
            image_path (str): Path to image file  
            folder_path (str): Target folder path
            
        Returns:
            tuple[bool, str]: (is_valid, error_message)
        """
        if not name:
            return False, "Asset name cannot be empty"
        
        if not AssetRepository._validate_folder_path_static(folder_path):
            return False, f"Invalid folder path: {folder_path}"
            
        if not archive_path or not os.path.exists(archive_path):
            return False, f"Archive file does not exist: {archive_path}"
            
        if not image_path or not os.path.exists(image_path):
            return False, f"Image file does not exist: {image_path}"
            
        return True, ""

    def _load_existing_asset_data(self, asset_file_path: str) -> dict | None:
        """
        Loads existing asset data if .asset file exists.
        
        Args:
            asset_file_path (str): Path to .asset file
            
        Returns:
            dict|None: Existing asset data or None
        """
        if os.path.exists(asset_file_path):
            try:
                existing_data = load_from_file(asset_file_path)
                logger.debug(f"Found existing .asset file: {os.path.basename(asset_file_path)}")
                return existing_data
            except Exception as e:
                logger.warning(f"Error loading existing asset data: {e}")
                return None
        return None

    def _create_base_asset_data(self, name: str, archive_path: str, image_path: str, folder_path: str) -> dict:
        """
        Creates base asset data structure.
        
        Args:
            name (str): Asset name
            archive_path (str): Path to archive file
            image_path (str): Path to image file
            folder_path (str): Target folder path
            
        Returns:
            dict: Base asset data
        """
        archive_size_mb = self._get_file_size_mb(archive_path)
        textures_in_archive = self._check_texture_folders_presence(folder_path)
        
        return {
            "type": "asset",
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

    def _preserve_user_data(self, asset_data: dict, existing_asset_data: dict | None, name: str) -> None:
        """
        Preserves user data from existing asset (stars, color, thumbnail, meta).
        
        Args:
            asset_data (dict): New asset data to update
            existing_asset_data (dict | None): Existing asset data
            name (str): Asset name for logging
        """
        if not existing_asset_data:
            return
        
        # Preserve stars
        if existing_asset_data.get("stars") is not None:
            asset_data["stars"] = existing_asset_data["stars"]
            logger.debug(f"Preserved stars: {existing_asset_data['stars']} for {name}")
        
        # Preserve color
        if existing_asset_data.get("color") is not None:
            asset_data["color"] = existing_asset_data["color"]
            logger.debug(f"Preserved color: {existing_asset_data['color']} for {name}")
        
        # Preserve thumbnail
        if existing_asset_data.get("thumbnail") is not None:
            asset_data["thumbnail"] = existing_asset_data["thumbnail"]
            logger.debug(f"Preserved thumbnail: {existing_asset_data['thumbnail']} for {name}")
        
        # Preserve meta data
        if "meta" in existing_asset_data:
            asset_data["meta"] = existing_asset_data["meta"]

    def _save_asset_with_error_handling(self, asset_data: dict, asset_file_path: str, name: str) -> bool:
        """
        Saves asset data to file with comprehensive error handling.
        
        Args:
            asset_data (dict): Asset data to save
            asset_file_path (str): Path to save the file
            name (str): Asset name for logging
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            save_to_file(asset_data, asset_file_path)
            logger.debug(f"Created .asset file: {name}.asset")
            return True
        except FileNotFoundError as e:
            logger.error(f"File not found while creating asset {name}: {e}")
            return False
        except PermissionError as e:
            logger.error(f"Permission denied while creating asset {name}: {e}")
            return False
        except OSError as e:
            logger.error(f"System error while creating asset {name}: {e}")
            return False
        except (ValueError, TypeError) as e:
            logger.error(f"Data error while creating asset {name}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error while creating asset {name}: {e}")
            return False

    def _create_single_asset(
        self, name: str, archive_path: str, image_path: str, folder_path: str
    ) -> dict | None:
        """
        Creates a single .asset file using specialized helper functions.

        This method is now much simpler and more maintainable than the previous
        monolithic implementation. It uses the Single Responsibility Principle
        by delegating specific tasks to specialized helper functions.

        Args:
            name (str): File name (without extension)
            archive_path (str): Path to archive file
            image_path (str): Path to image file
            folder_path (str): Path to target folder

        Returns:
            dict|None: Asset data dictionary or None on error
        """
        # Step 1: Validate all inputs
        is_valid, error_msg = self._validate_asset_creation_inputs(name, archive_path, image_path, folder_path)
        if not is_valid:
            logger.error(error_msg)
            return None

        # Step 2: Prepare file path
        asset_file_path = os.path.join(folder_path, f"{name}.asset")

        # Step 3: Load existing asset data (if any)
        existing_asset_data = self._load_existing_asset_data(asset_file_path)

        # Step 4: Create base asset data structure
        asset_data = self._create_base_asset_data(name, archive_path, image_path, folder_path)

        # Step 5: Preserve user data from existing asset
        self._preserve_user_data(asset_data, existing_asset_data, name)

        # Step 6: Save asset file with comprehensive error handling
        if self._save_asset_with_error_handling(asset_data, asset_file_path, name):
            return asset_data
        else:
            return None

    def _get_file_size_mb(self, file_path: str) -> float:
        """Gets file size in megabytes"""
        return get_file_size_mb(file_path)

    def _validate_thumbnail_inputs(self, asset_path: str, image_path: str) -> tuple[bool, str]:
        """
        Validates inputs for thumbnail creation.
        
        Args:
            asset_path (str): Path to the .asset file
            image_path (str): Path to the image file
            
        Returns:
            tuple[bool, str]: (is_valid, error_message_or_asset_name)
        """
        if not image_path or not os.path.exists(image_path):
            return False, f"Image file does not exist: {image_path}"
        
        if not asset_path:
            return False, "Asset path cannot be empty"
        
        asset_name = os.path.splitext(os.path.basename(asset_path))[0]
        return True, asset_name

    def _parse_thumbnail_result(self, result, asset_name: str) -> str | None:
        """
        Parses the result from generate_thumbnail function.
        
        Args:
            result: Result from generate_thumbnail
            asset_name (str): Name of the asset for logging
            
        Returns:
            str|None: Thumbnail filename (not full path) or None on error
        """
        if isinstance(result, tuple) and len(result) >= 1:
            thumbnail_full_path = result[0]  # First element is thumbnail path
            # Extract only filename from full path since thumbnails are always in .cache folder
            thumbnail_filename = os.path.basename(thumbnail_full_path)
            logger.debug(f"Extracted thumbnail filename: {thumbnail_filename} from full path: {thumbnail_full_path}")
            return thumbnail_filename
        else:
            logger.warning(f"Invalid result from generate_thumbnail for {asset_name}: {result}")
            return None

    def _update_asset_with_thumbnail(self, asset_path: str, thumbnail_filename: str) -> bool:
        """
        Updates the .asset file with thumbnail filename.
        
        Args:
            asset_path (str): Path to the .asset file
            thumbnail_filename (str): Filename of the thumbnail (not full path)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            asset_data = load_from_file(asset_path)
            if asset_data:
                asset_data["thumbnail"] = thumbnail_filename
                save_to_file(asset_data, asset_path)
                logger.debug(f"Updated .asset file with thumbnail filename: {thumbnail_filename}")
                return True
            else:
                logger.warning(f"Failed to load asset data from: {asset_path}")
                return False
        except Exception as e:
            logger.error(f"Error updating asset file {asset_path}: {e}")
            return False

    def create_thumbnail_for_asset(
        self, asset_path: str, image_path: str
    ) -> str | None:
        """
        Creates a thumbnail for an asset using specialized helper functions.
        
        This method is now much simpler and more maintainable than the previous
        implementation. It uses the Single Responsibility Principle by delegating
        specific tasks to specialized helper functions.

        Args:
            asset_path (str): Path to the .asset file
            image_path (str): Path to the image file

        Returns:
            str: Filename of the created thumbnail or None on error
        """
        # Step 1: Validate inputs
        is_valid, asset_name_or_error = self._validate_thumbnail_inputs(asset_path, image_path)
        if not is_valid:
            logger.error(asset_name_or_error)
            return None
        
        asset_name = asset_name_or_error
        
        try:
            logger.debug(f"Creating thumbnail for asset: {asset_name}, image: {image_path}")

            # Step 2: Generate thumbnail
            result = generate_thumbnail(image_path)
            logger.debug(f"generate_thumbnail result: {result}")

            # Step 3: Parse thumbnail result
            thumbnail_filename = self._parse_thumbnail_result(result, asset_name)
            
            if thumbnail_filename:
                logger.debug(f"Created thumbnail: {thumbnail_filename}")

                # Step 4: Update .asset file with thumbnail filename
                if self._update_asset_with_thumbnail(asset_path, thumbnail_filename):
                    return thumbnail_filename
                else:
                    logger.warning(f"Failed to update asset file for: {asset_name}")
                    return None
            else:
                logger.warning(f"Failed to create thumbnail for: {asset_name}")
                return None

        except Exception as e:
            return self._handle_error("thumbnail creation", e, asset_path)

    def _find_unpaired_files(self, archive_by_name: dict, image_by_name: dict, common_names: set) -> tuple[list, list]:
        """
        Finds unpaired files that don't have matching counterparts.
        
        Args:
            archive_by_name (dict): Dictionary of archive files by name
            image_by_name (dict): Dictionary of image files by name
            common_names (set): Set of common names
            
        Returns:
            tuple[list, list]: (unpaired_archives, unpaired_images)
        """
        # Find unpaired files (names without extensions)
        unpaired_archive_names = set(archive_by_name.keys()) - common_names
        unpaired_image_names = set(image_by_name.keys()) - common_names

        # Get full filenames with extensions
        unpaired_archives = [
            os.path.basename(archive_by_name[name])
            for name in unpaired_archive_names
        ]
        unpaired_images = [
            os.path.basename(image_by_name[name]) 
            for name in unpaired_image_names
        ]
        
        return unpaired_archives, unpaired_images

    def _create_unpaired_data_structure(self, unpaired_archives: list, unpaired_images: list) -> dict:
        """
        Creates data structure for unpaired files.
        
        Args:
            unpaired_archives (list): List of unpaired archive files
            unpaired_images (list): List of unpaired image files
            
        Returns:
            dict: Data structure ready for JSON serialization
        """
        return {
            "unpaired_archives": unpaired_archives,
            "unpaired_images": unpaired_images,
            "total_unpaired_archives": len(unpaired_archives),
            "total_unpaired_images": len(unpaired_images),
        }

    def _save_unpaired_files_json(self, folder_path: str, unpaired_data: dict) -> None:
        """
        Saves unpaired files data to JSON file.
        
        Args:
            folder_path (str): Path to the folder
            unpaired_data (dict): Data to save
        """
        unpaired_file_path = os.path.join(folder_path, "unpair_files.json")
        save_to_file(unpaired_data, unpaired_file_path)

        logger.info(
            f"Created unpair_files.json: "
            f"{unpaired_data['total_unpaired_archives']} unpaired archives, "
            f"{unpaired_data['total_unpaired_images']} unpaired images"
        )

    def _create_unpair_files_json(
        self,
        folder_path: str,
        archive_by_name: dict,
        image_by_name: dict,
        common_names: set,
    ) -> None:
        """
        Creates a JSON file with unpaired files using specialized helper functions.
        
        This method is now much simpler and more maintainable than the previous
        implementation. It uses the Single Responsibility Principle by delegating
        specific tasks to specialized helper functions.

        Args:
            folder_path (str): Path to the folder
            archive_by_name (dict): Dictionary of archive files by name
            image_by_name (dict): Dictionary of image files by name
            common_names (set): Set of common names
        """
        try:
            # Step 1: Find unpaired files
            unpaired_archives, unpaired_images = self._find_unpaired_files(
                archive_by_name, image_by_name, common_names
            )

            # Step 2: Create data structure
            unpaired_data = self._create_unpaired_data_structure(unpaired_archives, unpaired_images)

            # Step 3: Save to JSON file
            self._save_unpaired_files_json(folder_path, unpaired_data)

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
