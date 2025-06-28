### 🗺️ MAPA PLIKÓW FUNKCJONALNOŚCI BIZNESOWEJ

**Wygenerowano na podstawie aktualnego kodu: 2025-06-28**

**Odkryte katalogi z logiką biznesową:**

- core - Główna logika biznesowa aplikacji.
- core/amv_controllers - Kontrolery dla widoku AMV.
- core/amv_models - Modele danych dla widoku AMV.
- core/amv_views - Widoki dla AMV.

#### **core** (C:\_cloud\__CFAB_browser\core)
```
C:\_cloud\__CFAB_browser\core/
├── main_window.py ⚫⚫⚫⚫ - Orkiestrator aplikacji, zarządza konfiguracją i UI. - ✅ UKOŃCZONA ANALIZA (2025-06-28)
├── scanner.py ⚫⚫⚫⚫ - Główny algorym parowania zasobów. - ✅ UKOŃCZONA ANALIZA (2025-06-28)
├── amv_tab.py ⚫⚫⚫⚫ - Główny interfejs przeglądania zasobów. - ✅ UKOŃCZONA ANALIZA (2025-06-28)
├── thumbnail.py ⚫⚫⚫⚫ - Przetwarzanie obrazów i zarządzanie miniaturami. - ✅ UKOŃCZONA ANALIZA (2025-06-28)
├── folder_scanner_worker.py 🔴🔴🔴 - Skanowanie w tle, kluczowe dla wydajności UI. - ✅ UKOŃCZONA ANALIZA (2025-06-28)
├── json_utils.py 🟡🟡 - Narzędzia do obsługi JSON. - ✅ UKOŃCZONA ANALIZA (2025-06-28)
├── rules.py 🟡🟡 - Reguły. - ✅ UKOŃCZONA ANALIZA (2025-06-28)
├── thumbnail_tile.py 🟡🟡 - Widget kafelka. - ✅ UKOŃCZONA ANALIZA (2025-06-28)
├── pairing_tab.py 🟢 - Przyszła funkcjonalność. - ✅ UKOŃCZONA ANALIZA (2025-06-28)
└── tools_tab.py 🟢 - Przyszła funkcjonalność. - ✅ UKOŃCZONA ANALIZA (2025-06-28)
```

#### **amv_controllers** (C:\_cloud\__CFAB_browser\core\amv_controllers)
```
C:\_cloud\__CFAB_browser\core\amv_controllers/
└── amv_controller.py 🔴🔴🔴 - Kontroler dla widoku AMV, zarządza logiką. - ✅ UKOŃCZONA ANALIZA (2025-06-28)
```

#### **amv_models** (C:\_cloud\__CFAB_browser\core\amv_models)
```
C:\_cloud\__CFAB_browser\core\amv_models/
└── asset_grid_model.py 🔴🔴🔴 - Model dla siatki zasobów, zarządza danymi. - ✅ UKOŃCZONA ANALIZA (2025-06-28)
```

#### **amv_views** (C:\_cloud\__CFAB_browser\core\amv_views)
```
C:\_cloud\__CFAB_browser\core\amv_views/
└── amv_view.py 🔴🔴🔴 - Widok AMV, kluczowy dla UI. - ✅ UKOŃCZONA ANALIZA (2025-06-28)
```
