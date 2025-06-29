### 📄 core/amv_controllers/amv_controller.py - Analiza Dependency Injection

- **Status:** ✅ UKOŃCZONA ANALIZA
- **Data ukończenia:** niedziela, 29 czerwca 2025
- **Business impact:** `AmvController` jest odpowiedzialny za koordynację między modelem a widokiem. Wprowadzenie Dependency Injection poprawi modularność, testowalność i elastyczność kontrolera, ułatwiając zarządzanie zależnościami.
- **Performance impact:** NISKI. Wprowadzenie Dependency Injection dotyczy głównie struktury kodu i separacji odpowiedzialności, a nie bezpośrednio wydajności.
- **Modernization priority:** WYSOKIE - Jest to kluczowy krok w modernizacji architektury i przygotowaniu aplikacji na przyszłe zmiany w sposobie przechowywania danych i komponentów.
- **Bottlenecks found:**
  - **Brak bezpośredniego wstrzykiwania zależności dla podległych modeli:** Kontroler otrzymuje `AmvModel` w konstruktorze, ale dostęp do poszczególnych modeli (`asset_grid_model`, `control_panel_model`, itp.) odbywa się poprzez `self.model.<model_name>`. To silnie wiąże kontroler z wewnętrzną strukturą `AmvModel` i utrudnia testowanie.
- **Modernization needed:**
  - **Wstrzykiwanie bezpośrednich zależności:** Zamiast przekazywać cały `AmvModel` do `AmvController`, można przekazać tylko te modele, których kontroler faktycznie potrzebuje (np. `asset_grid_model`, `control_panel_model`, `file_operations_model`, `selection_model`, `drag_drop_model`, `asset_scanner_model`, `folder_system_model`).
  - **Użycie interfejsów (opcjonalnie, ale zalecane):** Jeśli zdefiniowano interfejsy dla modeli (np. `IAssetGridModel`), kontroler powinien przyjmować instancje tych interfejsów, a nie konkretne implementacje.
  - **Centralny kontener DI (w przyszłości):** W przyszłości, jeśli zostanie wprowadzony centralny kontener DI, to on będzie odpowiedzialny za tworzenie i wstrzykiwanie tych zależności.
  - **Wprowadzenie Type Hints:** Dla lepszej czytelności i utrzymania kodu.
