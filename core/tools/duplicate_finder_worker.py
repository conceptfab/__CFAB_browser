"""
Duplicate Finder Worker module for CFAB Browser
Finds and moves duplicate files based on SHA-256 hash comparison
"""

import logging
import os
import shutil
from typing import Dict, List
from PyQt6.QtCore import pyqtSignal

from .base_worker import BaseWorker
from core.__rust import hash_utils  # pyright: ignore

# Informational log about loading Rust module
try:
    hash_utils_location = hash_utils.__file__
    
    # Pobierz informacje o kompilacji
    build_info = hash_utils.get_build_info()
    build_timestamp = build_info.get('build_timestamp', 'unknown')
    module_number = build_info.get('module_number', '2')
    
    print(f"🦀 RUST HASH_UTILS: Using LOCAL version from: {hash_utils_location} [build: {build_timestamp}, module: {module_number}]")
except AttributeError:
    print(f"🦀 RUST HASH_UTILS: Module loaded (no location information)")

logger = logging.getLogger(__name__)


class DuplicateFinderWorker(BaseWorker):
    """Worker for finding duplicate files based on SHA-256"""

    finished = pyqtSignal(str)  # message
    duplicates_found = pyqtSignal(list)  # list of duplicates to display

    def __init__(self, folder_path: str):
        super().__init__(folder_path)
        self.duplicates_to_move = []

    def _run_operation(self):
        """Main method for finding duplicates"""
        try:
            logger.info(f"Starting duplicate search in folder: {self.folder_path}")

            # Find archive files
            archive_files = self._find_archive_files()
            if not archive_files:
                self.finished.emit("No archive files to check")
                return

            # Calculate SHA-256 for each file
            file_hashes = self._calculate_file_hashes(archive_files)
            
            # Find duplicates
            duplicates = self._find_duplicates(file_hashes)
            
            if not duplicates:
                self.finished.emit("No duplicates found")
                return

            # Prepare list for moving (newer files)
            self.duplicates_to_move = self._prepare_files_to_move(duplicates)
            
            # Move files to __duplicates__ folder
            moved_count = self._move_duplicates_to_folder()
            
            message = f"Found {len(duplicates)} duplicate groups. Moved {moved_count} files to __duplicates__ folder"
            self.finished.emit(message)

        except Exception as e:
            error_msg = f"Error while finding duplicates: {e}"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)

    def _find_archive_files(self) -> List[str]:
        """Finds archive files in the folder"""
        archive_extensions = {".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".sbsar"}
        archive_files = []
        
        for item in os.listdir(self.folder_path):
            item_path = os.path.join(self.folder_path, item)
            if os.path.isfile(item_path):
                file_ext = os.path.splitext(item)[1].lower()
                if file_ext in archive_extensions:
                    archive_files.append(item_path)
        
        return archive_files

    def _calculate_file_hashes(self, files: List[str]) -> Dict[str, str]:
        """Calculates SHA-256 for each file"""
        file_hashes = {}
        total_files = len(files)
        
        for i, file_path in enumerate(files):
            try:
                if self._should_stop:
                    break
                    
                self.progress_updated.emit(
                    i, total_files, f"Calculating SHA-256: {os.path.basename(file_path)}"
                )
                
                sha256_hash = self._calculate_sha256(file_path)
                file_hashes[file_path] = sha256_hash
                
            except Exception as e:
                logger.error(f"Error calculating SHA-256 for {file_path}: {e}")
                continue
        
        return file_hashes

    def _calculate_sha256(self, file_path: str) -> str:
        """Calculates SHA-256 for a single file using Rust module"""
        return hash_utils.calculate_sha256(file_path)  # type: ignore

    def _find_duplicates(self, file_hashes: Dict[str, str]) -> Dict[str, List[str]]:
        """Finds duplicates based on SHA-256"""
        hash_to_files = {}
        
        # Group files by hash
        for file_path, file_hash in file_hashes.items():
            if file_hash not in hash_to_files:
                hash_to_files[file_hash] = []
            hash_to_files[file_hash].append(file_path)
        
        # Return only groups with duplicates (more than 1 file)
        duplicates = {}
        for file_hash, file_list in hash_to_files.items():
            if len(file_list) > 1:
                duplicates[file_hash] = file_list
        
        return duplicates

    def _prepare_files_to_move(self, duplicates: Dict[str, List[str]]) -> List[str]:
        """Prepares a list of files to move (newer files)"""
        files_to_move = []
        
        for file_hash, file_list in duplicates.items():
            # Sort files by modification date (oldest first)
            sorted_files = sorted(file_list, key=lambda x: os.path.getmtime(x))
            
            # Move all but the oldest
            for file_path in sorted_files[1:]:
                files_to_move.append(file_path)
        
        return files_to_move

    def _move_duplicates_to_folder(self) -> int:
        """Moves duplicates to the __duplicates__ folder"""
        if not self.duplicates_to_move:
            return 0
            
        # Create __duplicates__ folder if it doesn't exist
        duplicates_folder = os.path.join(self.folder_path, "__duplicates__")
        os.makedirs(duplicates_folder, exist_ok=True)
        
        moved_count = 0
        
        for file_path in self.duplicates_to_move:
            try:
                if self._should_stop:
                    break
                    
                filename = os.path.basename(file_path)
                destination = os.path.join(duplicates_folder, filename)
                
                # Move archive file
                shutil.move(file_path, destination)
                moved_count += 1
                
                # Find and move related files (asset and cache)
                self._move_related_files(file_path, duplicates_folder)
                
            except Exception as e:
                logger.error(f"Error moving {file_path}: {e}")
                continue
        
        return moved_count

    def _move_related_files(self, original_file_path: str, duplicates_folder: str):
        """Moves related files (asset and cache) to the duplicates folder"""
        try:
            base_name = os.path.splitext(os.path.basename(original_file_path))[0]
            folder_path = os.path.dirname(original_file_path)
            
            # Search for related files in the folder
            for item in os.listdir(folder_path):
                item_path = os.path.join(folder_path, item)
                if os.path.isfile(item_path):
                    item_base_name = os.path.splitext(item)[0]
                    
                    # Check if it's a related file (same base name)
                    if item_base_name == base_name and item_path != original_file_path:
                        try:
                            destination = os.path.join(duplicates_folder, item)
                            shutil.move(item_path, destination)
                            logger.info(f"Moved related file: {item}")
                        except Exception as e:
                            logger.error(f"Error moving related file {item}: {e}")
            
            # Check cache folder
            cache_folder = os.path.join(folder_path, "cache")
            if os.path.exists(cache_folder):
                for item in os.listdir(cache_folder):
                    if item.startswith(base_name):
                        try:
                            item_path = os.path.join(cache_folder, item)
                            
                            # Create cache folder in __duplicates__ if it doesn't exist
                            duplicates_cache_folder = os.path.join(duplicates_folder, "cache")
                            os.makedirs(duplicates_cache_folder, exist_ok=True)
                            
                            destination = os.path.join(duplicates_cache_folder, item)
                            shutil.move(item_path, destination)
                            logger.info(f"Moved cache file: {item}")
                        except Exception as e:
                            logger.error(f"Error moving cache file {item}: {e}")
            
        except Exception as e:
            logger.error(f"Error moving related files: {e}") 