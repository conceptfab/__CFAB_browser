### ⚡ thumbnail_tile.py - Analiza Wydajności

**Data analizy:** 29.06.2025

#### Krytyczne Problemy Wydajnościowe:

1.  **Synchroniczne Ładowanie Obrazów (KRYTYCZNY PRIORYTET):**
    -   **Problem:** Zarówno `ThumbnailTile` (w `_create_placeholder_thumbnail`, `_load_texture_icon`, `load_thumbnail_from_cache`) jak i `FolderTile` (w `_load_folder_icon`) ładują obrazy (`QPixmap`) synchronicznie z dysku. Ta operacja jest blokująca i odbywa się w głównym wątku UI. Dla dużych plików graficznych lub wolnych dysków, ładowanie wielu miniatur jednocześnie (np. podczas przewijania galerii) może zająć dużo czasu i zablokować główny wątek UI, powodując zamrożenie aplikacji.
    -   **Rekomendacja (KRYTYCZNA):** Ładowanie obrazów musi odbywać się **asynchronicznie w tle**. Należy wykorzystać zmodernizowany `ThumbnailProcessor` (z modułu `thumbnail.py`) lub dedykowany `ImageLoader` (działający na `QThreadPool`). Kafelki powinny najpierw wyświetlać placeholder (np. pusty obszar lub ikonę ładowania), a następnie wysyłać żądanie załadowania obrazu. Gdy obraz jest gotowy, loader emituje sygnał z gotowym `QPixmap`, a kafelek aktualizuje swój `QLabel`.

2.  **Brak Reużywania Obiektów (Object Pooling) - KRYTYCZNY PRIORYTET:**
    -   **Problem:** Zarówno `ThumbnailTile` jak i `FolderTile` są tworzone jako nowe instancje `QWidget` z własnymi pod-widżetami. W kontekście galerii (np. `AssetTileView` w `amv_views/asset_tile_view.py`), która czyści i tworzy wszystkie kafelki od nowa przy każdej aktualizacji, prowadzi to do ogromnego zużycia pamięci i procesora, powodując zacinanie się interfejsu i migotanie.
    -   **Rekomendacja (KRYTYCZNA):** Te klasy powinny zostać zastąpione przez `QStyledItemDelegate` (np. `ThumbnailTileDelegate`, `FolderTileDelegate`). Delegat nie tworzy pełnych widżetów, lecz rysuje wygląd pojedynczego elementu listy. `QListView` (który będzie używał tych delegatów) jest zoptymalizowany do wyświetlania dużych zbiorów danych, renderując tylko widoczne elementy i reużywając delegaty. To jest klucz do osiągnięcia wydajności w galerii.

3.  **Nieefektywne Skalowanie Obrazów:**
    -   **Problem:** W metodzie `update_thumbnail_size` obraz jest skalowany od nowa przy każdej zmianie rozmiaru. Chociaż Qt jest zoptymalizowane, dla bardzo dużych obrazów i częstych zmian rozmiaru, może to być kosztowne.
    -   **Rekomendacja (ŚREDNIA):** Po przejściu na `QStyledItemDelegate`, skalowanie obrazu będzie zarządzane przez delegata, który może wykorzystać cache miniatur w różnych rozmiarach lub bardziej efektywne algorytmy skalowania.
