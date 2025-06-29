### 🗺️ MAPA PLIKÓW FUNKCJONALNOŚCI BIZNESOWEJ - ANALIZA WYDAJNOŚCI

**Wygenerowano na podstawie aktualnego kodu: 29.06.2025**

**Odkryte katalogi z logiką biznesową:**

- `core/amv_controllers` - Kontrolery aplikacji, zarządzanie interakcjami użytkownika. - 🚀 PERFORMANCE CRITICAL
- `core/amv_models` - Modele danych, logika biznesowa i operacje na danych. - 🧠 MEMORY INTENSIVE
- `core/amv_views` - Widoki, renderowanie interfejsu użytkownika. - 🎨 UI RENDERING
- `core` - Główne komponenty aplikacji i operacje I/O. - 🔄 I/O OPERATIONS

#### **core/amv_controllers** (F:/__CFAB_browser/core/amv_controllers) - 🚀 PERFORMANCE CRITICAL
F:/__CFAB_browser/core/amv_controllers/
├── amv_controller.py ⚫⚫⚫⚫ KRYTYCZNE - Główny kontroler aplikacji, wymaga async operations.

**Zidentyfikowane bottlenecki:**
- Brak asynchronicznych operacji w głównym kontrolerze.

**Rekomendowane modernizacje:**
- Wprowadzenie `asyncio` i konwersja blokujących operacji na asynchroniczne.

#### **core/amv_models** (F:/__CFAB_browser/core/amv_models) - 🧠 MEMORY INTENSIVE
F:/__CFAB_browser/core/amv_models/
├── asset_grid_model.py ⚫⚫⚫⚫ KRYTYCZNE - Model siatki zasobów, wymaga lazy loading i cache.
├── asset_tile_model.py 🔴🔴🔴 WYSOKIE - Model kafelka zasobu.
├── config_manager_model.py 🟡🟡 ŚREDNIE - Zarządzanie konfiguracją.
├── control_panel_model.py 🟡🟡 ŚREDNIE - Model panelu kontrolnego.
├── drag_drop_model.py 🔴🔴🔴 WYSOKIE - Model przeciągnij i upuść.
├── file_operations_model.py 🔴🔴🔴 WYSOKIE - Operacje na plikach, wymaga progress tracking.
├── pairing_model.py 🔴🔴🔴 WYSOKIE - Model parowania.
└── selection_model.py 🔴🔴🔴 WYSOKIE - Zarządzanie zaznaczeniem, wymaga batch operations.

**Zidentyfikowane bottlenecki:**
- Brak lazy loading i cache w `AssetGridModel`.
- Potencjalnie blokujące operacje na plikach w `FileOperationsModel`.

**Rekomendowane modernizacje:**
- Implementacja lazy loading i LRU cache w `AssetGridModel`.
- Przeniesienie operacji plikowych do osobnych wątków z mechanizmem śledzenia postępu.

#### **core/amv_views** (F:/__CFAB_browser/core/amv_views) - 🎨 UI RENDERING
F:/__CFAB_browser/core/amv_views/
├── asset_tile_view.py ⚫⚫⚫⚫ KRYTYCZNE - Główny komponent renderowania, wymaga virtual scrolling.
├── folder_tree_view.py ⚫⚫⚫⚫ KRYTYCZNE - Drzewo folderów, wymaga debounced expansion.
├── gallery_widgets.py 🟡🟡 ŚREDNIE - Widżety galerii.
├── preview_gallery_view.py 🟡🟡 ŚREDNIE - Widok galerii podglądu.
└── preview_tile.py 🟡🟡 ŚREDNIE - Kafelek podglądu.

**Zidentyfikowane bottlenecki:**
- Brak wirtualnego przewijania w `AssetTileView`.
- Brak debouncingu przy rozwijaniu drzewa folderów w `FolderTreeView`.

**Rekomendowane modernizacje:**
- Implementacja wirtualnego przewijania dla `AssetTileView`.
- Dodanie mechanizmu debounce dla zdarzeń rozwijania w `FolderTreeView`.

#### **core** (F:/__CFAB_browser/core) - 🔄 I/O OPERATIONS
F:/__CFAB_browser/core/
├── folder_scanner_worker.py 🔴🔴🔴 WYSOKIE - Skaner folderów, operacje I/O.
├── main_window.py 🔴🔴🔴 WYSOKIE - Główne okno aplikacji.
├── pairing_tab.py 🔴🔴🔴 WYSOKIE - Zakładka parowania.
├── preview_window.py 🟡🟡 ŚREDNIE - Okno podglądu.
├── scanner.py 🔴🔴🔴 WYSOKIE - Skaner, operacje I/O.
├── thumbnail.py 🔴🔴🔴 WYSOKIE - Przetwarzanie miniaturek, wymaga background processing.
└── thumbnail_tile.py 🔴🔴🔴 WYSOKIE - Kafelek miniaturki.

**Zidentyfikowane bottlenecki:**
- Synchroniczne operacje I/O w `folder_scanner_worker.py` i `scanner.py`.
- Przetwarzanie miniaturek w głównym wątku.

**Rekomendowane modernizacje:**
- Przeniesienie operacji I/O do osobnych wątków.
- Przetwarzanie miniaturek w tle z wykorzystaniem `QThreadPool`.
