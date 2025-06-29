### ⚡ rules.py - Analiza Wydajności

**Data analizy:** 29.06.2025

#### Główne Problemy Wydajnościowe:

1.  **Synchroniczne Operacje I/O w `analyze_folder_content` (NISKI PRIORYTET):**
    -   **Problem:** Metoda `analyze_folder_content` wykonuje synchroniczne operacje I/O (`os.path.exists`, `os.listdir`, `os.path.isdir`, `os.stat().st_mtime`). Chociaż te operacje są zazwyczaj szybkie, w przypadku wolnych dysków sieciowych lub bardzo dużych katalogów mogą powodować krótkotrwałe blokowanie wątku, w którym są wywoływane.
    -   **Wpływ:** Jeśli `decide_action` jest wywoływane w głównym wątku UI (np. po kliknięciu w folder), może to prowadzić do mikro-zacięć interfejsu. W kontekście całego systemu, gdzie te funkcje są używane przez inne komponenty (np. `FolderStructureScanner`), stają się one punktami, w których może dochodzić do blokowania.
    -   **Rekomendacja (NISKA):** Aby zapewnić pełną responsywność, zwłaszcza w aplikacjach GUI, operacje I/O powinny być wykonywane asynchronicznie. Można to osiągnąć poprzez:
        a)  **Asynchroniczne API:** Dodanie asynchronicznych wersji funkcji, np. `async def analyze_folder_content_async(folder_path: Path) -> FolderAnalysisResult:`. Wewnątrz tych funkcji można użyć `asyncio.to_thread` do uruchomienia synchronicznych operacji w puli wątków.
        b)  **Delegowanie do Wątków Roboczych:** Komponenty wywołujące te funkcje powinny uruchamiać je w osobnym wątku (np. `QThread`) lub w puli wątków (`QThreadPool`).

2.  **Wielokrotne Odpytywanie Systemu Plików w `_analyze_cache_folder`:**
    -   **Problem:** Metoda `_analyze_cache_folder` używa `os.listdir` do pobrania wszystkich elementów w folderze `.cache`, a następnie iteruje po nich, aby policzyć pliki `.thumb`. Dla bardzo dużych folderów `.cache` może to być nieefektywne.
    -   **Rekomendacja (MIKROOPTYMALIZACJA):** Zastąpić `os.listdir` przez `os.scandir`, co jest bardziej wydajne, ponieważ zwraca iterator obiektów `DirEntry` i pozwala na szybsze filtrowanie.

#### Pozytywne Aspekty:

-   **Cache Wyników Analizy:** Implementacja cache (`_folder_analysis_cache`) z TTL (`CACHE_TTL`) jest bardzo dobrym rozwiązaniem, które znacząco poprawia wydajność, zapobiegając wielokrotnemu analizowaniu tego samego folderu w krótkim czasie.
-   **Użycie `set` dla Rozszerzeń:** Użycie zbiorów (`Set[str]`) do przechowywania rozszerzeń plików (`ASSET_EXTENSIONS`, `ARCHIVE_EXTENSIONS`, `PREVIEW_EXTENSIONS`) zapewnia bardzo szybkie sprawdzanie przynależności (`O(1)`), co jest wydajne.
