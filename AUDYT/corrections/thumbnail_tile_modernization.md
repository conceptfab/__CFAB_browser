### 🚀 thumbnail_tile.py - Plan Modernizacji

**Data analizy:** 29.06.2025

#### Główne Kierunki Modernizacji:

1.  **Usunięcie Duplikacji Kodu (`PreviewWindow`):**
    -   **Cel:** Eliminacja zduplikowanego kodu i centralizacja logiki.
    -   **Plan Działania:**
        1.  Usunąć klasę `PreviewWindow` z tego pliku.
        2.  Wszędzie tam, gdzie jest potrzebna, importować ją z `core.preview_window`.

2.  **Transformacja do `QStyledItemDelegate` (KRYTYCZNY PRIORYTET):**
    -   **Cel:** Całkowite zastąpienie `ThumbnailTile` i `FolderTile` jako `QWidget` przez delegaty, co jest kluczowe dla wydajnego wyświetlania dużych galerii z wirtualnym przewijaniem.
    -   **Plan Działania:**
        1.  Usunąć klasy `ThumbnailTile` i `FolderTile` jako `QWidget`.
        2.  Stworzyć klasy `ThumbnailTileDelegate` i `FolderTileDelegate`, które dziedziczą po `QStyledItemDelegate`.
        3.  Zaimplementować metodę `paint(painter, option, index)` w delegatach. Ta metoda będzie odpowiedzialna za ręczne rysowanie wyglądu kafelka (miniatury, nazwy pliku, gwiazdek, checkboxa) na obszarze dostarczonym przez widok (`QListView` lub `QTableView`).
        4.  Zaimplementować metodę `sizeHint(option, index)`, aby poinformować widok o preferowanym rozmiarze kafelka.
        5.  Cała logika obsługi myszy (kliknięcia, drag & drop) zostanie przeniesiona do widoku (`QListView`) lub kontrolera, który będzie używał delegata.

3.  **Asynchroniczne Ładowanie Obrazów:**
    -   **Cel:** Przeniesienie operacji ładowania obrazów do wątku roboczego, aby nie blokować UI.
    -   **Plan Działania:**
        1.  Wykorzystać zmodernizowany `ThumbnailProcessor` (z modułu `thumbnail.py`) do asynchronicznego ładowania miniatur i ikon.
        2.  Delegaty będą wyświetlać placeholder, a następnie zlecać `ThumbnailProcessor` załadowanie obrazu. Po załadowaniu, `ThumbnailProcessor` emituje sygnał, a delegat odświeża dany element.

4.  **Centralizacja Stylów QSS:**
    -   **Cel:** Ułatwienie zarządzania wyglądem aplikacji i tworzenia motywów.
    -   **Plan Działania:**
        1.  Usunąć hardkodowane style (`setStyleSheet`) z kodu.
        2.  Zdefiniować style dla elementów listy w zewnętrznym pliku QSS (`styles.qss`).

5.  **Użycie `pathlib` i `dataclasses`:**
    -   **Cel:** Modernizacja kodu zgodnie z nowoczesnymi standardami Pythona.
    -   **Plan Działania:**
        1.  Zastąpić stringi przechowujące ścieżki obiektami `pathlib.Path`.
        2.  Wprowadzić `dataclass` dla reprezentacji danych (np. `AssetData`, `FolderData`).
