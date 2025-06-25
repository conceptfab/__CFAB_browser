# PATCH-CODE DLA: RULES.PY

**Powiązany plik z analizą:** `../corrections/rules_correction.md`
**Zasady ogólne:** `../refactoring_rules.md`

---

### PATCH 1: BEZPIECZEŃSTWO I WALIDACJA INPUT

**Problem:** Brak walidacji wejścia i potencjalna podatność na Path Traversal
**Rozwiązanie:** Dodanie comprehensive input validation i security checks

```python
import logging
import os
from pathlib import Path
from typing import Dict, Set
import functools
import time

logger = logging.getLogger(__name__)

class FolderClickRules:
    """
    Klasa zawierająca logikę decyzyjną dla kliknięć w foldery
    z ulepszoną walidacją, bezpieczeństwem i wydajnością.
    """
    
    # STAŁE KONFIGURACYJNE - wyekstraktowane z hardcoded values
    ASSET_EXTENSION = '.asset'
    CACHE_FOLDER_NAME = '.cache'
    THUMB_EXTENSION = '.thumb'
    CACHE_TTL_SECONDS = 30  # TTL dla cache wyników analizy
    
    # Obsługiwane rozszerzenia jako sets dla O(1) lookup
    ARCHIVE_EXTENSIONS: Set[str] = {'.rar', '.zip', '.sbsar'}
    IMAGE_EXTENSIONS: Set[str] = {'.jpg', '.png', '.jpeg', '.gif', '.webp'}
    
    # Cache dla wyników analizy folderów
    _analysis_cache: Dict[str, tuple] = {}
    
    @staticmethod
    def _validate_folder_path(folder_path: str) -> str:
        """
        Waliduje i normalizuje ścieżkę folderu z protection przeciwko path traversal
        
        Args:
            folder_path (str): Ścieżka do walidacji
            
        Returns:
            str: Znormalizowana i bezpieczna ścieżka
            
        Raises:
            ValueError: Gdy ścieżka jest nieprawidłowa lub niebezpieczna
        """
        if not folder_path:
            raise ValueError("Folder path cannot be empty or None")
            
        if not isinstance(folder_path, str):
            raise ValueError(f"Folder path must be string, got {type(folder_path)}")
        
        # Normalizacja ścieżki i resolving symbolic links
        try:
            normalized_path = Path(folder_path).resolve()
        except (OSError, ValueError) as e:
            raise ValueError(f"Invalid folder path: {e}")
        
        # Basic security check - sprawdź czy ścieżka nie zawiera podejrzanych sekwencji
        path_str = str(normalized_path)
        if '..' in path_str or path_str.startswith('/proc') or path_str.startswith('/sys'):
            raise ValueError(f"Potentially unsafe path: {path_str}")
        
        # Sprawdź czy to jest folder (nie plik)
        if normalized_path.exists() and not normalized_path.is_dir():
            raise ValueError(f"Path is not a directory: {path_str}")
            
        return str(normalized_path)

    @staticmethod
    def _get_cached_analysis(folder_path: str) -> Dict:
        """
        Pobiera cached wynik analizy folderu jeśli jest aktualny
        
        Args:
            folder_path (str): Ścieżka folderu
            
        Returns:
            Dict: Cached wynik lub None jeśli cache invalid/expired
        """
        cache_key = folder_path
        if cache_key in FolderClickRules._analysis_cache:
            cached_result, timestamp = FolderClickRules._analysis_cache[cache_key]
            if time.time() - timestamp < FolderClickRules.CACHE_TTL_SECONDS:
                logger.debug(f"Cache hit for folder analysis: {folder_path}")
                return cached_result
            else:
                # Expired cache entry
                del FolderClickRules._analysis_cache[cache_key]
                logger.debug(f"Cache expired for folder: {folder_path}")
        
        return None

    @staticmethod
    def _cache_analysis_result(folder_path: str, result: Dict) -> None:
        """
        Cache'uje wynik analizy folderu
        
        Args:
            folder_path (str): Ścieżka folderu
            result (Dict): Wynik analizy do cache'owania
        """
        cache_key = folder_path
        FolderClickRules._analysis_cache[cache_key] = (result, time.time())
        logger.debug(f"Cached analysis result for: {folder_path}")
```

---

### PATCH 2: OPTYMALIZACJA ANALYZE_FOLDER_CONTENT

