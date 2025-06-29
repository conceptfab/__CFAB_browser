### ⚡ amv_controller.py - Analiza Wydajności

**Data analizy:** 29.06.2025

#### Krytyczne Problemy Wydajnościowe:

1.  **Nieefektywna Przebudowa Siatki UI (`_rebuild_asset_grid`):**
    -   **Problem:** To największy problem wydajnościowy w tej klasie. Metoda usuwa wszystkie istniejące widżety (`tile.deleteLater()`) i tworzy je od nowa przy każdej, nawet najmniejszej zmianie. Przy dużej liczbie assetów (np. >1000) prowadzi to do zamrożenia aplikacji, ogromnego zużycia pamięci i procesora.
    -   **Rekomendacja (KRYTYCZNA):** Należy całkowicie zrezygnować z tego podejścia i zaimplementować **wirtualne przewijanie (virtual scrolling)**. Widok powinien renderować tylko te kafelki, które są aktualnie widoczne w `QScrollArea`. W miarę przewijania, widżety, które znikają z widoku, powinny być reużywane (wzorzec Object Pooling) do wyświetlania nowych danych, zamiast być niszczone i tworzone na nowo.

2.  **Synchroniczne Operacje I/O w Głównym Wątku:**
    -   **Problem:** Metody takie jak `_on_tile_filename_clicked`, `_open_path_in_explorer` i `_open_path_in_default_app` używają blokujących wywołań `os.startfile()` i `subprocess.run()`. Jeśli aplikacja docelowa lub system plików działa wolno, interfejs użytkownika zostanie zablokowany.
    -   **Rekomendacja (WYSOKA):** Chociaż te operacje są zazwyczaj szybkie, dla pełnej responsywności powinny być wykonywane w osobnym wątku. Można użyć `QThread` lub `asyncio.to_thread` (w Python 3.9+), aby przenieść je z głównego wątku zdarzeń.

3.  **Brak Debouncingu dla Zdarzeń o Wysokiej Częstotliwości:**
    -   **Problem:** Sygnały takie jak `gallery_viewport_resized` (`_on_gallery_resized`) i `thumbnail_size_slider.valueChanged` (`_on_thumbnail_size_changed`) mogą być emitowane bardzo często (np. podczas przeciągania suwaka lub zmiany rozmiaru okna). Każda emisja wywołuje kosztowną operację przeliczania kolumn i aktualizacji wszystkich kafelków.
    -   **Rekomendacja (WYSOKA):** Należy zaimplementować mechanizm **debounce**. Zamiast reagować na każde zdarzenie, należy poczekać na krótką przerwę w emisji sygnałów (np. 150-250 ms) i dopiero wtedy wykonać kosztowną operację. Można to osiągnąć za pomocą `QTimer`.

4.  **Niepotrzebne Aktualizacje UI:**
    -   **Problem:** W `_rebuild_asset_grid` znajdują się wywołania `update()` i `repaint()`, które często są zbędne, ponieważ Qt inteligentnie zarządza odświeżaniem. Wymuszanie odświeżania może prowadzić do problemów z migotaniem i niepotrzebnego obciążenia.
    -   **Rekomendacja (ŚREDNIA):** Usunąć ręczne wywołania `update()` i `repaint()`, chyba że są absolutnie konieczne do rozwiązania konkretnego problemu z renderowaniem. Zdać się na wbudowane mechanizmy Qt.
