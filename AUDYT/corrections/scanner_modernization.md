### 🚀 scanner.py - Plan Modernizacji

**Data analizy:** 29.06.2025

#### Główne Kierunki Modernizacji:

1.  **Rozbicie Modułu na Mniejsze, Spójne Klasy/Moduły:**
    -   **Cel:** Wprowadzenie czystej separacji odpowiedzialności i poprawa modularności.
    -   **Plan Działania:**
        1.  **`AssetScanner`:** Klasa odpowiedzialna za skanowanie folderów, identyfikację plików archiwum i obrazów, oraz znajdowanie par. Powinna używać `os.scandir` i `pathlib`.
        2.  **`AssetCreator`:** Klasa odpowiedzialna za tworzenie i aktualizowanie plików `.asset` na dysku. Powinna przyjmować obiekt `AssetData` i zapisywać go do pliku JSON. Powinna również obsługiwać logikę zachowywania danych użytkownika (gwiazdki, kolor) przy aktualizacji.
        3.  **`ThumbnailService`:** Klasa odpowiedzialna za generowanie miniatur. Powinna być asynchroniczna i działać w tle.
        4.  **`UnpairedFilesManager`:** Klasa odpowiedzialna za zarządzanie plikiem `unpair_files.json` (ładowanie, zapisywanie, dodawanie/usuwanie wpisów).
        5.  **`AssetData` (dataclass):** Dedykowana klasa do reprezentowania danych pojedynczego assetu.

2.  **Pełna Asynchronizacja Operacji I/O:**
    -   **Cel:** Wyeliminowanie blokowania wątków przez operacje na systemie plików i przetwarzanie obrazów.
    -   **Plan Działania:**
        1.  Wszystkie operacje I/O (skanowanie, odczyt/zapis JSON, generowanie miniatur) powinny być asynchroniczne. Można to osiągnąć poprzez:
            -   Użycie `asyncio.to_thread` dla blokujących wywołań `os.*`, `json.*`, `shutil.*`.
            -   Zaimplementowanie `ThumbnailService` jako asynchronicznego serwisu działającego w puli wątków.
        2.  Funkcja `find_and_create_assets` (lub jej odpowiednik w nowej architekturze) powinna być funkcją asynchroniczną (`async def`).

3.  **Wprowadzenie `pathlib` dla Zarządzania Ścieżkami:**
    -   **Cel:** Zastąpienie przestarzałego `os.path` nowoczesnym, obiektowym API.
    -   **Plan Działania:**
        1.  Wszystkie stringi reprezentujące ścieżki powinny zostać zastąpione obiektami `pathlib.Path`.
        2.  Wszelkie operacje na ścieżkach powinny być wykonywane przy użyciu metod `Path` (np. `path.exists()`, `path.joinpath()`, `path.name`, `path.suffix`).

4.  **Użycie `dataclasses` dla Danych Assetów:**
    -   **Cel:** Zastąpienie słowników typowanymi, strukturalnymi obiektami.
    -   **Plan Działania:**
        1.  Zdefiniować `AssetData` jako `dataclass` z odpowiednimi polami i typami.
        2.  Wszystkie funkcje i metody powinny operować na obiektach `AssetData` zamiast na słownikach.

5.  **Implementacja Bezpiecznego Anulowania (Cooperative Cancellation):**
    -   **Cel:** Umożliwienie bezpiecznego przerwania długotrwałych operacji.
    -   **Plan Działania:**
        1.  Wprowadzić flagę anulowania, którą funkcje asynchroniczne będą regularnie sprawdzać.
        2.  Zapewnić, że operacje I/O mogą być bezpiecznie przerwane w trakcie ich trwania.