**Problem:** Nieefektywne operacje I/O i string processing w pętlach
**Rozwiązanie:** Zoptymalizowana analiza z sets lookup i reduced I/O calls

```python
    @staticmethod
    def analyze_folder_content(folder_path: str) -> Dict:
        """
        Analizuje zawartość folderu z ulepszoną wydajnością i cache'owaniem
        
        Args:
            folder_path (str): Ścieżka do folderu do analizy
            
        Returns:
            Dict: Szczegółowe informacje o zawartości folderu
        """
        try:
            # Walidacja i normalizacja input
            validated_path = FolderClickRules._validate_folder_path(folder_path)
            
            # Sprawdź cache
            cached_result = FolderClickRules._get_cached_analysis(validated_path)
            if cached_result is not None:
                return cached_result
            
            # Sprawdź czy folder istnieje (atomic operation)
            try:
                items = os.listdir(validated_path)
            except FileNotFoundError:
                result = {
                    "error": f"Folder does not exist: {validated_path}",
                    "asset_files": [],
                    "preview_archive_files": [],
                    "cache_exists": False,
                    "cache_thumb_count": 0,
                    "asset_count": 0,
                    "preview_archive_count": 0,
                }
                FolderClickRules._cache_analysis_result(validated_path, result)
                return result
            except PermissionError:
                result = {
                    "error": f"Permission denied accessing folder: {validated_path}",
                    "asset_files": [],
                    "preview_archive_files": [],
                    "cache_exists": False,
                    "cache_thumb_count": 0,
                    "asset_count": 0,
                    "preview_archive_count": 0,
                }
                FolderClickRules._cache_analysis_result(validated_path, result)
                return result

            # Inicjalizacja list wyników
            asset_files = []
            preview_archive_files = []

            # Optymalizowana kategoryzacja plików - single pass przez items
            for item in items:
                # Pomijamy ukryte pliki i cache folder
                if item.startswith('.'):
                    continue
                    
                # Single .lower() call per item
                item_lower = item.lower()
                
                # O(1) lookup w sets zamiast multiple string comparisons
                if item_lower.endswith(FolderClickRules.ASSET_EXTENSION):
                    asset_files.append(item)
                else:
                    # Sprawdź extension against sets
                    item_ext = Path(item_lower).suffix
                    if item_ext in FolderClickRules.ARCHIVE_EXTENSIONS or item_ext in FolderClickRules.IMAGE_EXTENSIONS:
                        preview_archive_files.append(item)

            # Sprawdź cache folder - single operation
            cache_folder_path = os.path.join(validated_path, FolderClickRules.CACHE_FOLDER_NAME)
            cache_exists = False
            cache_thumb_count = 0
            
            try:
                if os.path.isdir(cache_folder_path):
                    cache_exists = True
                    cache_items = os.listdir(cache_folder_path)
                    # Optimized counting - single pass
                    cache_thumb_count = sum(1 for item in cache_items 
                                          if item.lower().endswith(FolderClickRules.THUMB_EXTENSION))
            except (OSError, PermissionError) as e:
                logger.debug(f"Error checking cache folder {cache_folder_path}: {e}")
                cache_exists = False
                cache_thumb_count = 0

            # Prepare result
            result = {
                "asset_files": asset_files,
                "preview_archive_files": preview_archive_files,
                "cache_exists": cache_exists,
                "cache_thumb_count": cache_thumb_count,
                "asset_count": len(asset_files),
                "preview_archive_count": len(preview_archive_files),
            }
            
            # Cache the result
            FolderClickRules._cache_analysis_result(validated_path, result)
            
            logger.debug(f"Analyzed folder: {validated_path} | "
                        f"Assets: {len(asset_files)} | "
                        f"Archives/Images: {len(preview_archive_files)} | "
                        f"Cache: {cache_exists} | Thumbs: {cache_thumb_count}")
            
            return result

        except ValueError as e:
            # Input validation errors
            logger.error(f"Validation error for folder {folder_path}: {e}")
            return {
                "error": f"Validation error: {e}",
                "asset_files": [],
                "preview_archive_files": [],
                "cache_exists": False,
                "cache_thumb_count": 0,
                "asset_count": 0,
                "preview_archive_count": 0,
            }
        except Exception as e:
            # Unexpected errors
            logger.error(f"Unexpected error analyzing folder {folder_path}: {e}")
            return {
                "error": f"Analysis error: {e}",
                "asset_files": [],
                "preview_archive_files": [],
                "cache_exists": False,
                "cache_thumb_count": 0,
                "asset_count": 0,
                "preview_archive_count": 0,
            }
```

