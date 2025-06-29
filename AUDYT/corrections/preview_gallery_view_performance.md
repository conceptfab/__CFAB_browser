### 📊 core/amv_views/preview_gallery_view.py - Analiza Wydajności

**Plik:** `core/amv_views/preview_gallery_view.py`

#### **Zidentyfikowane Bottlenecki Wydajnościowe:**

- **Krytyczne: Nieefektywne odświeżanie w `resizeEvent` i `set_previews`:**
  - **Opis:** Za każdym razem, gdy widok `PreviewGalleryView` zmienia rozmiar (np. użytkownik zmienia rozmiar okna aplikacji), metoda `resizeEvent` wywołuje `set_previews`. Ta metoda z kolei iteruje przez wszystkie istniejące `PreviewTile` w `gallery_layout`, usuwa je (`widget_to_remove.deleteLater()`), a następnie tworzy i dodaje nowe instancje `PreviewTile` dla każdego elementu na liście `preview_paths`.
  - **Wpływ:** Jest to operacja o bardzo wysokim koszcie obliczeniowym i pamięciowym. Powoduje to:
    - **Zacięcia UI:** Aplikacja staje się niereponsywna podczas zmiany rozmiaru okna, zwłaszcza przy dużej liczbie podglądów.
    - **Nadmierne obciążenie CPU:** Ciągłe tworzenie i niszczenie widżetów oraz ich układanie w `QGridLayout` zużywa dużo zasobów procesora.
    - **Wzrost zużycia pamięci:** Chociaż `deleteLater()` pomaga w zwolnieniu pamięci, ciągłe alokowanie i dealokowanie pamięci dla wielu obiektów `PreviewTile` (i ich wewnętrznych `QPixmap`) prowadzi do fragmentacji pamięci i obciążenia garbage collectora.
  - **Rekomendacja:** Zastosowanie mechanizmu `virtual scrolling` lub `object pooling` dla `PreviewTile`. Zamiast niszczyć i tworzyć widżety, należy je ponownie wykorzystywać, aktualizując ich zawartość.

- **Brak Lazy Loading dla obrazów podglądu:**
  - **Opis:** Chociaż `PreviewGalleryView` zarządza układem kafelków, to `PreviewTile` (który jest tworzony w pętli) jest odpowiedzialny za ładowanie obrazów. Jeśli `PreviewTile` ładuje obraz natychmiast po utworzeniu, to przy dużej liczbie podglądów wszystkie obrazy są ładowane do pamięci, nawet te niewidoczne.
  - **Wpływ:** Wysokie zużycie pamięci, wolniejsze ładowanie galerii, potencjalne zacięcia UI.
  - **Rekomendacja:** Implementacja lazy loading w `PreviewTile`, tak aby obraz był ładowany tylko wtedy, gdy kafelek staje się widoczny w obszarze scrollowania.

- **Nieoptymalne obliczanie kolumn w `get_columns_count`:**
  - **Opis:** Metoda `get_columns_count` oblicza liczbę kolumn na podstawie szerokości widoku i stałego `tile_width_with_margin`. Chociaż sama metoda nie jest kosztowna, jej częste wywoływanie w `resizeEvent` (poprzez `set_previews`) przyczynia się do ogólnego problemu wydajności.
  - **Wpływ:** Dodatkowe, niepotrzebne obliczenia.
  - **Rekomendacja:** Zoptymalizowanie wywołań `get_columns_count` i upewnienie się, że jest ona wywoływana tylko wtedy, gdy jest to absolutnie konieczne, np. z debouncingiem.

#### **Rekomendowane Działania Optymalizacyjne:**

1.  **Implementacja Virtual Scrolling/Object Pooling:**
    - Zmodyfikować `set_previews` tak, aby zarządzała pulą obiektów `PreviewTile`.
    - Tylko widoczne kafelki powinny być aktywne i wyświetlane. Kafelki poza widokiem powinny być ukrywane lub zwracane do puli.
2.  **Optymalizacja `resizeEvent`:**
    - Zmienić logikę `resizeEvent`, aby nie wywoływała pełnego przeładowania galerii. Powinna ona jedynie dostosowywać układ istniejących kafelków w `QGridLayout` lub zarządzać widocznością kafelków z puli.
3.  **Wdrożenie Lazy Loading w `PreviewTile`:**
    - Zapewnić, że obrazy podglądu są ładowane tylko wtedy, gdy `PreviewTile` jest widoczny.
4.  **Centralizacja Cache'owania Miniatur:**
    - Podobnie jak w `AssetTileView`, miniatury powinny być ładowane i cache'owane centralnie, aby uniknąć wielokrotnego ładowania tych samych obrazów.
