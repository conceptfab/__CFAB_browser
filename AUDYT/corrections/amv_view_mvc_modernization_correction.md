### 📄 core/amv_views/amv_view.py - Analiza Modernizacji MVC

- **Status:** ✅ UKOŃCZONA ANALIZA
- **Data ukończenia:** niedziela, 29 czerwca 2025
- **Business impact:** `AmvView` jest głównym widokiem aplikacji, odpowiedzialnym za prezentację interfejsu użytkownika. Modernizacja jego struktury w kontekście MVC poprawi modularność, testowalność i elastyczność UI.
- **Performance impact:** NISKI. Modernizacja MVC dotyczy głównie struktury kodu i separacji odpowiedzialności, a nie bezpośrednio wydajności. Jednak optymalizacja `remove_asset_tiles` będzie miała bezpośredni wpływ na wydajność.
- **Modernization priority:** WYSOKIE - Jest to kluczowy krok w modernizacji architektury MVC, zwłaszcza w kontekście optymalizacji wydajności UI.
- **Bottlenecks found:**
  - **Bezpośrednie tworzenie instancji widżetów:** `AmvView` bezpośrednio tworzy instancje niektórych widżetów (np. `CustomFolderTreeView`) w swoich metodach. Chociaż jest to typowe dla widoków PyQt, wstrzykiwanie tych zależności mogłoby zwiększyć elastyczność i testowalność.
  - **Nieefektywne usuwanie kafelków w `remove_asset_tiles`:** Metoda ta usuwa widżety `AssetTileView` z układu poprzez `deleteLater()`. W kontekście problemów z wydajnością zidentyfikowanych w `AssetTileView` i `PreviewGalleryView`, ta metoda powinna być zoptymalizowana, aby wykorzystywać object pooling lub virtual scrolling, zamiast niszczyć i ponownie tworzyć widżety.
- **Modernization needed:**
  - **Wstrzykiwanie zależności (Dependency Injection):** Zamiast tworzyć instancje widżetów (np. `CustomFolderTreeView`) bezpośrednio w `AmvView`, można by je wstrzykiwać jako argumenty konstruktora. To pozwoliłoby na łatwiejsze testowanie i elastyczność w konfiguracji.
  - **Optymalizacja `remove_asset_tiles`:** Ta metoda powinna zostać zrefaktoryzowana, aby wykorzystywać object pooling lub virtual scrolling, zamiast niszczyć i ponownie tworzyć widżety. To będzie wymagało ścisłej współpracy z `AmvController` i `AssetGridModel`.
  - **Wprowadzenie Type Hints:** Dla lepszej czytelności i utrzymania kodu.
