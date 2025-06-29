### 🚀 pairing_tab.py - Plan Modernizacji

**Data analizy:** 29.06.2025

#### Główne Kierunki Modernizacji:

1.  **Refaktoryzacja do Architektury Model-View-Controller (MVC):**
    -   **Cel:** Oddzielenie logiki widoku od logiki biznesowej i kontroli.
    -   **Plan Działania:**
        1.  Stworzyć dedykowany `PairingController`. Będzie on odpowiedzialny za obsługę interakcji użytkownika (kliknięcia przycisków, zaznaczenia), komunikację z `PairingModel` (lub jego zrefaktoryzowanymi częściami) oraz inicjowanie operacji na plikach.
        2.  `PairingTab` będzie emitował sygnały (np. `create_asset_requested`, `delete_previews_requested`) w odpowiedzi na akcje użytkownika. Kontroler będzie nasłuchiwał na te sygnały.
        3.  Kontroler będzie również nasłuchiwał na sygnały z `PairingModel` (np. `data_changed`, `operation_completed`) i aktualizował widok za pomocą metod `PairingTab` (np. `update_archive_list`, `show_message`).

2.  **Asynchroniczne Operacje I/O:**
    -   **Cel:** Przeniesienie wszystkich blokujących operacji na plikach do wątków roboczych lub zadań asynchronicznych.
    -   **Plan Działania:**
        1.  Wszystkie operacje na plikach (usuwanie, tworzenie assetów, otwieranie plików zewnętrznych) powinny być wykonywane asynchronicznie. Można użyć `QThread` lub `asyncio.to_thread`.
        2.  `PairingController` będzie odpowiedzialny za uruchamianie tych operacji w tle i zarządzanie ich postępem.
        3.  Widok będzie wyświetlał wskaźniki postępu (np. spinner, pasek postępu) i blokował przyciski podczas trwania operacji.

3.  **Wirtualne Przewijanie dla Listy Archiwów:**
    -   **Cel:** Wydajne wyświetlanie dużej liczby niesparowanych archiwów.
    -   **Plan Działania:**
        1.  Zastąpić `QListWidget` przez `QListView`.
        2.  Stworzyć dedykowany model dziedziczący po `QAbstractListModel` (np. `UnpairedArchivesModel`), który będzie dostarczał dane do `QListView`.
        3.  Model ten będzie emitował sygnały `rowsInserted`, `rowsRemoved`, `dataChanged`, co pozwoli widokowi na inteligentne odświeżanie tylko zmienionych elementów.
        4.  `ArchiveListItem` zostanie zastąpiony przez `QStyledItemDelegate`, który będzie odpowiedzialny za rysowanie wyglądu pojedynczego elementu listy.

4.  **Modernizacja Zarządzania Ścieżkami i Danymi:**
    -   **Cel:** Użycie nowoczesnych, obiektowych i bezpiecznych typów.
    -   **Plan Działania:**
        1.  Zastąpić wszystkie stringi przechowujące ścieżki obiektami `pathlib.Path`.
        2.  Wprowadzić `dataclass` dla reprezentacji danych (np. `UnpairedArchiveData`, `UnpairedPreviewData`).
