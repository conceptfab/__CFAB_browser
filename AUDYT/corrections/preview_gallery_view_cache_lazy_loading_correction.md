### 📄 core/amv_views/preview_gallery_view.py - Analiza Cache'owania i Lazy Loading

- **Status:** ✅ UKOŃCZONA ANALIZA
- **Data ukończenia:** niedziela, 29 czerwca 2025
- **Business impact:** `PreviewGalleryView` jest odpowiedzialny za wyświetlanie podglądów zasobów. Brak lazy loading i cache'owania prowadzi do wysokiego zużycia pamięci i spowolnienia UI, zwłaszcza przy dużej liczbie podglądów i częstych zmianach rozmiaru okna.
- **Performance impact:** KRYTYCZNY. Głównym problemem jest nieefektywne zarządzanie widżetami `PreviewTile`, które są całkowicie usuwane i ponownie tworzone przy każdej zmianie rozmiaru widoku. Brak lazy loading dla obrazów podglądu i brak cache'owania dla `PreviewTile` znacząco obniża wydajność.
- **Modernization priority:** KRYTYCZNE - Implementacja object pooling/virtual scrolling i wykorzystanie cache'owania miniatur jest niezbędna dla poprawy wydajności i płynności UI.
- **Bottlenecks found:**
  - **Brak Lazy Loading dla `PreviewTile`:** Wszystkie `PreviewTile` są tworzone i dodawane do układu, nawet jeśli nie są widoczne. To prowadzi do niepotrzebnego zużycia zasobów.
  - **Brak Cache'owania dla `PreviewTile`:** Instancje `PreviewTile` są niszczone i ponownie tworzone, zamiast być ponownie wykorzystywane. To generuje znaczne obciążenie dla systemu zarządzania pamięcią i garbage collectora.
  - **Brak Lazy Loading dla obrazów podglądu w `PreviewTile`:** (Zakładając, że `PreviewTile` ładuje obraz natychmiast). Wszystkie obrazy podglądu są ładowane do pamięci, nawet te niewidoczne.
- **Modernization needed:**
  - **Implementacja Object Pooling/Virtual Scrolling:** Zamiast usuwać i ponownie tworzyć `PreviewTile` przy każdej zmianie rozmiaru lub aktualizacji, należy zaimplementować mechanizm ponownego wykorzystania istniejących instancji (object pooling) lub renderowania tylko widocznych elementów (virtual scrolling). To będzie wymagało zarządzania pulą obiektów `PreviewTile` i aktualizowania ich zawartości, gdy stają się widoczne.
  - **Wykorzystanie Globalnego Cache Miniatur:** `PreviewTile` (który jest tworzony przez `PreviewGalleryView`) powinien pobierać miniatury z globalnego cache (np. `_thumbnail_cache` z `core/thumbnail.py`), zamiast ładować je bezpośrednio z dysku. Jeśli miniatury nie ma w cache, powinna zostać załadowana asynchronicznie (np. przez `ThumbnailLoaderWorker`), a `PreviewTile` powinien zostać zaktualizowany po jej załadowaniu.
  - **Wprowadzenie Type Hints:** Dla lepszej czytelności i utrzymania kodu.
