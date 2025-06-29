### ⚡ preview_tile.py - Analiza Wydajności

**Data analizy:** 29.06.2025

#### Krytyczne Problemy Wydajnościowe:

1.  **Synchroniczne Ładowanie Obrazu (KRYTYCZNY PRIORYTET):**
    -   **Problem:** Metoda `load_thumbnail` wywołuje `QPixmap(self.file_path)`. Ta operacja jest blokująca i odbywa się w głównym wątku UI. Dla dużych plików graficznych (np. wysokiej rozdzielczości podglądy), ładowanie obrazu może zająć dużo czasu i zablokować główny wątek UI, powodując zamrożenie aplikacji. Jest to szczególnie problematyczne, gdy wiele `PreviewTile` jest tworzonych jednocześnie (np. w `PreviewGalleryView`).
    -   **Rekomendacja (KRYTYCZNA):** Ładowanie obrazów musi odbywać się **asynchronicznie w tle**. Należy wykorzystać zmodernizowany `ThumbnailProcessor` (z modułu `thumbnail.py`) lub dedykowany `ImageLoader` (działający na `QThreadPool`). `PreviewTile` powinien najpierw wyświetlać placeholder (np. pusty obszar lub ikonę ładowania), a następnie wysyłać żądanie załadowania obrazu. Gdy obraz jest gotowy, loader emituje sygnał z gotowym `QPixmap`, a `PreviewTile` aktualizuje swój `QLabel`.

2.  **Brak Reużywania Obiektów (Object Pooling):**
    -   **Problem:** Każdy `PreviewTile` jest tworzony jako nowa instancja `QWidget` z własnymi pod-widżetami. W kontekście `PreviewGalleryView`, która czyści i tworzy wszystkie kafelki od nowa przy każdej aktualizacji, prowadzi to do ogromnego zużycia pamięci i procesora, powodując zacinanie się interfejsu i migotanie.
    -   **Rekomendacja (KRYTYCZNA):** `PreviewTile` powinien zostać zastąpiony przez `QStyledItemDelegate` (np. `PreviewTileDelegate`). Delegat nie tworzy pełnych widżetów, lecz rysuje wygląd pojedynczego elementu listy. `QListView` (który będzie używał tego delegata) jest zoptymalizowany do wyświetlania dużych zbiorów danych, renderując tylko widoczne elementy i reużywając delegaty. To jest klucz do osiągnięcia wydajności w galerii podglądów.

3.  **Nieefektywne Obliczanie Wysokości (`update_thumbnail_size`):**
    -   **Problem:** W metodzie `update_thumbnail_size`, wysokość kafelka jest obliczana dynamicznie na podstawie `sizeHint()` innych widżetów. Chociaż jest to poprawne, w połączeniu z synchronicznym ładowaniem miniatur i brakiem reużywania obiektów, dodaje to narzutu.
    -   **Rekomendacja (ŚREDNIA):** Po przejściu na `QStyledItemDelegate`, wysokość elementu będzie obliczana przez delegata w metodzie `sizeHint()`, co będzie bardziej efektywne i zintegrowane z systemem Qt Model/View.
