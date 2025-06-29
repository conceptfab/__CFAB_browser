### 🚀 preview_gallery_view.py - Plan Modernizacji

**Data analizy:** 29.06.2025

#### Główne Kierunki Modernizacji:

1.  **Transformacja do Architektury Model-View-Delegate (KRYTYCZNY PRIORYTET):**
    -   **Cel:** Umożliwienie wydajnego wyświetlania dużych zbiorów danych poprzez wykorzystanie wbudowanych mechanizmów Qt do wirtualnego przewijania i reużywania widoków.
    -   **Plan Działania:**
        1.  Zastąpić `QGridLayout` i ręczne dodawanie `PreviewTile` przez `QListView`.
        2.  Stworzyć dedykowany model dziedziczący po `QAbstractListModel` (np. `PreviewListModel`), który będzie dostarczał dane (ścieżki do podglądów) do `QListView`.
        3.  Zastąpić `PreviewTile` przez `QStyledItemDelegate` (np. `PreviewTileDelegate`), który będzie odpowiedzialny za rysowanie wyglądu pojedynczego elementu listy. Delegat będzie rysował miniaturę, checkbox i inne elementy, ale nie będzie tworzył pełnych widżetów.
        4.  `PreviewListModel` będzie emitował sygnały `rowsInserted`, `rowsRemoved`, `dataChanged`, a `QListView` będzie reagował na nie, odświeżając tylko zmienione elementy.

2.  **Asynchroniczne Ładowanie Miniatur:**
    -   **Cel:** Przeniesienie operacji ładowania obrazów do wątku roboczego, aby nie blokować UI.
    -   **Plan Działania:**
        1.  Wykorzystać zmodernizowany `ThumbnailProcessor` (z modułu `thumbnail.py`) do asynchronicznego ładowania miniatur.
        2.  `PreviewTileDelegate` będzie wyświetlał placeholder, a następnie zlecał `ThumbnailProcessor` załadowanie miniatury. Po załadowaniu, `ThumbnailProcessor` emituje sygnał, a delegat odświeża dany element.

3.  **Wydzielenie Logiki Selekcji:**
    -   **Cel:** Oddzielenie logiki zarządzania zaznaczeniem od widoku.
    -   **Plan Działania:**
        1.  Wykorzystać `SelectionModel` (lub jego rozszerzenie) do zarządzania zaznaczeniem podglądów.
        2.  `PreviewGalleryView` będzie jedynie emitował sygnał (np. `preview_toggled(file_path, is_checked)`), a kontroler będzie nasłuchiwał na ten sygnał i aktualizował `SelectionModel`.
        3.  `PreviewTileDelegate` będzie rysował stan zaznaczenia na podstawie danych z modelu (np. `Qt.CheckStateRole`).

4.  **Użycie `pathlib` i `dataclasses`:**
    -   **Cel:** Modernizacja kodu zgodnie z nowoczesnymi standardami Pythona.
    -   **Plan Działania:**
        1.  Zastąpić wszystkie stringi przechowujące ścieżki obiektami `pathlib.Path`.
        2.  Wprowadzić `dataclass` dla reprezentacji danych (np. `PreviewData`).
