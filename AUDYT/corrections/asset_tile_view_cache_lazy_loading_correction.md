### 📄 core/amv_views/asset_tile_view.py - Analiza Cache'owania i Lazy Loading

- **Status:** ✅ UKOŃCZONA ANALIZA
- **Data ukończenia:** niedziela, 29 czerwca 2025
- **Business impact:** `AssetTileView` jest widokiem dla pojedynczego kafelka assetu. Brak lazy loading i cache'owania miniatur prowadzi do wysokiego zużycia pamięci i spowolnienia UI, zwłaszcza przy przewijaniu dużych galerii.
- **Performance impact:** KRYTYCZNY. Miniatury są ładowane i skalowane natychmiast po utworzeniu `AssetTileView`, co jest nieefektywne w scenariuszu `virtual scrolling`. Brak cache'owania powoduje wielokrotne ładowanie tych samych obrazów z dysku.
- **Modernization priority:** KRYTYCZNE - Implementacja lazy loading i wykorzystanie cache'owania miniatur jest niezbędna dla poprawy wydajności i płynności UI.
- **Bottlenecks found:**
  - **Brak Lazy Loading dla miniatur:** Miniatury są ładowane i skalowane natychmiast po utworzeniu `AssetTileView` w metodzie `_setup_asset_tile_ui`. W scenariuszu `virtual scrolling`, gdzie wiele kafelków jest tworzonych, ale tylko część jest widoczna, jest to nieefektywne.
  - **Brak Cache'owania miniatur:** Każda instancja `AssetTileView` ładuje miniaturę niezależnie, nawet jeśli ta sama miniatura jest już wyświetlana w innym kafelku lub została niedawno załadowana. Prowadzi to do zbędnych operacji I/O i przetwarzania obrazów.
- **Modernization needed:**
  - **Implementacja Lazy Loading dla miniatur:** Miniatura powinna być ładowana tylko wtedy, gdy kafelek staje się widoczny w obszarze scrollowania. Może to wymagać opóźnionego ładowania obrazu w `_setup_asset_tile_ui` lub `update_ui`, wywołując dedykowaną funkcję ładowania miniatury, która sprawdzi, czy kafelek jest widoczny.
  - **Wykorzystanie Globalnego Cache Miniatur:** `AssetTileView` powinien pobierać miniatury z globalnego cache (np. `_thumbnail_cache` z `core/thumbnail.py`), zamiast ładować je bezpośrednio z dysku. Jeśli miniatury nie ma w cache, powinna zostać załadowana asynchronicznie (np. przez `ThumbnailLoaderWorker`), a `AssetTileView` powinien zostać zaktualizowany po jej załadowaniu.
  - **Wprowadzenie Type Hints:** Dla lepszej czytelności i utrzymania kodu.
