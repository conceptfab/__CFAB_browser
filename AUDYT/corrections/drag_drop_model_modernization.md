### 🚀 drag_drop_model.py - Plan Modernizacji

**Data analizy:** 29.06.2025

#### Główne Kierunki Modernizacji:

Model `DragDropModel` jest prosty i funkcjonalny. Poniższe propozycje modernizacji mają na celu głównie poprawę jakości kodu, jego czytelności i przygotowanie na przyszły rozwój, a nie naprawę istniejących problemów.

1.  **Wprowadzenie `dataclass` dla Stanu Operacji:**
    -   **Cel:** Zastąpienie prostej listy ID bardziej strukturalnym obiektem stanu, co zwiększy czytelność i elastyczność.
    -   **Plan Działania:**
        1.  Zdefiniować `dataclass` `DragOperation`:
            ```python
            from dataclasses import dataclass, field
            from pathlib import Path

            @dataclass
            class DragOperation:
                source_path: Path
                asset_ids: set[str] = field(default_factory=set)
            ```
        2.  Model `DragDropModel` będzie przechowywał instancję `DragOperation | None` zamiast `self._dragged_asset_ids`.
        3.  Sygnały będą mogły emitować cały obiekt operacji, dostarczając konsumentom więcej kontekstu.

2.  **Użycie `set` dla ID Assetów:**
    -   **Cel:** Użycie bardziej odpowiedniej struktury danych do przechowywania unikalnych identyfikatorów.
    -   **Plan Działania:**
        1.  Zmienić typ `_dragged_asset_ids` z `list` na `set`.
        2.  Zaktualizować sygnatury metod i sygnałów, aby operowały na `set[str]` zamiast `list`.

3.  **Wydzielenie Logiki Walidacji (Rule Engine):**
    -   **Cel:** Uczynienie reguł walidacji bardziej elastycznymi i konfigurowalnymi.
    -   **Plan Działania:**
        1.  Stworzyć interfejs (klasę abstrakcyjną) `IDropRule` z jedną metodą `is_valid(operation: DragOperation, target_path: Path) -> bool`.
        2.  Stworzyć konkretne klasy reguł, np. `DisallowTextureFolderRule`, `CheckPermissionsRule`.
        3.  Stworzyć `DropValidator`, który będzie przechowywał listę reguł i sprawdzał je wszystkie.
        4.  `DragDropModel` będzie używał `DropValidator` do walidacji, zamiast implementować ją samodzielnie.

4.  **Pełne Adnotacje Typów i `pathlib`:**
    -   **Cel:** Poprawa jakości kodu zgodnie z nowoczesnymi standardami Pythona.
    -   **Plan Działania:**
        1.  Upewnić się, że wszystkie metody i atrybuty mają precyzyjne adnotacje typów.
        2.  Zastąpić wszystkie stringi przechowujące ścieżki (np. `target_path`) obiektami `pathlib.Path`.
