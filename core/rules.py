#!/usr/bin/env python3
"""
Rules - Decision logic for handling folder clicks

This module contains the FolderClickRules class, which implements decision logic
for the CFAB Browser application. The class analyzes folder contents and decides
whether to run the scanner to process files or display the gallery of ready assets.

Main features:
- Analyzes folder contents (asset files, archives, previews)
- Checks for the existence and contents of the .cache folder
- Decides on action based on folder state
- Handles various scenarios (no files, incomplete cache, ready assets)

Author: CFAB Browser Team
Date: 2025
"""

import logging
import os
import re
import time
from typing import Dict, Optional, Set

from core.performance_monitor import measure_operation
from core.json_utils import load_from_file

logger = logging.getLogger(__name__)


class DecisionStrategy:
    """Abstract base class for folder decision strategies"""
    
    @staticmethod
    def execute(folder_path: str, content: Dict) -> Dict:
        """Execute the decision strategy
        
        Args:
            folder_path: Path to the folder being analyzed
            content: Analyzed folder content data
            
        Returns:
            dict: Decision result with action, message, condition, details
        """
        raise NotImplementedError("Subclasses must implement execute method")


class Condition1Strategy(DecisionStrategy):
    """Strategy for Condition 1: Archives but no assets → Run scanner"""
    
    @staticmethod
    def execute(folder_path: str, content: Dict) -> Dict:
        """Handle condition 1: Folder contains archive/preview files, but NO asset files"""
        asset_count = content["asset_count"]
        preview_archive_count = content["preview_archive_count"]

        logger.debug(
            f"CONDITION 1: {folder_path} | "
            f"Asset files: {asset_count} | "
            f"Archive/Preview files: {preview_archive_count} | "
            f"DECISION: Running scanner (no asset files)"
        )

        return {
            "action": "run_scanner",
            "message": f"No asset files - running scanner",
            "condition": "condition_1",
            "details": {
                "asset_count": asset_count,
                "preview_archive_count": preview_archive_count,
            },
        }


class Condition2aStrategy(DecisionStrategy):
    """Strategy for Condition 2a: Both archives and assets, but no cache → Run scanner"""
    
    @staticmethod
    def execute(folder_path: str, content: Dict) -> Dict:
        """Handle condition 2a: Both file types exist, but no .cache folder"""
        asset_count = content["asset_count"]
        preview_archive_count = content["preview_archive_count"]

        logger.debug(
            f"CONDITION 2a: {folder_path} | "
            f"Asset files: {asset_count} | "
            f"Archive/Preview files: {preview_archive_count} | "
            f"Cache: NO | "
            f"DECISION: Running scanner (no cache)"
        )

        return {
            "action": "run_scanner",
            "message": f"Both types of files, but no cache - running scanner",
            "condition": "condition_2a",
            "details": {
                "asset_count": asset_count,
                "preview_archive_count": preview_archive_count,
                "cache_exists": False,
            },
        }


class Condition2bStrategy(DecisionStrategy):
    """Strategy for Condition 2b: Both archives and assets, cache exists but mismatched → Run scanner"""
    
    @staticmethod
    def execute(folder_path: str, content: Dict) -> Dict:
        """Handle condition 2b: Cache exists but thumbnail count doesn't match asset count"""
        asset_count = content["asset_count"]
        preview_archive_count = content["preview_archive_count"]
        cache_thumb_count = content["cache_thumb_count"]

        logger.debug(
            f"CONDITION 2b: {folder_path} | "
            f"Asset files: {asset_count} | "
            f"Archive/Preview files: {preview_archive_count} | "
            f"Cache: YES | "
            f"Thumbnails: {cache_thumb_count} | "
            f"DECISION: Running scanner (cache mismatch)"
        )

        return {
            "action": "run_scanner",
            "message": (
                f"Both types of files, mismatched number of thumbnails "
                f"({cache_thumb_count}) and asset files ({asset_count}) - "
                f"running scanner"
            ),
            "condition": "condition_2b",
            "details": {
                "asset_count": asset_count,
                "preview_archive_count": preview_archive_count,
                "cache_exists": True,
                "cache_thumb_count": cache_thumb_count,
            },
        }