---

### PATCH 3: REFAKTORYZACJA DECIDE_ACTION - PODZIAŁ NA MNIEJSZE METODY

**Problem:** Monolityczna metoda 280+ linii trudna do testowania i debugowania
**Rozwiązanie:** Podział na logiczne komponenty z jasną separation of concerns

```python
    @staticmethod
    def _assess_folder_state(content: Dict) -> str:
        """
        Ocenia stan folderu na podstawie zawartości
        
        Args:
            content (Dict): Wynik analizy zawartości folderu
            
        Returns:
            str: Stan folderu ('empty', 'archives_only', 'assets_only', 'mixed', 'error')
        """
        if "error" in content:
            return "error"
            
        asset_count = content["asset_count"]
        preview_archive_count = content["preview_archive_count"]
        
        if asset_count == 0 and preview_archive_count == 0:
            return "empty"
        elif asset_count == 0 and preview_archive_count > 0:
            return "archives_only"
        elif asset_count > 0 and preview_archive_count == 0:
            return "assets_only"
        else:
            return "mixed"

    @staticmethod
    def _check_cache_validity(content: Dict) -> Dict:
        """
        Sprawdza czy cache jest prawidłowy i synchroniczny z assetami
        
        Args:
            content (Dict): Wynik analizy zawartości folderu
            
        Returns:
            Dict: Status cache z detailed info
        """
        cache_exists = content["cache_exists"]
        cache_thumb_count = content["cache_thumb_count"]
        asset_count = content["asset_count"]
        
        if not cache_exists:
            return {
                "valid": False,
                "reason": "cache_missing",
                "message": "Cache folder does not exist"
            }
        
        if cache_thumb_count != asset_count:
            return {
                "valid": False,
                "reason": "count_mismatch",
                "message": f"Thumbnail count ({cache_thumb_count}) != asset count ({asset_count})"
            }
        
        return {
            "valid": True,
            "reason": "synchronized",
            "message": f"Cache synchronized: {cache_thumb_count} thumbnails for {asset_count} assets"
        }

    @staticmethod
    def _make_decision_archives_only(content: Dict) -> Dict:
        """
        Podejmuje decyzję dla folderu zawierającego tylko archiwa/obrazy (bez assets)
        
        Args:
            content (Dict): Wynik analizy zawartości folderu
            
        Returns:
            Dict: Decyzja z detailed reasoning
        """
        return {
            "action": "run_scanner",
            "message": "Archives/images found but no assets - running scanner to create assets",
            "condition": "archives_only_case",
            "details": {
                "preview_archive_count": content["preview_archive_count"],
                "asset_count": content["asset_count"],
                "reasoning": "Scanner needed to process archives into asset files"
            },
        }

    @staticmethod  
    def _make_decision_assets_only(content: Dict) -> Dict:
        """
        Podejmuje decyzję dla folderu zawierającego tylko assety (bez archiwów)
        
        Args:
            content (Dict): Wynik analizy zawartości folderu
            
        Returns:
            Dict: Decyzja z detailed reasoning
        """
        cache_status = FolderClickRules._check_cache_validity(content)
        
        if cache_status["valid"]:
            return {
                "action": "show_gallery",
                "message": f"Assets ready with valid cache - showing gallery ({content['asset_count']} assets)",
                "condition": "assets_only_ready",
                "details": {
                    "asset_count": content["asset_count"],
                    "cache_thumb_count": content["cache_thumb_count"],
                    "reasoning": "All assets have thumbnails, ready for gallery display"
                },
            }
        else:
            return {
                "action": "run_scanner", 
                "message": f"Assets found but {cache_status['reason']} - running scanner",
                "condition": "assets_only_cache_invalid",
                "details": {
                    "asset_count": content["asset_count"],
                    "cache_exists": content["cache_exists"],
                    "cache_thumb_count": content["cache_thumb_count"],
                    "reasoning": cache_status["message"]
                },
            }

    @staticmethod
    def _make_decision_mixed_content(content: Dict) -> Dict:
        """
        Podejmuje decyzję dla folderu z mixed content (assety + archiwa)
        
        Args:
            content (Dict): Wynik analizy zawartości folderu
            
        Returns:
            Dict: Decyzja z detailed reasoning
        """
        cache_status = FolderClickRules._check_cache_validity(content)
        
        if cache_status["valid"]:
            return {
                "action": "show_gallery",
                "message": f"Mixed content ready - showing gallery ({content['asset_count']} assets)",
                "condition": "mixed_content_ready", 
                "details": {
                    "preview_archive_count": content["preview_archive_count"],
                    "asset_count": content["asset_count"],
                    "cache_thumb_count": content["cache_thumb_count"],
                    "reasoning": "Assets and cache synchronized, ready for display"
                },
            }
        else:
            return {
                "action": "run_scanner",
                "message": f"Mixed content but {cache_status['reason']} - running scanner",
                "condition": "mixed_content_cache_invalid",
                "details": {
                    "preview_archive_count": content["preview_archive_count"],
                    "asset_count": content["asset_count"],
                    "cache_exists": content["cache_exists"],
                    "cache_thumb_count": content["cache_thumb_count"],
                    "reasoning": cache_status["message"]
                },
            }
```

