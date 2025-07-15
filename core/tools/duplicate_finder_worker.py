"""
Duplicate Finder Worker module for CFAB Browser
Finds and moves duplicate files based on SHA-256 hash comparison
"""

import logging
import os
import shutil
from typing import Dict, List
from PyQt6.QtCore import pyqtSignal

from .base_worker import BaseToolWorker

# Import Rust module without pyright ignore
try:
    from core.__rust import hash_utils
    
    # Informational log about loading Rust module
    try:
        hash_utils_location = hash_utils.__file__
        build_info = hash_utils.get_build_info()
        build_timestamp = build_info.get('build_timestamp', 'unknown')
        module_number = build_info.get('module_number', '2')
        
        print(f"🦀 RUST HASH_UTILS: Using LOCAL version from: {hash_utils_location} [build: {build_timestamp}, module: {module_number}]")
    except AttributeError:
        print(f"🦀 RUST HASH_UTILS: Module loaded (no location information)")
except ImportError as e:
    print(f"⚠️ Warning: Could not import hash_utils module: {e}")
    hash_utils = None

logger = logging.getLogger(__name__)


class DuplicateFinderWorker(BaseToolWorker):
    """Worker for finding duplicate files based on SHA-256"""

    duplicates_found = pyqtSignal(list)  # list of duplicates to display

    def __init__(self, folder_path: str):
        super().__init__(folder_path)
        self.duplicates_to_move = []

    def _run_operation(self):
        """Main method for finding duplicates"""
        try:
            self._log_operation_start()

            # Find archive files
            archive_files = self._find_archive_files()
            if not archive_files:
                self._log_operation_end("No archive files to check")
                return

            # Calculate SHA-256 for each file
            file_hashes = self._calculate_file_hashes(archive_files)
            
            # Find duplicates
            duplicates = self._find_duplicates(file_hashes)
            
            if not duplicates:
                self._log_operation_end("No duplicates found")
                return

            # Prepare list for moving (newer files)
            self.duplicates_to_move = self._prepare_files_to_move(duplicates)
            
            # Move files to __duplicates__ folder
            moved_count = self._move_duplicates_to_folder()
            
            message = f"Found {len(duplicates)} duplicate groups. Moved {moved_count} files to __duplicates__ folder"
            self._log_operation_end(message)

        except Exception as e:
            self._log_error(f"Error while finding duplicates: {e}")

    def _find_archive_files(self) -> List[str]:
        """Finds archive files in the folder"""
        archive_extensions = {".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".sbsar", ".spsm"}
        return self._find_files_by_extensions(archive_extensions)

    def _calculate_file_hashes(self, files: List[str]) -> Dict[str, str]:
        """Calculates SHA-256 for each file"""
        file_hashes = {}
        total_files = len(files)
        
        for i, file_path in enumerate(files):
            try:
                if self._should_stop:
                    break
                    
                self._log_progress(
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
        if hash_utils is None:
            logger.error("Rust hash_utils module not available")
            return ""
        return hash_utils.calculate_sha256(file_path)

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
        """Zawsze zostawia najstarszy wg ctime (data utworzenia), resztę przenosi"""
        files_to_move = []
        
        for file_hash, file_list in duplicates.items():
            # Tworzymy listę (plik, ctime)
            files_with_ctime = []
            for file_path in file_list:
                try:
                    ctime = os.path.getctime(file_path)
                    files_with_ctime.append((file_path, ctime))
                except Exception as e:
                    logger.error(f"Błąd pobierania czasu utworzenia pliku {file_path}: {e}")
                    continue
            if len(files_with_ctime) > 1:
                # Sortujemy po ctime rosnąco
                files_sorted = sorted(files_with_ctime, key=lambda x: x[1])
                # Najstarszy zostaje, resztę przenosimy
                files_to_move.extend([f[0] for f in files_sorted[1:]])
            # Jeśli tylko jeden plik, nic nie przenosimy
        
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
                if self._safe_file_operation(shutil.move, file_path, destination):
                    moved_count += 1
                
            except Exception as e:
                logger.error(f"Error moving {file_path}: {e}")
                continue
        
        return moved_count 