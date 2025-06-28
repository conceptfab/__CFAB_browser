# PATCH CODE: rules.py

**Wersja: 1.0**

**Data: 2025-06-28**

**Autor: Gemini**

---

## 🎯 OPIS ZMIAN

1.  **Zmiana `THUMB_EXTENSION` na zbiór:** Zapewniono spójność z innymi definicjami rozszerzeń.
2.  **Uczynienie `CACHE_TTL` łatwiejszym do modyfikacji:** Zmieniono na zmienną klasy.

## 💻 KOD

### Zmiana 1 i 2: Zmiana `THUMB_EXTENSION` i `CACHE_TTL`

```python
class FolderClickRules:
    """
    Klasa zawierająca logikę decyzyjną dla kliknięć w foldery

    Ta klasa implementuje algorytm decyzyjny, który analizuje zawartość folderu
    i podejmuje decyzje o tym, jaką akcję wykonać:

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
    THUMB_EXTENSION: Set[str] = {".thumb"} # Zmieniono na zbiór

    # Zbiory rozszerzeń plików dla efektywnego lookup
    ASSET_EXTENSIONS: Set[str] = {".asset"}
    ARCHIVE_EXTENSIONS: Set[str] = {".rar", ".zip", ".sbsar"}
    PREVIEW_EXTENSIONS: Set[str] = {".jpg", ".jpeg", ".png", ".gif"}

    # Cache TTL (Time To Live) w sekundach
    CACHE_TTL = 300  # 5 minut (można uczynić konfigurowalnym z config.json w przyszłości)

    # Cache dla wyników analizy folderów
    _folder_analysis_cache: Dict[str, Dict] = {}
    _cache_timestamps: Dict[str, float] = {}

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
                if item.lower().endswith(tuple(FolderClickRules.THUMB_EXTENSION)) # Użycie tuple dla endswith
            )

            return thumb_count

        except (OSError, PermissionError) as e:
            logger.warning(f"Błąd sprawdzania .cache: {e}")
            return 0
```
