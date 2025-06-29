### 🚀 asset_tile_view.py - Plan Modernizacji

**Data analizy:** 29.06.2025

#### Główne Kierunki Modernizacji:

1.  **Przeprojektowanie na Potrzeby Wirtualnego Przewijania (Delegat):**
    -   **Cel:** Umożliwienie wydajnego wyświetlania tysięcy elementów poprzez rezygnację z tworzenia widżetu dla każdego elementu.
    -   **Plan Działania:**
        1.  Zrezygnować z klasy `AssetTileView` jako `QFrame`. Zamiast tego, stworzyć klasę `AssetTileDelegate`, która będzie dziedziczyć po `QStyledItemDelegate`.
        2.  Zaimplementować metodę `paint(painter, option, index)` w delegacie. Ta metoda będzie odpowiedzialna za ręczne rysowanie wyglądu kafelka (miniatury, tekstu, gwiazdek, checkboxa) na obszarze dostarczonym przez widok (`QListView` lub `QTableView`). To jest klucz do osiągnięcia najwyższej wydajności.
        3.  Zaimplementować metodę `sizeHint(option, index)`, aby poinformować widok o preferowanym rozmiarze kafelka.
        4.  Cała logika obsługi myszy (kliknięcia, hover) zostanie przeniesiona do widoku siatki, który będzie używał delegata.

2.  **Centralizacja Zarządzania Zasobami:**
    -   **Cel:** Usunięcie z widoku odpowiedzialności za ładowanie zasobów i uniknięcie hardkodowania ścieżek.
    -   **Plan Działania:**
        1.  Stworzyć globalny singleton lub wstrzykiwaną usługę `ResourceManager`.
        2.  `ResourceManager` będzie odpowiedzialny za ładowanie stylów QSS z pliku oraz za dostarczanie ikon i obrazów z systemu zasobów Qt (`.qrc`).
        3.  Delegat (`AssetTileDelegate`) będzie prosił `ResourceManager` o potrzebne `QPixmap` do narysowania ikony czy placeholdera.

3.  **Asynchroniczny Loader Miniatur:**
    -   **Cel:** Zapobieganie blokowaniu głównego wątku przez operacje I/O podczas ładowania miniatur.
    -   **Plan Działania:**
        1.  Stworzyć klasę `ThumbnailLoader` działającą na globalnym `QThreadPool`.
        2.  Gdy delegat rysuje kafelek, sprawdza, czy miniatura jest w cache'u (np. `QCache`).
        3.  Jeśli miniatury nie ma w cache'u, delegat wyświetla placeholder i wysyła asynchroniczne zadanie do `ThumbnailLoader` z prośbą o załadowanie obrazka dla danego `index`.
        4.  Gdy `ThumbnailLoader` zakończy pracę, emituje sygnał `thumbnail_loaded(index, pixmap)`. Widok siatki przechwytuje ten sygnał i zleca odświeżenie tylko tego jednego elementu (`view.update(index)`).

4.  **Użycie `pathlib` i `dataclasses`:**
    -   **Cel:** Modernizacja kodu zgodnie z nowymi standardami Pythona.
    -   **Plan Działania:**
        1.  Wszelkie operacje na ścieżkach powinny zostać przeniesione do `pathlib.Path`.
        2.  Dane przekazywane do delegata (przez model) powinny być w formie `AssetData` (`dataclass`), a nie surowego słownika.
