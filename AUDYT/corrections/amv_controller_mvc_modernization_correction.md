### 📄 core/amv_controllers/amv_controller.py - Analiza Modernizacji MVC

- **Status:** ✅ UKOŃCZONA ANALIZA
- **Data ukończenia:** niedziela, 29 czerwca 2025
- **Business impact:** `AmvController` jest centralnym punktem koordynacji między modelem a widokiem. Modernizacja jego struktury w kontekście MVC poprawi modularność, testowalność i elastyczność aplikacji.
- **Performance impact:** ŚREDNI. Modernizacja MVC dotyczy głównie struktury kodu i separacji odpowiedzialności. Jednak refaktoryzacja `_rebuild_asset_grid` będzie miała bezpośredni wpływ na wydajność UI.
- **Modernization priority:** WYSOKIE - Jest to kluczowy krok w modernizacji architektury MVC, zwłaszcza w kontekście optymalizacji wydajności UI.
- **Bottlenecks found:**
  - **Bezpośrednie tworzenie `AssetTileView` w `_rebuild_asset_grid`:** Kontroler bezpośrednio tworzy instancje `AssetTileView` w pętli. W kontekście object pooling, kontroler powinien zarządzać pulą tych obiektów, a nie tworzyć je od nowa za każdym razem.
  - **Dostęp do modeli poprzez `self.model`:** Kontroler ma wiele zależności do różnych modeli, do których uzyskuje dostęp poprzez `self.model`. Wstrzykiwanie tych zależności bezpośrednio do konstruktora kontrolera mogłoby poprawić testowalność i modularność.
- **Modernization needed:**
  - **Wstrzykiwanie zależności (Dependency Injection):** Kontroler powinien otrzymywać bezpośrednie referencje do potrzebnych modeli (np. `AssetGridModel`, `SelectionModel`, `FileOperationsModel`) w konstruktorze, zamiast dostępu poprzez `self.model`.
  - **Refaktoryzacja `_rebuild_asset_grid`:** Jest to najważniejszy punkt. Zmiana logiki tej metody, aby wykorzystywała object pooling/virtual scrolling zamiast ciągłego tworzenia/niszczenia widżetów. To będzie wymagało ścisłej współpracy z `AssetGridModel` i `AmvView`.
  - **Wprowadzenie Type Hints:** Dla lepszej czytelności i utrzymania kodu.
