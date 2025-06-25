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
        try:
            # Sprawdź czy folder istnieje
            if not os.path.exists(folder_path):
                return {
                    "error": f"Folder nie istnieje: {folder_path}",
                    "asset_files": [],
                    "preview_archive_files": [],
                    "cache_exists": False,
                    "cache_thumb_count": 0,
                }

            # Pobierz listę wszystkich elementów w folderze
            items = os.listdir(folder_path)

            # Kategoryzuj pliki według typów
            asset_files = []
            preview_archive_files = []

            for item in items:
                # Pomijamy ukryte pliki (zaczynające się od kropki)
                if not item.startswith("."):
                    item_lower = item.lower()

                    # Kategoria 1: Pliki asset (.asset)
                    if item_lower.endswith(".asset"):
                        asset_files.append(item)

                    # Kategoria 2: Pliki archiwalne i podglądy
                    elif (
                        item_lower.endswith(".rar")
                        or item_lower.endswith(".zip")
                        or item_lower.endswith(".sbsar")
                    ):
                        preview_archive_files.append(item)

                    # Kategoria 3: Pliki podglądów (obrazy)
                    elif (
                        item_lower.endswith(".jpg")
                        or item_lower.endswith(".png")
                        or item_lower.endswith(".jpeg")
                        or item_lower.endswith(".gif")
                    ):
                        preview_archive_files.append(item)

            # Sprawdź istnienie i zawartość folderu .cache
            cache_folder_path = os.path.join(folder_path, ".cache")
            cache_exists = os.path.exists(cache_folder_path) and os.path.isdir(
                cache_folder_path
            )

            # Policz pliki miniaturek w folderze .cache
            cache_thumb_count = 0
            if cache_exists:
                try:
                    cache_items = os.listdir(cache_folder_path)
                    # Licz tylko pliki miniaturek (.thumb)
                    cache_thumb_count = len(
                        [
                            item
                            for item in cache_items
                            if item.lower().endswith(".thumb")
                        ]
                    )
                except Exception as e:
                    logger.warning(f"Błąd sprawdzania .cache: {e}")
                    cache_thumb_count = 0

            # Zwróć kompletne informacje o zawartości folderu
            return {
                "asset_files": asset_files,
                "preview_archive_files": preview_archive_files,
                "cache_exists": cache_exists,
                "cache_thumb_count": cache_thumb_count,
                "asset_count": len(asset_files),
                "preview_archive_count": len(preview_archive_files),
            }

        except Exception as e:
            logger.error(f"Błąd analizy zawartości folderu {folder_path}: {e}")
            return {
                "error": f"Błąd analizy folderu: {e}",
                "asset_files": [],
                "preview_archive_files": [],
                "cache_exists": False,
                "cache_thumb_count": 0,
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
            logger.info(
                f"ANALIZA FOLDERU: {folder_path} | "
                f"Asset: {asset_count} | "
                f"Podglądy/Archiwa: {preview_archive_count} | "
                f"Cache: {'TAK' if cache_exists else 'NIE'} | "
                f"Miniatury: {cache_thumb_count}"
            )

            # WARUNEK 1: Folder zawiera pliki archiwalne/podglądy, ale NIE ma
            # plików asset → Scanner musi przetworzyć archiwa na pliki asset
            if preview_archive_count > 0 and asset_count == 0:
                logger.info(
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

            # WARUNEK 2: Folder zawiera zarówno pliki archiwalne/podglądy jak i
            # pliki asset
            elif preview_archive_count > 0 and asset_count > 0:

                # Podwarunek 2a: Brak folderu .cache
                # → Scanner musi wygenerować miniatury
                if not cache_exists:
                    logger.info(
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
                            "cache_exists": cache_exists,
                        },
                    }

                # Podwarunek 2b: .cache istnieje, ale liczba miniaturek ≠ liczba
                # assetów → Scanner musi uzupełnić brakujące miniatury
                elif cache_thumb_count != asset_count:
                    logger.info(
                        f"PRZYPADEK 2B WYKRYTY: {folder_path} | "
                        f"Pliki archiwalne/podglądy: {preview_archive_count} | "
                        f"Pliki asset: {asset_count} | "
                        f"Cache: TAK | "
                        f"Miniatury: {cache_thumb_count} | "
                        f"DECYZJA: Uruchamiam scanner (niezgodna liczba "
                        f"miniaturek)"
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
                            "cache_exists": cache_exists,
                            "cache_thumb_count": cache_thumb_count,
                        },
                    }

                # Podwarunek 2c: .cache istnieje i liczba miniaturek = liczba
                # assetów → Wszystko gotowe, można pokazać galerię
                else:
                    logger.info(
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
                            f"(thumb: {cache_thumb_count}, asset: "
                            f"{asset_count})"
                        ),
                        "condition": "warunek_2c",
                        "details": {
                            "preview_archive_count": preview_archive_count,
                            "asset_count": asset_count,
                            "cache_exists": cache_exists,
                            "cache_thumb_count": cache_thumb_count,
                        },
                    }

            # DODATKOWY PRZYPADEK: Folder zawiera tylko pliki asset (bez
            # archiwów) → Sprawdź czy cache jest kompletny
            elif asset_count > 0 and preview_archive_count == 0:

                # Brak folderu .cache → Uruchom scanner
                if not cache_exists:
                    logger.info(
                        f"PRZYPADEK DODATKOWY (BRAK CACHE): {folder_path} | "
                        f"Pliki asset: {asset_count} | "
                        f"Pliki archiwalne/podglądy: {preview_archive_count} | "
                        f"Cache: NIE | "
                        f"DECYZJA: Uruchamiam scanner (tylko asset, brak "
                        f".cache)"
                    )

                    return {
                        "action": "run_scanner",
                        "message": (
                            "Tylko pliki asset, brak .cache - uruchamiam " "scanner"
                        ),
                        "condition": "dodatkowy_brak_cache",
                        "details": {
                            "asset_count": asset_count,
                            "preview_archive_count": preview_archive_count,
                            "cache_exists": cache_exists,
                        },
                    }

                # Niezgodna liczba miniaturek → Uruchom scanner
                elif cache_thumb_count != asset_count:
                    logger.info(
                        f"PRZYPADEK DODATKOWY (NIEZGODNA LICZBA): "
                        f"{folder_path} | "
                        f"Pliki asset: {asset_count} | "
                        f"Pliki archiwalne/podglądy: {preview_archive_count} | "
                        f"Cache: TAK | "
                        f"Miniatury: {cache_thumb_count} | "
                        f"DECYZJA: Uruchamiam scanner (niezgodna liczba "
                        f"miniaturek)"
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
                            "cache_exists": cache_exists,
                            "cache_thumb_count": cache_thumb_count,
                        },
                    }

                # Wszystko gotowe → Pokaż galerię
                else:
                    logger.info(
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
                            "cache_exists": cache_exists,
                            "cache_thumb_count": cache_thumb_count,
                        },
                    }

            # PRZYPADEK DOMYŚLNY: Folder nie zawiera odpowiednich plików
            # → Nie wykonuj żadnej akcji
            else:
                logger.info(
                    f"PRZYPADEK DOMYŚLNY: {folder_path} | "
                    f"Pliki asset: {asset_count} | "
                    f"Pliki archiwalne/podglądy: {preview_archive_count} | "
                    f"Cache: {'TAK' if cache_exists else 'NIE'} | "
                    f"Miniatury: {cache_thumb_count} | "
                    f"DECYZJA: Brak akcji (folder nie zawiera odpowiednich "
                    f"plików)"
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

        except Exception as e:
            error_msg = f"Błąd podejmowania decyzji dla folderu {folder_path}: {e}"
            logger.error(f"BŁĄD DECYZJI: {folder_path} - {error_msg}")
            return {"action": "error", "message": error_msg, "condition": "error"}