---

### PATCH 4: ZOPTYMALIZOWANA GŁÓWNA METODA DECIDE_ACTION

**Problem:** Złożona logika decyzyjna i nadmierne logowanie INFO
**Rozwiązanie:** Wykorzystanie helper methods i optimized logging

```python
    @staticmethod
    def decide_action(folder_path: str) -> Dict:
        """
        Podejmuje decyzję o akcji na podstawie zawartości folderu
        Zrefaktoryzowana wersja z improved modularity i performance
        
        Args:
            folder_path (str): Ścieżka do folderu do analizy
            
        Returns:
            Dict: Słownik zawierający decyzję z detailed reasoning
        """
        try:
            # Step 1: Analyze folder content (with caching)
            content = FolderClickRules.analyze_folder_content(folder_path)
            
            # Step 2: Handle errors early
            if "error" in content:
                logger.error(f"Folder analysis failed: {folder_path} - {content['error']}")
                return {
                    "action": "error",
                    "message": content["error"],
                    "condition": "analysis_error",
                    "details": {"folder_path": folder_path}
                }

            # Step 3: Assess folder state
            folder_state = FolderClickRules._assess_folder_state(content)
            
            # Step 4: Make decision based on state using helper methods
            if folder_state == "empty":
                logger.debug(f"Empty folder detected: {folder_path}")
                return {
                    "action": "no_action",
                    "message": "Folder contains no relevant files",
                    "condition": "empty_folder",
                    "details": {
                        "asset_count": 0,
                        "preview_archive_count": 0,
                        "reasoning": "No assets, archives, or images found"
                    },
                }
            
            elif folder_state == "archives_only":
                decision = FolderClickRules._make_decision_archives_only(content)
                logger.info(f"DECISION: {folder_path} -> {decision['action']} (archives only)")
                return decision
                
            elif folder_state == "assets_only":
                decision = FolderClickRules._make_decision_assets_only(content)
                logger.info(f"DECISION: {folder_path} -> {decision['action']} (assets only)")
                return decision
                
            elif folder_state == "mixed":
                decision = FolderClickRules._make_decision_mixed_content(content)
                logger.info(f"DECISION: {folder_path} -> {decision['action']} (mixed content)")
                return decision
                
            else:
                # Fallback case
                logger.warning(f"Unexpected folder state: {folder_state} for {folder_path}")
                return {
                    "action": "no_action",
                    "message": f"Unexpected folder state: {folder_state}",
                    "condition": "unexpected_state",
                    "details": content
                }
                
        except Exception as e:
            error_msg = f"Decision making failed for folder {folder_path}: {e}"
            logger.error(error_msg)
            return {
                "action": "error", 
                "message": error_msg, 
                "condition": "decision_error",
                "details": {"folder_path": folder_path, "exception": str(e)}
            }

    @staticmethod
    def clear_cache() -> None:
        """
        Czyści cache analizy folderów - useful for testing lub manual refresh
        """
        FolderClickRules._analysis_cache.clear()
        logger.debug("Folder analysis cache cleared")

    @staticmethod 
    def get_cache_stats() -> Dict:
        """
        Zwraca statystyki cache dla monitoring i debugging
        
        Returns:
            Dict: Cache statistics
        """
        current_time = time.time()
        valid_entries = 0
        expired_entries = 0
        
        for cache_key, (result, timestamp) in FolderClickRules._analysis_cache.items():
            if current_time - timestamp < FolderClickRules.CACHE_TTL_SECONDS:
                valid_entries += 1
            else:
                expired_entries += 1
                
        return {
            "total_entries": len(FolderClickRules._analysis_cache),
            "valid_entries": valid_entries,
            "expired_entries": expired_entries,
            "cache_ttl_seconds": FolderClickRules.CACHE_TTL_SECONDS
        }
```

