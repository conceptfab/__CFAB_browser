#!/usr/bin/env python3
"""
Rules - Logika decyzyjna dla obsługi kliknięć w foldery

Ten moduł zawiera klasę FolderClickRules, która implementuje logikę decyzyjną
dla aplikacji CFAB Browser. Klasa analizuje zawartość folderów i podejmuje
decyzje o tym, czy uruchomić scanner do przetwarzania plików, czy wyświetlić
galerię gotowych assetów.

Główne funkcjonalności:
- Analiza zawartości folderu (pliki asset, archiwa, podglądy)
- Sprawdzanie istnienia i zawartości folderu .cache
- Podejmowanie decyzji o akcji na podstawie stanu folderu
- Obsługa różnych scenariuszy (brak plików, niekompletne cache, gotowe assety)

Autor: CFAB Browser Team
Data: 2025
"""

import logging
import os
import re
import time
from typing import Dict, Optional, Set

logger = logging.getLogger(__name__)


class FolderClickRules:
    """
    Klasa zawierająca logikę decyzyjną dla kliknięć w foldery

    Ta klasa implementuje algorytm decyzyjny, który analizuje zawartość folderu
    i podejmuje decyzję o tym, jaką akcję wykonać:

    - Uruchomić scanner (gdy brak plików asset lub niekompletne cache)
    - Wyświetlić galerię (gdy wszystko jest gotowe)
    - Nie wykonać żadnej akcji (gdy folder nie zawiera odpowiednich plików)

    Klasa obsługuje następujące typy plików:
    - Pliki .asset - główne pliki assetów
    - Pliki archiwalne (.rar, .zip, .sbsar) - źródła do przetwarzania
    - Pliki podglądów (.jpg, .png, .jpeg, .gif) - obrazy podglądowe
    - Folder .cache - cache z wygenerowanymi miniaturami
    """

    # Stałe konfiguracyjne
    CACHE_FOLDER_NAME = ".cache"
    THUMB_EXTENSION = ".thumb"

    # Zbiory rozszerzeń plików dla efektywnego lookup
    ASSET_EXTENSIONS: Set[str] = {".asset"}
    ARCHIVE_EXTENSIONS: Set[str] = {".rar", ".zip", ".sbsar", ".7z"}
    PREVIEW_EXTENSIONS: Set[str] = {".jpg", ".jpeg", ".png",".webp", ".gif"}

    # Cache TTL (Time To Live) w sekundach
    CACHE_TTL = 300  # 5 minut

    # Cache dla wyników analizy folderów
    _folder_analysis_cache: Dict[str, Dict] = {}
    _cache_timestamps: Dict[str, float] = {}

    @staticmethod
    def _validate_folder_path(folder_path: str) -> Optional[str]:
        """
        Waliduje ścieżkę folderu pod kątem bezpieczeństwa

        Args:
            folder_path (str): Ścieżka do walidacji

        Returns:
            Optional[str]: Komunikat błędu lub None jeśli ścieżka jest poprawna
        """
        if not folder_path:
            return "Ścieżka folderu nie może być pusta"

        if not isinstance(folder_path, str):
            return "Ścieżka folderu musi być stringiem"

        # Sprawdź czy ścieżka nie zawiera sekwencji path traversal
        if ".." in folder_path or "\\.." in folder_path or "/.." in folder_path:
            return "Ścieżka zawiera niedozwolone sekwencje path traversal"

        # Sprawdź czy ścieżka nie jest zbyt długa
        if len(folder_path) > 4096:
            return "Ścieżka folderu jest zbyt długa"

        # Sprawdź czy ścieżka nie zawiera niedozwolonych znaków
        # Uwaga: dwukropek (:) jest dozwolony w Windows (C:\)
        invalid_chars = re.search(r'[<>"|?*]', folder_path)
        if invalid_chars:
            return f"Ścieżka zawiera niedozwolone znaki: " f"{invalid_chars.group()}"

        return None

    @staticmethod
    def _is_cache_valid(folder_path: str) -> bool:
        """
        Sprawdza czy cache dla folderu jest aktualny

        Args:
            folder_path (str): Ścieżka do folderu

        Returns:
            bool: True jeśli cache jest aktualny
        """
        if folder_path not in FolderClickRules._cache_timestamps:
            return False

        current_time = time.time()
        cache_time = FolderClickRules._cache_timestamps[folder_path]

        return (current_time - cache_time) < FolderClickRules.CACHE_TTL

    @staticmethod
    def _get_cached_analysis(folder_path: str) -> Optional[Dict]:
        """
        Pobiera zcache'owaną analizę folderu

        Args:
            folder_path (str): Ścieżka do folderu

        Returns:
            Optional[Dict]: Zcache'owana analiza lub None
        """
        if (
            folder_path in FolderClickRules._folder_analysis_cache
            and FolderClickRules._is_cache_valid(folder_path)
        ):
            logger.debug(f"Cache hit dla folderu: {folder_path}")
            return FolderClickRules._folder_analysis_cache[folder_path]

        return None

    @staticmethod
    def _cache_analysis(folder_path: str, analysis: Dict) -> None:
        """
        Zapisuje analizę folderu do cache

        Args:
            folder_path (str): Ścieżka do folderu
            analysis (Dict): Wynik analizy do zcache'owania
        """
        FolderClickRules._folder_analysis_cache[folder_path] = analysis
        FolderClickRules._cache_timestamps[folder_path] = time.time()
        logger.debug(f"Zcache'owano analizę folderu: {folder_path}")

    @staticmethod
    def _categorize_file(item: str) -> Optional[str]:
        """
        Kategoryzuje plik na podstawie rozszerzenia

        Args:
            item (str): Nazwa pliku

        Returns:
            Optional[str]: Kategoria pliku lub None jeśli nie pasuje
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
        Analizuje zawartość folderu cache i zwraca liczbę miniaturek

        Args:
            cache_folder_path (str): Ścieżka do folderu cache

        Returns:
            int: Liczba plików miniaturek
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
            logger.warning(f"Błąd sprawdzania .cache: {e}")
            return 0

    @staticmethod
    def _create_error_result(error_message: str) -> dict:
        """
        Pomocnicza metoda do generowania słownika błędu dla analyze_folder_content

        Args:
            error_message (str): Treść komunikatu błędu

        Returns:
            dict: Słownik z informacjami o błędzie
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
        Analizuje zawartość folderu i zwraca szczegółowe informacje o plikach

        Metoda skanuje folder w poszukiwaniu różnych typów plików:
        - Pliki .asset (główne pliki assetów)
        - Pliki archiwalne (.rar, .zip, .sbsar)
        - Pliki podglądów (.jpg, .png, .jpeg, .gif)
        - Folder .cache z miniaturami

        Args:
            folder_path (str): Ścieżka do folderu do analizy

        Returns:
            dict: Słownik zawierający:
                - asset_files: lista plików .asset
                - preview_archive_files: lista plików archiwalnych i podglądów
                - cache_exists: czy istnieje folder .cache
                - cache_thumb_count: liczba plików miniaturek w .cache
                - asset_count: liczba plików asset
                - preview_archive_count: liczba plików archiwalnych/podglądów
                - error: komunikat błędu (jeśli wystąpił)

        Przykład zwracanego słownika:
        {
            "asset_files": ["model.asset", "texture.asset"],
            "preview_archive_files": ["model.zip", "preview.jpg"],
            "cache_exists": True,
            "cache_thumb_count": 2,
            "asset_count": 2,
            "preview_archive_count": 2
        }
        """
        # Sprawdź cache
        cached_result = FolderClickRules._get_cached_analysis(folder_path)
        if cached_result:
            return cached_result

        # Walidacja input
        validation_error = FolderClickRules._validate_folder_path(folder_path)
        if validation_error:
            return FolderClickRules._create_error_result(validation_error)

        try:
            # Sprawdź czy folder istnieje
            if not os.path.exists(folder_path):
                return FolderClickRules._create_error_result(
                    f"Folder nie istnieje: {folder_path}"
                )

            # Pobierz listę wszystkich elementów w folderze
            try:
                items = os.listdir(folder_path)
            except (OSError, PermissionError) as e:
                return FolderClickRules._create_error_result(
                    f"Brak uprawnień do odczytu folderu: {e}"
                )

            # Kategoryzuj pliki według typów
            asset_files = []
            preview_archive_files = []

            for item in items:
                category = FolderClickRules._categorize_file(item)
                if category == "asset":
                    asset_files.append(item)
                elif category in ("archive", "preview"):
                    preview_archive_files.append(item)

            # Sprawdź istnienie i zawartość folderu .cache
            cache_folder_path = os.path.join(
                folder_path, FolderClickRules.CACHE_FOLDER_NAME
            )
            cache_exists = os.path.exists(cache_folder_path) and os.path.isdir(
                cache_folder_path
            )

            # Policz pliki miniaturek w folderze .cache
            cache_thumb_count = FolderClickRules._analyze_cache_folder(
                cache_folder_path
            )

            # Przygotuj wynik
            result = {
                "asset_files": asset_files,
                "preview_archive_files": preview_archive_files,
                "cache_exists": cache_exists,
                "cache_thumb_count": cache_thumb_count,
                "asset_count": len(asset_files),
                "preview_archive_count": len(preview_archive_files),
            }

            # Zcache'uj wynik
            FolderClickRules._cache_analysis(folder_path, result)

            return result

        except Exception as e:
            logger.error(f"Błąd analizy zawartości folderu {folder_path}: {e}")
            return FolderClickRules._create_error_result(f"Błąd analizy folderu: {e}")

    @staticmethod
    def _log_folder_analysis(folder_path: str, content: Dict) -> None:
        """
        Loguje informacje o analizie folderu na poziomie DEBUG

        Args:
            folder_path (str): Ścieżka do folderu
            content (Dict): Wynik analizy folderu
        """
        logger.debug(
            f"ANALIZA FOLDERU: {folder_path} | "
            f"Asset: {content.get('asset_count', 0)} | "
            f"Podglądy/Archiwa: {content.get('preview_archive_count', 0)} | "
            f"Cache: {'TAK' if content.get('cache_exists', False) else 'NIE'} | "
            f"Miniatury: {content.get('cache_thumb_count', 0)}"
        )

    @staticmethod
    def _handle_condition_1(folder_path: str, content: Dict) -> Dict:
        """
        Obsługuje warunek 1: Folder zawiera pliki archiwalne/podglądy,
        ale NIE ma plików asset

        Args:
            folder_path (str): Ścieżka do folderu
            content (Dict): Wynik analizy folderu

        Returns:
            Dict: Decyzja dla warunku 1
        """
        asset_count = content["asset_count"]
        preview_archive_count = content["preview_archive_count"]

        logger.debug(
            f"PRZYPADEK 1 WYKRYTY: {folder_path} | "
            f"Pliki archiwalne/podglądy: {preview_archive_count} | "
            f"Pliki asset: {asset_count} | "
            f"DECYZJA: Uruchamiam scanner (brak plików asset)"
        )

        return {
            "action": "run_scanner",
            "message": "Brak plików asset - uruchamiam scanner",
            "condition": "warunek_1",
            "details": {
                "preview_archive_count": preview_archive_count,
                "asset_count": asset_count,
            },
        }

    @staticmethod
    def _handle_condition_2a(folder_path: str, content: Dict) -> Dict:
        """
        Obsługuje warunek 2a: Brak folderu .cache

        Args:
            folder_path (str): Ścieżka do folderu
            content (Dict): Wynik analizy folderu

        Returns:
            Dict: Decyzja dla warunku 2a
        """
        asset_count = content["asset_count"]
        preview_archive_count = content["preview_archive_count"]

        logger.debug(
            f"PRZYPADEK 2A WYKRYTY: {folder_path} | "
            f"Pliki archiwalne/podglądy: {preview_archive_count} | "
            f"Pliki asset: {asset_count} | "
            f"Cache: NIE | "
            f"DECYZJA: Uruchamiam scanner (brak folderu .cache)"
        )

        return {
            "action": "run_scanner",
            "message": "Brak folderu .cache - uruchamiam scanner",
            "condition": "warunek_2a",
            "details": {
                "preview_archive_count": preview_archive_count,
                "asset_count": asset_count,
                "cache_exists": False,
            },
        }

    @staticmethod
    def _handle_condition_2b(folder_path: str, content: Dict) -> Dict:
        """
        Obsługuje warunek 2b: .cache istnieje, ale liczba miniaturek ≠
        liczba assetów

        Args:
            folder_path (str): Ścieżka do folderu
            content (Dict): Wynik analizy folderu

        Returns:
            Dict: Decyzja dla warunku 2b
        """
        asset_count = content["asset_count"]
        preview_archive_count = content["preview_archive_count"]
        cache_thumb_count = content["cache_thumb_count"]

        logger.debug(
            f"PRZYPADEK 2B WYKRYTY: {folder_path} | "
            f"Pliki archiwalne/podglądy: {preview_archive_count} | "
            f"Pliki asset: {asset_count} | "
            f"Cache: TAK | "
            f"Miniatury: {cache_thumb_count} | "
            f"DECYZJA: Uruchamiam scanner (niezgodna liczba miniaturek)"
        )

        return {
            "action": "run_scanner",
            "message": (
                f"Niezgodna liczba miniaturek ({cache_thumb_count}) "
                f"i assetów ({asset_count}) - uruchamiam scanner"
            ),
            "condition": "warunek_2b",
            "details": {
                "preview_archive_count": preview_archive_count,
                "asset_count": asset_count,
                "cache_exists": True,
                "cache_thumb_count": cache_thumb_count,
            },
        }

    @staticmethod
    def _handle_condition_2c(folder_path: str, content: Dict) -> Dict:
        """
        Obsługuje warunek 2c: .cache istnieje i liczba miniaturek =
        liczba assetów

        Args:
            folder_path (str): Ścieżka do folderu
            content (Dict): Wynik analizy folderu

        Returns:
            Dict: Decyzja dla warunku 2c
        """
        asset_count = content["asset_count"]
        preview_archive_count = content["preview_archive_count"]
        cache_thumb_count = content["cache_thumb_count"]

        logger.debug(
            f"PRZYPADEK 2C WYKRYTY: {folder_path} | "
            f"Pliki archiwalne/podglądy: {preview_archive_count} | "
            f"Pliki asset: {asset_count} | "
            f"Cache: TAK | "
            f"Miniatury: {cache_thumb_count} | "
            f"DECYZJA: Wyświetlam galerię (wszystko gotowe)"
        )

        return {
            "action": "show_gallery",
            "message": (
                f"Wszystko gotowe - wyświetlam galerię "
                f"(thumb: {cache_thumb_count}, asset: {asset_count})"
            ),
            "condition": "warunek_2c",
            "details": {
                "preview_archive_count": preview_archive_count,
                "asset_count": asset_count,
                "cache_exists": True,
                "cache_thumb_count": cache_thumb_count,
            },
        }

    @staticmethod
    def _handle_additional_case_no_cache(folder_path: str, content: Dict) -> Dict:
        """
        Obsługuje dodatkowy przypadek: Tylko pliki asset, brak .cache

        Args:
            folder_path (str): Ścieżka do folderu
            content (Dict): Wynik analizy folderu

        Returns:
            Dict: Decyzja dla tego przypadku
        """
        asset_count = content["asset_count"]
        preview_archive_count = content["preview_archive_count"]

        logger.debug(
            f"PRZYPADEK DODATKOWY (BRAK CACHE): {folder_path} | "
            f"Pliki asset: {asset_count} | "
            f"Pliki archiwalne/podglądy: {preview_archive_count} | "
            f"Cache: NIE | "
            f"DECYZJA: Uruchamiam scanner (tylko asset, brak .cache)"
        )

        return {
            "action": "run_scanner",
            "message": ("Tylko pliki asset, brak .cache - uruchamiam scanner"),
            "condition": "dodatkowy_brak_cache",
            "details": {
                "asset_count": asset_count,
                "preview_archive_count": preview_archive_count,
                "cache_exists": False,
            },
        }

    @staticmethod
    def _handle_additional_case_mismatch(folder_path: str, content: Dict) -> Dict:
        """
        Obsługuje dodatkowy przypadek: Tylko pliki asset,
        niezgodna liczba miniaturek

        Args:
            folder_path (str): Ścieżka do folderu
            content (Dict): Wynik analizy folderu

        Returns:
            Dict: Decyzja dla tego przypadku
        """
        asset_count = content["asset_count"]
        preview_archive_count = content["preview_archive_count"]
        cache_thumb_count = content["cache_thumb_count"]

        logger.debug(
            f"PRZYPADEK DODATKOWY (NIEZGODNA LICZBA): {folder_path} | "
            f"Pliki asset: {asset_count} | "
            f"Pliki archiwalne/podglądy: {preview_archive_count} | "
            f"Cache: TAK | "
            f"Miniatury: {cache_thumb_count} | "
            f"DECYZJA: Uruchamiam scanner (niezgodna liczba miniaturek)"
        )

        return {
            "action": "run_scanner",
            "message": (
                f"Tylko pliki asset, niezgodna liczba miniaturek "
                f"({cache_thumb_count}) i assetów ({asset_count}) - "
                f"uruchamiam scanner"
            ),
            "condition": "dodatkowy_niezgodna_liczba",
            "details": {
                "asset_count": asset_count,
                "preview_archive_count": preview_archive_count,
                "cache_exists": True,
                "cache_thumb_count": cache_thumb_count,
            },
        }

    @staticmethod
    def _handle_additional_case_ready(folder_path: str, content: Dict) -> Dict:
        """
        Obsługuje dodatkowy przypadek: Tylko pliki asset, wszystko gotowe

        Args:
            folder_path (str): Ścieżka do folderu
            content (Dict): Wynik analizy folderu

        Returns:
            Dict: Decyzja dla tego przypadku
        """
        asset_count = content["asset_count"]
        preview_archive_count = content["preview_archive_count"]
        cache_thumb_count = content["cache_thumb_count"]

        logger.debug(
            f"PRZYPADEK DODATKOWY (GOTOWE): {folder_path} | "
            f"Pliki asset: {asset_count} | "
            f"Pliki archiwalne/podglądy: {preview_archive_count} | "
            f"Cache: TAK | "
            f"Miniatury: {cache_thumb_count} | "
            f"DECYZJA: Wyświetlam galerię (wszystko gotowe)"
        )

        return {
            "action": "show_gallery",
            "message": (
                f"Tylko pliki asset, wszystko gotowe - "
                f"wyświetlam galerię (thumb: {cache_thumb_count}, "
                f"asset: {asset_count})"
            ),
            "condition": "dodatkowy_gotowe",
            "details": {
                "asset_count": asset_count,
                "preview_archive_count": preview_archive_count,
                "cache_exists": True,
                "cache_thumb_count": cache_thumb_count,
            },
        }

    @staticmethod
    def _handle_default_case(folder_path: str, content: Dict) -> Dict:
        """
        Obsługuje przypadek domyślny: Folder nie zawiera odpowiednich plików

        Args:
            folder_path (str): Ścieżka do folderu
            content (Dict): Wynik analizy folderu

        Returns:
            Dict: Decyzja dla przypadku domyślnego
        """
        asset_count = content["asset_count"]
        preview_archive_count = content["preview_archive_count"]
        cache_exists = content["cache_exists"]
        cache_thumb_count = content["cache_thumb_count"]

        logger.debug(
            f"PRZYPADEK DOMYŚLNY: {folder_path} | "
            f"Pliki asset: {asset_count} | "
            f"Pliki archiwalne/podglądy: {preview_archive_count} | "
            f"Cache: {'TAK' if cache_exists else 'NIE'} | "
            f"Miniatury: {cache_thumb_count} | "
            f"DECYZJA: Brak akcji (folder nie zawiera odpowiednich plików)"
        )

        return {
            "action": "no_action",
            "message": "Folder nie zawiera odpowiednich plików",
            "condition": "brak_plikow",
            "details": {
                "asset_count": asset_count,
                "preview_archive_count": preview_archive_count,
                "cache_exists": cache_exists,
                "cache_thumb_count": cache_thumb_count,
            },
        }

    @staticmethod
    def decide_action(folder_path: str) -> dict:
        """
        Podejmuje decyzję o akcji na podstawie zawartości folderu

        Metoda implementuje algorytm decyzyjny oparty na następujących
        warunkach:

        WARUNEK 1: Folder zawiera pliki archiwalne/podglądy, ale NIE ma plików
        asset → Uruchom scanner (potrzebne przetworzenie archiwów na assety)

        WARUNEK 2: Folder zawiera zarówno pliki archiwalne/podglądy jak i pliki
        asset
        - 2a: Brak folderu .cache → Uruchom scanner (generowanie miniaturek)
        - 2b: .cache istnieje, ale liczba miniaturek ≠ liczba assetów →
        Uruchom scanner
        - 2c: .cache istnieje i liczba miniaturek = liczba assetów → Pokaż
        galerię

        DODATKOWY PRZYPADEK: Folder zawiera tylko pliki asset (bez archiwów)
        - Brak .cache lub niezgodna liczba miniaturek → Uruchom scanner
        - Wszystko gotowe → Pokaż galerię

        Args:
            folder_path (str): Ścieżka do folderu do analizy

        Returns:
            dict: Słownik zawierający decyzję:
                - action: "run_scanner", "show_gallery", "no_action", "error"
                - message: Opis decyzji w języku polskim
                - condition: Nazwa warunku, który został spełniony
                - details: Szczegółowe informacje o stanie folderu

        Przykład zwracanego słownika:
        {
            "action": "run_scanner",
            "message": "Brak plików asset - uruchamiam scanner",
            "condition": "warunek_1",
            "details": {
                "preview_archive_count": 3,
                "asset_count": 0
            }
        }
        """
        try:
            # Krok 1: Przeanalizuj zawartość folderu
            content = FolderClickRules.analyze_folder_content(folder_path)

            # Sprawdź czy wystąpił błąd podczas analizy
            if "error" in content:
                logger.error(
                    f"BŁĄD ANALIZY FOLDERU: {folder_path} - {content['error']}"
                )
                return {
                    "action": "error",
                    "message": content["error"],
                    "condition": "error",
                }

            # Krok 2: Wyciągnij kluczowe informacje
            asset_count = content["asset_count"]
            preview_archive_count = content["preview_archive_count"]
            cache_exists = content["cache_exists"]
            cache_thumb_count = content["cache_thumb_count"]

            # Logowanie informacji diagnostycznych
            FolderClickRules._log_folder_analysis(folder_path, content)

            # WARUNEK 1: Folder zawiera pliki archiwalne/podglądy, ale NIE ma
            # plików asset → Scanner musi przetworzyć archiwa na pliki asset
            if preview_archive_count > 0 and asset_count == 0:
                return FolderClickRules._handle_condition_1(folder_path, content)

            # WARUNEK 2: Folder zawiera zarówno pliki archiwalne/podglądy jak i
            # pliki asset
            elif preview_archive_count > 0 and asset_count > 0:

                # Podwarunek 2a: Brak folderu .cache
                # → Scanner musi wygenerować miniatury
                if not cache_exists:
                    return FolderClickRules._handle_condition_2a(folder_path, content)

                # Podwarunek 2b: .cache istnieje, ale liczba miniaturek ≠ liczba
                # assetów → Scanner musi uzupełnić brakujące miniatury
                elif cache_thumb_count != asset_count:
                    return FolderClickRules._handle_condition_2b(folder_path, content)

                # Podwarunek 2c: .cache istnieje i liczba miniaturek = liczba
                # assetów → Wszystko gotowe, można pokazać galerię
                else:
                    return FolderClickRules._handle_condition_2c(folder_path, content)

            # DODATKOWY PRZYPADEK: Folder zawiera tylko pliki asset (bez
            # archiwów) → Sprawdź czy cache jest kompletny
            elif asset_count > 0 and preview_archive_count == 0:

                # Brak folderu .cache → Uruchom scanner
                if not cache_exists:
                    return FolderClickRules._handle_additional_case_no_cache(
                        folder_path, content
                    )

                # Niezgodna liczba miniaturek → Uruchom scanner
                elif cache_thumb_count != asset_count:
                    return FolderClickRules._handle_additional_case_mismatch(
                        folder_path, content
                    )

                # Wszystko gotowe → Pokaż galerię
                else:
                    return FolderClickRules._handle_additional_case_ready(
                        folder_path, content
                    )

            # PRZYPADEK DOMYŚLNY: Folder nie zawiera odpowiednich plików
            # → Nie wykonuj żadnej akcji
            else:
                return FolderClickRules._handle_default_case(folder_path, content)

        except Exception as e:
            error_msg = f"Błąd podejmowania decyzji dla folderu {folder_path}: {e}"
            logger.error(f"BŁĄD DECYZJI: {folder_path} - {error_msg}")
            return {"action": "error", "message": error_msg, "condition": "error"}
