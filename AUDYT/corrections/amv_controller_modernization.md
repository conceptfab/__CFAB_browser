### 🚀 amv_controller.py - Plan Modernizacji

**Data analizy:** 29.06.2025

#### Główne Kierunki Modernizacji:

1.  **Refaktoryzacja do Architektury Wielokomponentowej:**
    -   **Cel:** Rozbicie klasy `AmvController` na mniejsze, wyspecjalizowane kontrolery/serwisy, aby przestrzegać Zasady Pojedynczej Odpowiedzialności (SRP).
    -   **Plan Działania:**
        1.  Utworzyć `FileOperationController` do zarządzania operacjami na plikach (przenoszenie, usuwanie).
        2.  Utworzyć `AssetGridController` do zarządzania logiką siatki assetów (przebudowa, filtrowanie, sortowanie).
        3.  Utworzyć `FolderTreeController` do obsługi interakcji z drzewem folderów.
        4.  Główny `AmvController` będzie pełnił rolę koordynatora, przekazując zadania do odpowiednich pod-kontrolerów.

2.  **Wprowadzenie Asynchroniczności (Async/Await):**
    -   **Cel:** Zwiększenie responsywności aplikacji poprzez konwersję blokujących operacji na asynchroniczne.
    -   **Plan Działania:**
        1.  Zintegrować pętlę zdarzeń `asyncio` z pętlą zdarzeń Qt za pomocą biblioteki `qasync` lub podobnej.
        2.  Przepisać metody wykonujące operacje I/O (np. w `AssetRebuilderThread`, `_on_tile_filename_clicked`) na funkcje asynchroniczne (`async def`).
        3.  Używać `asyncio.to_thread` dla operacji, których nie da się łatwo przekonwertować na natywny kod asynchroniczny.

3.  **Modernizacja Zarządzania Ścieżkami:**
    -   **Cel:** Zastąpienie przestarzałego modułu `os.path` nowoczesnym i obiektowym modułem `pathlib`.
    -   **Plan Działania:**
        1.  W całym pliku zastąpić wywołania `os.path.join()`, `os.path.exists()` itp. na rzecz obiektów `pathlib.Path`.
        2.  Przykład: `os.path.join(folder, file)` zamienić na `Path(folder) / file`.

4.  **Implementacja Pełnych Adnotacji Typów (Type Hinting):**
    -   **Cel:** Poprawa czytelności, łatwości utrzymania kodu i umożliwienie statycznej analizy typów.
    -   **Plan Działania:**
        1.  Przejrzeć wszystkie sygnatury funkcji i zmienne, dodając brakujące adnotacje typów zgodnie z PEP 484.
        2.  Używać bardziej szczegółowych typów, np. `list[Asset]` zamiast `list`.

5.  **Zastosowanie Wzorca Wstrzykiwania Zależności (Dependency Injection):**
    -   **Cel:** Zmniejszenie powiązań (coupling) i ułatwienie testowania.
    -   **Plan Działania:**
        1.  Zamiast tworzyć zależności wewnątrz klasy (np. `self.asset_rebuilder = AssetRebuilderThread(folder_path)`), należy przekazywać je z zewnątrz, np. przez konstruktor.
        2.  Rozważyć użycie kontenera DI do zarządzania zależnościami w całej aplikacji.