---

## ✅ CHECKLISTA WERYFIKACYJNA (DO WYPEŁNIENIA PRZED WDROŻENIEM)

#### **FUNKCJONALNOŚCI DO WERYFIKACJI:**

- [ ] **Funkcjonalność podstawowa** - wszystkie decision flows działają identycznie jak wcześniej
- [ ] **API kompatybilność** - publiczne metody zachowują identyczne sygnatury i return types
- [ ] **Obsługa błędów** - improved error handling z specific exceptions
- [ ] **Walidacja danych** - comprehensive input validation z security checks
- [ ] **Logowanie** - optimized logging (DEBUG dla szczegółów, INFO dla decyzji)
- [ ] **Konfiguracja** - constants wyekstraktowane do class-level configuration
- [ ] **Cache** - nowy cache system działa poprawnie z TTL expiration
- [ ] **Thread safety** - static methods remain thread-safe, cache access properly handled
- [ ] **Memory management** - cache ma proper cleanup i nie powoduje memory leaks
- [ ] **Performance** - minimum 20% improvement w typical folder analysis scenarios

#### **ZALEŻNOŚCI DO WERYFIKACJI:**

- [ ] **Importy** - wszystkie importy działają (logging, os, pathlib, functools, time, typing)
- [ ] **Zależności zewnętrzne** - compatible z Python stdlib wymaganiami
- [ ] **Zależności wewnętrzne** - folder_scanner_worker.py integration działa bez zmian
- [ ] **Cykl zależności** - brak nowych circular dependencies
- [ ] **Backward compatibility** - 100% compatible API dla existing callers
- [ ] **Interface contracts** - wszystkie return value structures zachowane
- [ ] **Event handling** - decision results properly handled przez UI components
- [ ] **Signal/slot connections** - Qt integration remains functional 
- [ ] **File I/O** - all file operations properly secured przeciwko path traversal

#### **TESTY WERYFIKACYJNE:**

- [ ] **Test jednostkowy** - each helper method works in isolation
- [ ] **Test integracyjny** - full workflow od folder click do decision works
- [ ] **Test regresyjny** - wszystkie existing behaviors preserved
- [ ] **Test wydajnościowy** - performance improvement verified (20%+ faster)
- [ ] **Test bezpieczeństwa** - path traversal protection works, no security regressions
- [ ] **Test cache** - cache TTL works, cache invalidation proper, memory usage controlled
- [ ] **Test edge cases** - empty folders, permission errors, malformed paths handled gracefully
- [ ] **Test concurrent access** - multiple simultaneous folder analyses work correctly

#### **SPECIFIC RULES.PY VERIFICATION:**

- [ ] **Decision logic preserved** - wszystkie warunki (warunek_1, warunek_2a-2c, dodatkowe) work identically  
- [ ] **Error messages consistent** - existing error handling behavior maintained
- [ ] **Cache synchronization** - thumbnail count vs asset count logic preserved
- [ ] **File extension handling** - wszystkie supported formats (.asset, .rar, .zip, .sbsar, .jpg, .png, etc.) recognized
- [ ] **Folder structure analysis** - .cache folder detection i validation works
- [ ] **Logging output compatible** - existing log parsing tools still work
- [ ] **Performance critical paths** - folder clicking responsiveness improved
- [ ] **Memory usage optimized** - reduced string operations, single-pass algorithms effective

#### **KRYTERIA SUKCESU:**

- [ ] **WSZYSTKIE CHECKLISTY MUSZĄ BYĆ ZAZNACZONE** przed wdrożeniem
- [ ] **BRAK FAILED TESTS** - wszystkie testy muszą przejść z PASS
- [ ] **PERFORMANCE BUDGET** - minimum 20% improvement w folder analysis speed
- [ ] **SECURITY REQUIREMENTS** - path traversal protection verified i functional
- [ ] **MEMORY BUDGET** - cache memory usage controlled, no memory leaks detected
- [ ] **BACKWARD COMPATIBILITY** - 100% compatible z existing folder_scanner_worker.py calls