class Condition2cStrategy(DecisionStrategy):
    """Strategy for Condition 2c: Both archives and assets, cache ready → Show gallery"""
    
    @staticmethod
    def execute(folder_path: str, content: Dict) -> Dict:
        """Handle condition 2c: Everything is ready, can display gallery"""
        asset_count = content["asset_count"]
        preview_archive_count = content["preview_archive_count"]
        cache_thumb_count = content["cache_thumb_count"]

        logger.debug(
            f"CONDITION 2c: {folder_path} | "
            f"Asset files: {asset_count} | "
            f"Archive/Preview files: {preview_archive_count} | "
            f"Cache: YES | "
            f"Thumbnails: {cache_thumb_count} | "
            f"DECISION: Displaying gallery (all ready)"
        )

        return {
            "action": "show_gallery",
            "message": (
                f"Both types of files, all ready - "
                f"displaying gallery (thumb: {cache_thumb_count}, "
                f"asset: {asset_count})"
            ),
            "condition": "condition_2c",
            "details": {
                "asset_count": asset_count,
                "preview_archive_count": preview_archive_count,
                "cache_exists": True,
                "cache_thumb_count": cache_thumb_count,
            },
        }


class AdditionalCaseStrategy(DecisionStrategy):
    """Strategy for Additional Cases: Only assets (no archives)"""
    
    @staticmethod
    def execute(folder_path: str, content: Dict) -> Dict:
        """Handle additional cases: Only asset files, various cache states"""
        asset_count = content["asset_count"]
        cache_exists = content["cache_exists"]
        cache_thumb_count = content["cache_thumb_count"]
        
        # No .cache folder → Run scanner
        if not cache_exists:
            logger.debug(
                f"ADDITIONAL CASE (NO CACHE): {folder_path} | "
                f"Asset files: {asset_count} | "
                f"Cache: NO | "
                f"DECISION: Running scanner (no cache)"
            )
            
            return {
                "action": "run_scanner",
                "message": f"Only asset files, no cache - running scanner",
                "condition": "additional_case_no_cache",
                "details": {
                    "asset_count": asset_count,
                    "cache_exists": False,
                },
            }
        
        # Mismatched number of thumbnails → Run scanner
        elif cache_thumb_count != asset_count:
            logger.debug(
                f"ADDITIONAL CASE (MISMATCH): {folder_path} | "
                f"Asset files: {asset_count} | "
                f"Cache: YES | "
                f"Thumbnails: {cache_thumb_count} | "
                f"DECISION: Running scanner (cache mismatch)"
            )
            
            return {
                "action": "run_scanner",
                "message": (
                    f"Only asset files, mismatched number of thumbnails "
                    f"({cache_thumb_count}) and asset files ({asset_count}) - "
                    f"running scanner"
                ),
                "condition": "additional_case_mismatch",
                "details": {
                    "asset_count": asset_count,
                    "preview_archive_count": 0,
                    "cache_exists": True,
                    "cache_thumb_count": cache_thumb_count,
                },
            }
        
        # All ready → Display gallery
        else:
            logger.debug(
                f"ADDITIONAL CASE (READY): {folder_path} | "
                f"Asset files: {asset_count} | "
                f"Cache: YES | "
                f"Thumbnails: {cache_thumb_count} | "
                f"DECISION: Displaying gallery (all ready)"
            )
            
            return {
                "action": "show_gallery",
                "message": (
                    f"Only asset files, all ready - "
                    f"displaying gallery (thumb: {cache_thumb_count}, "
                    f"asset: {asset_count})"
                ),
                "condition": "additional_case_ready",
                "details": {
                    "asset_count": asset_count,
                    "preview_archive_count": 0,
                    "cache_exists": True,
                    "cache_thumb_count": cache_thumb_count,
                },
            }


class DefaultCaseStrategy(DecisionStrategy):
    """Strategy for Default Case: No appropriate files → No action"""
    
    @staticmethod
    def execute(folder_path: str, content: Dict) -> Dict:
        """Handle default case: Folder does not contain appropriate files"""
        asset_count = content["asset_count"]
        preview_archive_count = content["preview_archive_count"]
        cache_exists = content["cache_exists"]
        cache_thumb_count = content["cache_thumb_count"]

        logger.debug(
            f"DEFAULT CASE: {folder_path} | "
            f"Asset files: {asset_count} | "
            f"Archive/Preview files: {preview_archive_count} | "
            f"Cache: {'YES' if cache_exists else 'NO'} | "
            f"Thumbnails: {cache_thumb_count} | "
            f"DECISION: No action (folder does not contain appropriate files)"
        )

        return {
            "action": "no_action",
            "message": "Folder does not contain appropriate files",
            "condition": "default_case",
            "details": {
                "asset_count": asset_count,
                "preview_archive_count": preview_archive_count,
                "cache_exists": cache_exists,
                "cache_thumb_count": cache_thumb_count,
            },
        }


