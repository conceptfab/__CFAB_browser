### 🚀 asset_tile_model.py - Plan Modernizacji

**Data analizy:** 29.06.2025

#### Główne Kierunki Modernizacji:

1.  **Wprowadzenie `dataclass` dla Reprezentacji Danych:**
    -   **Cel:** Zastąpienie słowników nowoczesnymi, typowanymi strukturami danych.
    -   **Plan Działania:**
        1.  Zdefiniować `AssetData` jako `dataclass`, zawierającą wszystkie pola z obecnego słownika (`name`, `size_mb`, `stars`, `thumbnail`, itp.).
        2.  Model `AssetTileModel` będzie przechowywał instancję `AssetData` zamiast słownika `self.data`.
        3.  Metody `get_*` będą prostymi akcesorami do pól `dataclass`.

2.  **Asynchroniczna Persystencja z Wzorcem Repozytorium:**
    -   **Cel:** Oddzielenie logiki modelu od zapisu na dysku i wyeliminowanie blokujących operacji I/O z głównego wątku.
    -   **Plan Działania:**
        1.  Utworzyć klasę `AssetRepository` z metodą `async def save_asset(asset_data: AssetData, path: Path)`.
        2.  W `AssetTileModel`, metoda `set_stars` będzie tylko aktualizować pole w `self.asset_data` i emitować sygnał `data_changed(field='stars')`.
        3.  `AmvController` (lub dedykowany `AssetPersistenceController`) będzie nasłuchiwał na ten sygnał i wywoływał metodę `save_asset` z repozytorium w sposób asynchroniczny (np. używając `qasync` lub `asyncio.create_task`).

3.  **Modernizacja Zarządzania Ścieżkami do `pathlib`:**
    -   **Cel:** Zastąpienie modułu `os.path` nowoczesnym, obiektowym API.
    -   **Plan Działania:**
        1.  Wszystkie atrybuty i zmienne przechowujące ścieżki (np. `asset_file_path`) powinny być typu `pathlib.Path`.
        2.  Wszelkie operacje na ścieżkach (łączenie, sprawdzanie istnienia, pobieranie nazwy folderu) powinny być wykonywane przy użyciu metod obiektu `Path` (np. `path.parent`, `path.exists()`, `path / 'filename'`).

4.  **Udoskonalenie Sygnałów:**
    -   **Cel:** Dostarczanie bardziej szczegółowych informacji o zmianach, aby umożliwić bardziej precyzyjne aktualizacje w innych częściach aplikacji.
    -   **Plan Działania:**
        1.  Zmodyfikować sygnał `data_changed`, aby przekazywał informację, które pole uległo zmianie, np. `data_changed = pyqtSignal(str) # field_name`.
        2.  Dzięki temu słuchacze (np. kontroler) mogą decydować, czy dana zmiana wymaga kosztownej operacji (jak zapis na dysku), czy tylko prostej aktualizacji UI.
