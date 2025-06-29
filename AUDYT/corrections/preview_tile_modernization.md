### 🚀 preview_tile.py - Plan Modernizacji

**Data analizy:** 29.06.2025

#### Główne Kierunki Modernizacji:

1.  **Transformacja do `QStyledItemDelegate` (KRYTYCZNY PRIORYTET):**
    -   **Cel:** Całkowite zastąpienie `PreviewTile` jako `QWidget` przez delegata, co jest kluczowe dla wydajnego wyświetlania dużych galerii z wirtualnym przewijaniem.
    -   **Plan Działania:**
        1.  Usunąć klasę `PreviewTile` jako `QWidget`.
        2.  Stworzyć klasę `PreviewTileDelegate`, która dziedziczy po `QStyledItemDelegate`.
        3.  Zaimplementować metodę `paint(painter, option, index)` w delegacie. Ta metoda będzie odpowiedzialna za ręczne rysowanie wyglądu kafelka (miniatury, nazwy pliku, checkboxa) na obszarze dostarczonym przez widok (`QListView`).
        4.  Zaimplementować metodę `sizeHint(option, index)`, aby poinformować widok o preferowanym rozmiarze kafelka.
        5.  Cała logika obsługi myszy (kliknięcia) zostanie przeniesiona do widoku (`QListView`), który będzie używał delegata.

2.  **Asynchroniczne Ładowanie Miniatur:**
    -   **Cel:** Przeniesienie operacji ładowania obrazów do wątku roboczego, aby nie blokować UI.
    -   **Plan Działania:**
        1.  Wykorzystać zmodernizowany `ThumbnailProcessor` (z modułu `thumbnail.py`) do asynchronicznego ładowania miniatur.
        2.  `PreviewTileDelegate` będzie wyświetlał placeholder, a następnie zlecał `ThumbnailProcessor` załadowanie miniatury. Po załadowaniu, `ThumbnailProcessor` emituje sygnał, a delegat odświeża dany element.

3.  **Wydzielenie Logiki Selekcji:**
    -   **Cel:** Oddzielenie logiki zarządzania zaznaczeniem od widoku.
    -   **Plan Działania:**
        1.  Wykorzystać `SelectionModel` (lub jego rozszerzenie) do zarządzania zaznaczeniem podglądów.
        2.  `PreviewTileDelegate` będzie rysował stan zaznaczenia na podstawie danych z modelu (np. `Qt.CheckStateRole`).

4.  **Centralizacja Stylów QSS:**
    -   **Cel:** Ułatwienie zarządzania wyglądem aplikacji i tworzenia motywów.
    -   **Plan Działania:**
        1.  Usunąć hardkodowane style (`setStyleSheet`) z kodu.
        2.  Zdefiniować style dla elementów listy w zewnętrznym pliku QSS (`styles.qss`).

5.  **Użycie `pathlib`:**
    -   **Cel:** Modernizacja kodu zgodnie z nowoczesnymi standardami Pythona.
    -   **Plan Działania:**
        1.  Zastąpić stringi przechowujące ścieżki (`file_path`) obiektami `pathlib.Path`.
        2.  Wszelkie operacje na ścieżkach powinny być wykonywane przy użyciu metod `Path`.