class FolderClickRules:
    """
    Class containing decision logic for folder clicks

    This class implements a decision algorithm that analyzes folder contents
    and decides which action to take:

    - Run the scanner (when there are no asset files or incomplete cache)
    - Display the gallery (when everything is ready)
    - Do nothing (when the folder does not contain appropriate files)

    The class handles the following file types:
    - .asset files - main asset files
    - Archive files (.rar, .zip, .sbsar) - sources for processing
    - Preview files (.jpg, .png, .jpeg, .gif) - preview images
    - .cache folder - cache with generated thumbnails
    """

    # Stałe konfiguracyjne
    CACHE_FOLDER_NAME = ".cache"
    THUMB_EXTENSION = ".thumb"

    # Zbiory rozszerzeń plików dla efektywnego lookup
    ASSET_EXTENSIONS: Set[str] = {".asset"}
    ARCHIVE_EXTENSIONS: Set[str] = {".rar", ".zip", ".sbsar", ".7z"}
    PREVIEW_EXTENSIONS: Set[str] = {".jpg", ".jpeg", ".png",".webp", ".gif"}

    # Cache TTL (Time To Live) w sekundach
    CACHE_TTL = 300  # 5 minutes

    # Cache dla wyników analizy folderów
    _folder_analysis_cache: Dict[str, Dict] = {}
    _cache_timestamps: Dict[str, float] = {}

    @staticmethod
    def _validate_folder_path(folder_path: str) -> Optional[str]:
        """
        Validates the folder path for security

        Args:
            folder_path (str): Path to validate

        Returns:
            Optional[str]: Error message or None if the path is valid
        """
        if not folder_path:
            return "Folder path cannot be empty"

        if not isinstance(folder_path, str):
            return "Folder path must be a string"

        # Sprawdź czy ścieżka nie zawiera sekwencji path traversal
        if ".." in folder_path or "\\.." in folder_path or "/.." in folder_path:
            return "Folder path contains forbidden path traversal sequences"

        # Sprawdź czy ścieżka nie jest zbyt długa
        if len(folder_path) > 4096:
            return "Folder path is too long"

        # Sprawdź czy ścieżka nie zawiera niedozwolonych znaków
        # Note: colon (:) is allowed in Windows (C:\)
        invalid_chars = re.search(r'[<>"|?*]', folder_path)
        if invalid_chars:
            return f"Folder path contains forbidden characters: {invalid_chars.group()}"

        return None

    @staticmethod
    def _is_cache_valid(folder_path: str) -> bool:
        """
        Checks if the cache for the folder is up to date

        Args:
            folder_path (str): Path to the folder

        Returns:
            bool: True if the cache is up to date
        """
        if folder_path not in FolderClickRules._cache_timestamps:
            return False

        current_time = time.time()
        cache_time = FolderClickRules._cache_timestamps[folder_path]

        return (current_time - cache_time) < FolderClickRules.CACHE_TTL

    @staticmethod
    def _get_cached_analysis(folder_path: str) -> Optional[Dict]:
        """
        Gets cached folder analysis

        Args:
            folder_path (str): Path to the folder

        Returns:
            Optional[Dict]: Cached analysis or None
        """
        if (
            folder_path in FolderClickRules._folder_analysis_cache
            and FolderClickRules._is_cache_valid(folder_path)
        ):
            logger.debug(f"Cache hit for folder: {folder_path}")
            return FolderClickRules._folder_analysis_cache[folder_path]

        return None

    @staticmethod
    def _cache_analysis(folder_path: str, analysis: Dict) -> None:
        """
        Saves folder analysis to cache

        Args:
            folder_path (str): Path to the folder
            analysis (Dict): Analysis result to cache
        """
        FolderClickRules._folder_analysis_cache[folder_path] = analysis
        FolderClickRules._cache_timestamps[folder_path] = time.time()
        logger.debug(f"Cached folder analysis: {folder_path}")

    @staticmethod
    def _categorize_file(item: str) -> Optional[str]:
        """
        Categorizes a file based on its extension

        Args:
            item (str): File name

        Returns:
            Optional[str]: File category or None if not matched
        """
        if item.startswith("."):
            return None

        item_lower = item.lower()

        # Sprawdź rozszerzenia używając sets dla O(1) lookup
        for ext in FolderClickRules.ASSET_EXTENSIONS:
            if item_lower.endswith(ext):
                return "asset"

        for ext in FolderClickRules.ARCHIVE_EXTENSIONS:
            if item_lower.endswith(ext):
                return "archive"

        for ext in FolderClickRules.PREVIEW_EXTENSIONS:
            if item_lower.endswith(ext):
                return "preview"

        return None

    @staticmethod
    def _analyze_cache_folder(cache_folder_path: str) -> int:
        """
        Analyzes the contents of the cache folder and returns the number of thumbnails

        Args:
            cache_folder_path (str): Path to the cache folder

        Returns:
            int: Number of thumbnail files
        """
        try:
            if not os.path.exists(cache_folder_path) or not os.path.isdir(
                cache_folder_path
            ):
                return 0

            cache_items = os.listdir(cache_folder_path)
            thumb_count = sum(
                1
                for item in cache_items
                if item.lower().endswith(FolderClickRules.THUMB_EXTENSION)
            )

            return thumb_count

        except (OSError, PermissionError) as e:
            logger.warning(f"Error checking .cache: {e}")
            return 0

    @staticmethod
    def _create_error_result(error_message: str) -> dict:
        """
        Helper method for generating an error dictionary
        """
        return {
            "error": error_message,
            "asset_files": [],
            "preview_archive_files": [],
            "cache_exists": False,
            "cache_thumb_count": 0,
            "asset_count": 0,
            "preview_archive_count": 0,
        }

    @staticmethod
    def analyze_folder_content(folder_path: str) -> dict:
        """
        Analyzes the contents of a folder and returns detailed file information

        Method scans the folder for different types of files:
        - .asset files (main asset files)
        - Archive files (.rar, .zip, .sbsar)
        - Preview files (.jpg, .png, .jpeg, .gif)
        - .cache folder with thumbnails

        Args:
            folder_path (str): Path to the folder to analyze

        Returns:
            dict: Dictionary containing:
                - asset_files: list of .asset files
                - preview_archive_files: list of archive and preview files
                - cache_exists: whether .cache folder exists
                - cache_thumb_count: number of thumbnail files in .cache
                - asset_count: number of asset files
                - preview_archive_count: number of archive/preview files
                - error: error message (if any)

        Example return dictionary:
        {
            "asset_files": ["model.asset", "texture.asset"],
            "preview_archive_files": ["model.zip", "preview.jpg"],
            "cache_exists": True,
            "cache_thumb_count": 2,
            "asset_count": 2,
            "preview_archive_count": 2
        }
        """
        # Check cache
        cached_result = FolderClickRules._get_cached_analysis(folder_path)
        if cached_result:
            return cached_result

        # Input validation
        validation_error = FolderClickRules._validate_folder_path(folder_path)
        if validation_error:
            return FolderClickRules._create_error_result(validation_error)

        try:
            # Check if folder exists
            if not os.path.exists(folder_path):
                return FolderClickRules._create_error_result(
                    f"Folder does not exist: {folder_path}"
                )

            # Get list of all items in the folder
            try:
                items = os.listdir(folder_path)
            except (OSError, PermissionError) as e:
                return FolderClickRules._create_error_result(
                    f"No read permission for folder: {e}"
                )

            # Categorize files by type
            asset_files = []
            preview_archive_files = []

            for item in items:
                category = FolderClickRules._categorize_file(item)
                if category == "asset":
                    asset_files.append(item)
                elif category in ("archive", "preview"):
                    preview_archive_files.append(item)

            # Check for existence and contents of .cache folder
            cache_folder_path = os.path.join(
                folder_path, FolderClickRules.CACHE_FOLDER_NAME
            )
            cache_exists = os.path.exists(cache_folder_path) and os.path.isdir(
                cache_folder_path
            )

            # Count thumbnail files in .cache folder
            cache_thumb_count = FolderClickRules._analyze_cache_folder(
                cache_folder_path
            )

            # Prepare result
            result = {
                "asset_files": asset_files,
                "preview_archive_files": preview_archive_files,
                "cache_exists": cache_exists,
                "cache_thumb_count": cache_thumb_count,
                "asset_count": len(asset_files),
                "preview_archive_count": len(preview_archive_files),
            }

            # Cache result
            FolderClickRules._cache_analysis(folder_path, result)

            return result

        except Exception as e:
            logger.error(f"Folder analysis error: {e}")
            return FolderClickRules._create_error_result(f"Folder analysis error: {e}")

    @staticmethod
    def _log_folder_analysis(folder_path: str, content: Dict) -> None:
        """
        Logs folder analysis information at DEBUG level

        Args:
            folder_path (str): Path to the folder
            content (Dict): Folder analysis result
        """
        logger.debug(
            f"FOLDER ANALYSIS: {folder_path} | "
            f"Asset: {content.get('asset_count', 0)} | "
            f"Previews/Archives: {content.get('preview_archive_count', 0)} | "
            f"Cache: {'YES' if content.get('cache_exists', False) else 'NO'} | "
            f"Thumbnails: {content.get('cache_thumb_count', 0)}"
        )

    @staticmethod
    def decide_action(folder_path: str) -> dict:
        """
        Decides on the action to take based on folder contents

        Method implements a decision algorithm based on the following
        conditions:

        CONDITION 1: Folder contains archive/preview files, but NO asset files
        → Run scanner (necessary processing of archives into asset files)

        CONDITION 2: Folder contains both archive/preview files and asset files
        - 2a: No .cache folder → Run scanner (generating thumbnails)
        - 2b: .cache exists, but number of thumbnails ≠ number of asset files
        → Run scanner
        - 2c: .cache exists and number of thumbnails = number of asset files
        → Display gallery

        ADDITIONAL CASE: Folder contains only asset files (without archives)
        - No .cache or mismatched number of thumbnails → Run scanner
        - All ready → Display gallery

        Args:
            folder_path (str): Path to the folder to analyze

        Returns:
            dict: Dictionary containing the decision:
                - action: "run_scanner", "show_gallery", "no_action", "error"
                - message: Decision description in Polish
                - condition: Name of the condition that was met
                - details: Detailed information about folder state

        Example return dictionary:
        {
            "action": "run_scanner",
            "message": "No asset files - running scanner",
            "condition": "condition_1",
            "details": {
                "preview_archive_count": 3,
                "asset_count": 0
            }
        }
        """
        try:
            # Step 1: Analyze folder contents
            content = FolderClickRules.analyze_folder_content(folder_path)

            # Check if there was an error during analysis
            if "error" in content:
                logger.error(
                    f"FOLDER ANALYSIS ERROR: {folder_path} - {content['error']}"
                )
                return {
                    "action": "error",
                    "message": content["error"],
                    "condition": "error",
                }

            # Step 2: Extract key information
            asset_count = content["asset_count"]
            preview_archive_count = content["preview_archive_count"]
            cache_exists = content["cache_exists"]
            cache_thumb_count = content["cache_thumb_count"]

            # Log diagnostic information
            FolderClickRules._log_folder_analysis(folder_path, content)

            # CONDITION 1: Folder contains archive/preview files, but NO asset files
            # → Scanner must process archives into asset files
            if preview_archive_count > 0 and asset_count == 0:
                return Condition1Strategy.execute(folder_path, content)

            # CONDITION 2: Folder contains both archive/preview files and asset files
            elif preview_archive_count > 0 and asset_count > 0:

                # Subcondition 2a: No .cache folder
                # → Scanner must generate thumbnails
                if not cache_exists:
                    return Condition2aStrategy.execute(folder_path, content)

                # Subcondition 2b: .cache exists, but number of thumbnails ≠ number of
                # asset files → Scanner must supplement missing thumbnails
                elif cache_thumb_count != asset_count:
                    return Condition2bStrategy.execute(folder_path, content)

                # Subcondition 2c: .cache exists and number of thumbnails = number of
                # asset files → All ready, can display gallery
                else:
                    return Condition2cStrategy.execute(folder_path, content)

            # ADDITIONAL CASE: Folder contains only asset files (without archives)
            # → Check if cache is complete
            elif asset_count > 0 and preview_archive_count == 0:

                # No .cache folder → Run scanner
                if not cache_exists:
                    return AdditionalCaseStrategy.execute(folder_path, content)

                # Mismatched number of thumbnails → Run scanner
                elif cache_thumb_count != asset_count:
                    return AdditionalCaseStrategy.execute(folder_path, content)

                # All ready → Display gallery
                else:
                    return AdditionalCaseStrategy.execute(folder_path, content)

            # DEFAULT CASE: Folder does not contain appropriate files
            # → Do nothing
            else:
                return DefaultCaseStrategy.execute(folder_path, content)

        except Exception as e:
            error_msg = f"Error deciding action for folder {folder_path}: {e}"
            logger.error(f"DECISION ERROR: {folder_path} - {error_msg}")
            return {"action": "error", "message": error_msg, "condition": "error"}
