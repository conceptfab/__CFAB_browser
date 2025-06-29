### ⚡ preview_gallery_view.py - Analiza Wydajności

**Data analizy:** 29.06.2025

#### Krytyczne Problemy Wydajnościowe:

1.  **Brak Wirtualnego Przewijania i Reużywania Obiektów (KRYTYCZNY PRIORYTET):**
    -   **Problem:** Największym problemem wydajnościowym jest to, że metoda `set_previews` czyści wszystkie istniejące kafelki (`widget_to_remove.deleteLater()`) i tworzy je od nowa przy każdej aktualizacji. To samo dzieje się w `resizeEvent`. Dla dużej liczby podglądów (setki, tysiące) prowadzi to do:
        -   **Ogromnego zużycia pamięci:** Wszystkie `PreviewTile` i ich wewnętrzne widżety są tworzone i przechowywane w pamięci, nawet jeśli nie są widoczne.
        -   **Spadku płynności UI:** Ciągłe tworzenie i niszczenie widżetów powoduje zacinanie się interfejsu i migotanie, zwłaszcza podczas przewijania lub zmiany rozmiaru okna.
        -   **Nadmiernego obciążenia procesora:** Proces tworzenia i inicjalizacji widżetów jest kosztowny.
    -   **Rekomendacja (KRYTYCZNA):** Należy całkowicie przeprojektować ten widok, aby wykorzystywał wzorzec **Model-View-Delegate** z `QListView` i `QAbstractListModel`. `QListView` jest zoptymalizowany do wyświetlania dużych zbiorów danych, renderując tylko widoczne elementy i reużywając delegaty. `PreviewTile` powinien zostać zastąpiony przez `QStyledItemDelegate`, który będzie odpowiedzialny za rysowanie wyglądu pojedynczego elementu listy, a nie za tworzenie pełnego widżetu.

2.  **Synchroniczne Ładowanie Miniatur w `PreviewTile` (KRYTYCZNY PRIORYTET):**
    -   **Problem:** `PreviewTile` (który jest tworzony w `PreviewGalleryView`) ładuje miniatury synchronicznie. Jeśli w galerii jest wiele podglądów, a miniatury nie są w cache'u lub są duże, ładowanie ich wszystkich naraz zablokuje UI.
    -   **Rekomendacja (KRYTYCZNA):** Ładowanie miniatur musi odbywać się **asynchronicznie w tle** (np. za pomocą `QThreadPool` i `ThumbnailLoaderWorker` z modułu `thumbnail.py`). `PreviewTile` (lub jego odpowiednik w delegacie) powinien wyświetlać placeholder, a następnie asynchronicznie ładować miniaturę. Po załadowaniu, widok powinien być odświeżany.

3.  **Nieefektywne Obliczanie Kolumn:**
    -   **Problem:** Metoda `get_columns_count` jest wywoływana przy każdej zmianie rozmiaru, a następnie `set_previews` jest wywoływane, co prowadzi do pełnej przebudowy galerii. Obliczenia są również oparte na przybliżonych wartościach (`+ 20`).
    -   **Rekomendacja (WYSOKA):** Po przejściu na `QListView`, liczba kolumn będzie zarządzana przez layout widoku (np. `QGridLayout` w `QListView`), a nie przez ręczne obliczenia. Zmiana rozmiaru widoku powinna automatycznie dostosowywać layout bez konieczności ręcznej przebudowy wszystkich elementów.
