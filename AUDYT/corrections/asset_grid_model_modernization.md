### 🚀 asset_grid_model.py - Plan Modernizacji

**Data analizy:** 29.06.2025

#### Główne Kierunki Modernizacji:

1.  **Transformacja do `QAbstractListModel` (NAJWYŻSZY PRIORYTET):**
    -   **Cel:** Pełna integracja z architekturą Qt Model/View, co jest fundamentem dla wydajnego wyświetlania dużych zbiorów danych.
    -   **Plan Działania:**
        1.  Zmienić dziedziczenie klasy z `QObject` na `QAbstractListModel`.
        2.  Zaimplementować wymagane metody: `rowCount()`, `data(index, role)` i opcjonalnie `flags(index)`.
        3.  W metodzie `data()`, w zależności od `role` (np. `Qt.ItemDataRole.DisplayRole`, `Qt.ItemDataRole.DecorationRole`), zwracać odpowiednie dane (nazwa pliku, miniatura, itp.).
        4.  Zastąpić sygnał `assets_changed` wbudowanymi sygnałami `QAbstractItemModel` (np. `beginInsertRows`, `endInsertRows`, `dataChanged`).

2.  **Implementacja Wzorca Repozytorium (Repository Pattern):**
    -   **Cel:** Oddzielenie logiki biznesowej modelu od sposobu pozyskiwania danych (z dysku, z bazy danych, z sieci).
    -   **Plan Działania:**
        1.  Utworzyć klasę `AssetRepository`, która będzie odpowiedzialna za operacje I/O (ładowanie plików `.asset`, skanowanie folderów).
        2.  `AssetGridModel` będzie korzystał z `AssetRepository` do pobierania danych, ale sam nie będzie zawierał żadnego kodu związanego z operacjami na plikach.
        3.  Repozytorium może implementować strategię cache'owania (np. LRU cache).

3.  **Wprowadzenie Struktur Danych (`dataclasses`):**
    -   **Cel:** Zastąpienie słowników obiektami z typowaniem, co poprawi czytelność i bezpieczeństwo kodu.
    -   **Plan Działania:**
        1.  Zdefiniować `AssetData` jako `dataclass`:
            ```python
            from dataclasses import dataclass, field
            from pathlib import Path

            @dataclass
            class AssetData:
                name: str
                path: Path
                asset_type: str
                thumbnail_path: Path | None = None
                stars: int = 0
                tags: list[str] = field(default_factory=list)
            ```
        2.  Przepisać model, aby wewnętrznie przechowywał `list[AssetData]` zamiast `list[dict]`.

4.  **Integracja z `asyncio` dla Operacji I/O:**
    -   **Cel:** Zapewnienie, że operacje ładowania danych z repozytorium nie blokują głównego wątku.
    -   **Plan Działania:**
        1.  Metody w `AssetRepository` (np. `get_assets_async`) powinny być funkcjami asynchronicznymi (`async def`).
        2.  `AssetGridModel` będzie wywoływał te metody asynchronicznie (np. przy użyciu `qasync`), a po otrzymaniu wyników aktualizował swój stan i emitował odpowiednie sygnały `QAbstractItemModel`.
