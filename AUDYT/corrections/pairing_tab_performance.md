### ⚡ pairing_tab.py - Analiza Wydajności

**Data analizy:** 29.06.2025

#### Krytyczne Problemy Wydajnościowe:

1.  **Blokujące Operacje I/O w Głównym Wątku (KRYTYCZNY PRIORYTET):**
    -   **Problem:** Metody takie jak `_on_archive_clicked` bezpośrednio wywołują `os.startfile` i `subprocess.Popen`. Te operacje są blokujące i mogą zamrozić interfejs użytkownika, jeśli zewnętrzna aplikacja uruchamia się wolno lub plik jest duży. Co ważniejsze, metody `_on_create_asset_button_clicked`, `_on_delete_unpaired_previews_clicked`, `_on_delete_unpaired_archives_clicked` i `_on_rebuild_assets_clicked` wywołują metody na `PairingModel` i `AssetRebuilderThread`, które z kolei wykonują długotrwałe operacje I/O (zapis/usuwanie plików, tworzenie miniatur, skanowanie). Wszystko to dzieje się synchronicznie w głównym wątku UI.
    -   **Rekomendacja (KRYTYCZNA):** Wszystkie operacje I/O muszą być przeniesione do wątków roboczych (`QThread`) lub zadań asynchronicznych (`asyncio.to_thread`). Widok powinien jedynie inicjować te operacje, a następnie natychmiast zwracać kontrolę do pętli zdarzeń. Postęp operacji powinien być raportowany za pomocą sygnałów, a UI aktualizowane na ich podstawie (np. wyświetlanie paska postępu, blokowanie przycisków).

2.  **Nieefektywne Odświeżanie Listy (`load_data`):**
    -   **Problem:** Metoda `load_data` jest wywoływana po każdej operacji (np. usunięciu plików, utworzeniu assetu). Czyści ona całą listę (`self.archive_list_widget.clear()`) i buduje ją od nowa, tworząc nowe instancje `ArchiveListItem` i `QListWidgetItem`. Dla dużej liczby niesparowanych plików (setki, tysiące) jest to bardzo nieefektywne, powoduje migotanie UI i zużywa dużo zasobów.
    -   **Rekomendacja (WYSOKA):** Należy zaimplementować mechanizm **wirtualnego przewijania** dla `QListWidget` lub, co jest bardziej zgodne z architekturą Qt, użyć `QListView` z dedykowanym modelem dziedziczącym po `QAbstractListModel`. Model powinien emitować sygnały o zmianach (dodanie/usunięcie elementów), a widok powinien reagować na te sygnały, aktualizując tylko zmienione elementy, zamiast przebudowywać całą listę.

3.  **Nadmiarowe Wywołania `_update_create_asset_button_state`:**
    -   **Problem:** Metoda `_update_create_asset_button_state` jest wywoływana po każdej drobnej zmianie stanu (np. zaznaczeniu archiwum, zaznaczeniu podglądu). Chociaż sama metoda jest szybka, jej częste wywoływanie może być niepotrzebne.
    -   **Rekomendacja (NISKA):** Można zastosować mechanizm debounce, aby wywoływać tę metodę tylko raz po serii szybkich zmian, ale w tym przypadku wpływ na wydajność jest minimalny.
