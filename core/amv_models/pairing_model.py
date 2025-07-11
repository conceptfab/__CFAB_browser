import json
import logging
import os
import shutil

from core.scanner import AssetRepository
from core.json_utils import save_to_file

logger = logging.getLogger(__name__)


class PairingModel:
    def __init__(self):
        self.work_folder = ""
        self.unpair_files_path = ""
        self.unpaired_archives = []
        self.unpaired_images = []
        logger.debug("PairingModel initialized.")

    def set_work_folder(self, folder_path: str):
        self.work_folder = folder_path
        self.unpair_files_path = os.path.join(folder_path, "unpair_files.json")
        logger.info(f"PairingModel working folder set to: {folder_path}")
        self.load_unpair_files()

    def load_unpair_files(self):
        if not self.unpair_files_path:
            logger.warning(
                "PairingModel: Attempting to load unpair files without a path set."
            )
            self._create_default_unpair_files()
            return

        logger.info(f"Attempting to load unpair files from: {self.unpair_files_path}")

        if not os.path.exists(self.unpair_files_path):
            logger.warning(
                f"File not found: {self.unpair_files_path}. Creating a default one."
            )
            self._create_default_unpair_files()
            return

        try:
            with open(self.unpair_files_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.unpaired_archives = data.get("unpaired_archives", [])
                self.unpaired_images = data.get("unpaired_images", [])
                
                # Sort lists alphabetically after loading
                self.unpaired_archives.sort()
                self.unpaired_images.sort()
                
                logger.info(
                    f"Successfully loaded {self.unpair_files_path}. "
                    f"Found {len(self.unpaired_archives)} archives and "
                    f"{len(self.unpaired_images)} previews."
                )
        except json.JSONDecodeError:
            logger.error(
                f"JSON decoding error from {self.unpair_files_path}. Creating a default one."
            )
            self._create_default_unpair_files()
            # Reset lists in case of error
            self.unpaired_archives = []
            self.unpaired_images = []
        except Exception as e:
            logger.error(
                f"Error loading {self.unpair_files_path}: {e}. Creating a default one."
            )
            self._create_default_unpair_files()
            # Reset lists in case of error
            self.unpaired_archives = []
            self.unpaired_images = []

    def _create_default_unpair_files(self):
        self.unpaired_archives = []
        self.unpaired_images = []
        
        if not self.unpair_files_path:
            return
            
        default_data = {
            "unpaired_archives": [],
            "unpaired_images": [],
            "total_unpaired_archives": 0,
            "total_unpaired_images": 0,
        }
        
        try:
            save_to_file(default_data, self.unpair_files_path)
        except Exception as e:
            logger.error(f"Error creating default {self.unpair_files_path}: {e}")

    def save_unpair_files(self):
        if not self.unpair_files_path:
            return  # Do not save if path is not set
        
        # Sort lists alphabetically before saving
        sorted_archives = sorted(self.unpaired_archives)
        sorted_images = sorted(self.unpaired_images)
        
        data = {
            "unpaired_archives": sorted_archives,
            "unpaired_images": sorted_images,
            "total_unpaired_archives": len(sorted_archives),
            "total_unpaired_images": len(sorted_images),
        }
        try:
            with open(self.unpair_files_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            logger.error(f"Error writing {self.unpair_files_path}: {e}")

    def get_unpaired_archives(self):
        return self.unpaired_archives

    def get_unpaired_images(self):
        return self.unpaired_images

    def remove_paired_files(self, archive_file, preview_file):
        if archive_file in self.unpaired_archives:
            self.unpaired_archives.remove(archive_file)
        if preview_file in self.unpaired_images:
            self.unpaired_images.remove(preview_file)
        self.save_unpair_files()

    def add_unpaired_archive(self, archive_file):
        if archive_file not in self.unpaired_archives:
            self.unpaired_archives.append(archive_file)
            self.save_unpair_files()

    def add_unpaired_image(self, image_file):
        if image_file not in self.unpaired_images:
            self.unpaired_images.append(image_file)
            self.save_unpair_files()

    def delete_unpaired_archives(self):
        """Deletes all unpaired archives from disk and updates the list."""
        if not self._validate_work_folder():
            return False

        work_folder = self.work_folder
        deleted_count = 0
        failed_count = 0

        for archive_name in self.unpaired_archives[:]:  # Iterate over a copy
            success = self._delete_single_archive(work_folder, archive_name)
            if success:
                deleted_count += 1
            else:
                failed_count += 1

        self.save_unpair_files()
        logger.info(
            f"Deleting archives finished. Deleted: {deleted_count}, Failures: {failed_count}."
        )
        return failed_count == 0

    def delete_unpaired_images(self):
        """Deletes all unpaired images from disk and updates the list."""
        if not self._validate_work_folder():
            return False

        work_folder = self.work_folder
        deleted_count = 0
        failed_count = 0

        for image_name in self.unpaired_images[:]:  # Iterate over a copy
            success = self._delete_single_image(work_folder, image_name)
            if success:
                deleted_count += 1
            else:
                failed_count += 1

        self.save_unpair_files()
        logger.info(
            f"Deleting previews finished. Deleted: {deleted_count}, Failures: {failed_count}."
        )
        return failed_count == 0
    
    def _validate_work_folder(self) -> bool:
        """Validate that work folder is set and exists"""
        if not self.work_folder:
            logger.error("Cannot delete files, the working folder path is not set.")
            return False
        
        if not os.path.exists(self.work_folder):
            logger.error(f"Working folder does not exist: {self.work_folder}")
            return False
        
        return True
    
    def _delete_single_archive(self, work_folder: str, archive_name: str) -> bool:
        """Delete single archive file with proper error handling"""
        try:
            file_path = os.path.join(work_folder, archive_name)
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Deleted unpaired archive: {file_path}")
                self.unpaired_archives.remove(archive_name)
                return True
            else:
                logger.warning(
                    f"Archive not found for deletion, removing from list: {file_path}"
                )
                self.unpaired_archives.remove(archive_name)
                return True  # Not an error, just file doesn't exist
        except PermissionError as e:
            logger.error(f"No permissions to delete archive {archive_name}: {e}")
            return False
        except OSError as e:
            logger.error(f"OS error deleting archive {archive_name}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error deleting archive {archive_name}: {e}")
            return False
    
    def _delete_single_image(self, work_folder: str, image_name: str) -> bool:
        """Delete single image file with proper error handling"""
        try:
            file_path = os.path.join(work_folder, image_name)
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Deleted unpaired image: {file_path}")
                self.unpaired_images.remove(image_name)
                return True
            else:
                logger.warning(
                    f"Image not found for deletion, removing from list: {file_path}"
                )
                self.unpaired_images.remove(image_name)
                return True  # Not an error, just file doesn't exist
        except PermissionError as e:
            logger.error(f"Permission denied deleting image {image_name}: {e}")
            return False
        except OSError as e:
            logger.error(f"OS error deleting image {image_name}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error deleting image {image_name}: {e}")
            return False

    def create_asset_from_pair(self, archive_full_path: str, preview_full_path: str):
        archive_name_without_ext = os.path.splitext(
            os.path.basename(archive_full_path)
        )[0]
        preview_ext = os.path.splitext(os.path.basename(preview_full_path))[1]
        new_preview_name = f"{archive_name_without_ext}{preview_ext}"
        new_preview_full_path = os.path.join(
            os.path.dirname(preview_full_path), new_preview_name
        )

        try:
            # 1. Rename the preview file
            if preview_full_path != new_preview_full_path:
                shutil.move(preview_full_path, new_preview_full_path)
                logger.info(
                    f"Renamed preview from {preview_full_path} to {new_preview_full_path}"
                )

            # 2. Create asset
            work_folder_path = os.path.dirname(archive_full_path)
            asset_repository = AssetRepository()
            asset_data = asset_repository._create_single_asset(
                archive_name_without_ext,
                archive_full_path,
                new_preview_full_path,
                work_folder_path,
            )
            if asset_data:
                logger.info(f"Created asset for {archive_name_without_ext}")
                # 3. Create thumbnail
                thumbnail_success = asset_repository.create_thumbnail_for_asset(
                    os.path.join(work_folder_path, f"{archive_name_without_ext}.asset"),
                    new_preview_full_path,
                )
                if thumbnail_success:
                    logger.info(f"Created thumbnail for {archive_name_without_ext}")
                else:
                    logger.warning(
                        f"Failed to create thumbnail for {archive_name_without_ext}"
                    )

                # 4. Update unpair_files.json
                self.remove_paired_files(
                    os.path.basename(archive_full_path),
                    os.path.basename(preview_full_path),
                )
                return True
            else:
                logger.error(f"Failed to create asset for {archive_name_without_ext}")
                return False
        except Exception as e:
            logger.error(f"Error creating asset from pair: {e}")
            return False
