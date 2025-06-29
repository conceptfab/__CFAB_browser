### 🚀 rules.py - Plan Modernizacji

**Data analizy:** 29.06.2025

#### Główne Kierunki Modernizacji:

1.  **Wprowadzenie `pathlib.Path` dla Ścieżek:**
    -   **Cel:** Zastąpienie stringów reprezentujących ścieżki nowoczesnym, obiektowym API `pathlib`.
    -   **Plan Działania:**
        1.  Zmienić sygnatury wszystkich funkcji, aby przyjmowały `folder_path: Path`.
        2.  Wewnątrz funkcji używać metod obiektu `Path` do operacji na plikach (np. `path.exists()`, `path.is_dir()`, `path.iterdir()`).

2.  **Użycie `dataclasses` dla Wyników Analizy:**
    -   **Cel:** Zastąpienie słowników (`dict`) typowanymi, strukturalnymi obiektami dla wyników analizy folderów.
    -   **Plan Działania:**
        1.  Zdefiniować `FolderAnalysisResult` jako `dataclass` z odpowiednimi polami i typami (np. `asset_files: list[Path]`, `cache_exists: bool`).
        2.  Metoda `analyze_folder_content` będzie zwracać instancję `FolderAnalysisResult`.
        3.  Metody `_create_error_result` i `_log_folder_analysis` zostaną zaktualizowane, aby operować na `FolderAnalysisResult`.

3.  **Refaktoryzacja Logiki Decyzyjnej (Chain of Responsibility/Strategy Pattern):**
    -   **Cel:** Uproszczenie metody `decide_action` i uczynienie jej bardziej rozszerzalną.
    -   **Plan Działania:**
        1.  Stworzyć interfejs (klasę abstrakcyjną) `IFolderActionRule` z metodą `applies(analysis: FolderAnalysisResult) -> bool` i `get_action(analysis: FolderAnalysisResult) -> dict`.
        2.  Dla każdego warunku (np. `warunek_1`, `warunek_2a`) stworzyć osobną klasę implementującą ten interfejs (np. `NoAssetFilesRule`, `MissingCacheRule`).
        3.  Metoda `decide_action` będzie zawierała listę tych reguł i iterowała po nich, aż znajdzie pierwszą, która się zastosuje, a następnie zwróci jej akcję.

4.  **Pełne Adnotacje Typów:**
    -   **Cel:** Poprawa czytelności i umożliwienie statycznej analizy kodu.
    -   **Plan Działania:**
        1.  Upewnić się, że wszystkie metody i atrybuty mają precyzyjne adnotacje typów.

5.  **Asynchroniczne Wersje Funkcji (Opcjonalnie):**
    -   **Cel:** Zapewnienie, że operacje I/O nie blokują głównego wątku UI.
    -   **Plan Działania:**
        1.  Dodać asynchroniczne wersje funkcji `analyze_folder_content` (np. `async def analyze_folder_content_async(folder_path: Path) -> FolderAnalysisResult:`).
        2.  Wewnątrz tych funkcji używać `asyncio.to_thread` do wywoływania synchronicznych operacji plikowych.
