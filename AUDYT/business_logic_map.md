### 🗺️ MAPA PLIKÓW FUNKCJONALNOŚCI BIZNESOWEJ

**Wygenerowano na podstawie aktualnego kodu: sobota, 28 czerwca 2025**

**Odkryte katalogi z logiką biznesową:**

- core/ - Główna logika biznesowa aplikacji, orkiestracja, skanowanie, operacje na plikach.
- core/amv_controllers/ - Kontrolery łączące modele z widokami, obsługa interakcji użytkownika.
- core/amv_models/ - Modele danych i logiki biznesowej dla zakładki AMV.
- core/amv_views/ - Widoki i komponenty UI (niektóre z wbudowaną logiką biznesową).

#### **core/** (core/)

core/
├── amv_tab.py ⚫⚫⚫⚫ - Główna klasa zakładki AMV, inicjalizuje komponenty MVC.

### 📄 amv_tab.py

- **Status:** ✅ UKOŃCZONA ANALIZA
- **Data ukończenia:** 2025-06-28
- **Business impact:** Plik pełni rolę orkiestratora komponentów MVC. Analiza wykazała, że jego struktura jest poprawna i nie wymaga bezpośrednich zmian.
- **Pliki wynikowe:**
  - `AUDYT/corrections/amv_tab_correction.md`
  - `AUDYT/patches/amv_tab_patch_code.md`
    ├── folder_scanner_worker.py 🔴🔴🔴 - Worker do skanowania struktury folderów i wykrywania plików asset.

### 📄 folder_scanner_worker.py

- **Status:** ✅ UKOŃCZONA ANALIZA
- **Data ukończenia:** 2025-06-28
- **Business impact:** Refaktoryzacja poprawiła separację odpowiedzialności poprzez delegowanie skanowania assetów do AssetScannerModelMV. FolderStructureScanner teraz skupia się wyłącznie na skanowaniu struktury folderów, co poprawia maintainability i testowanie kodu. Zmiana zachowuje 100% kompatybilność wsteczną.
- **Pliki wynikowe:**
  - `AUDYT/corrections/folder_scanner_worker_correction.md`
  - `AUDYT/patches/folder_scanner_worker_patch_code.md`
    ├── json_utils.py 🟡🟡 - Funkcje pomocnicze do serializacji/deserializacji JSON.
    ├── main_window.py ⚫⚫⚫⚫ - Główne okno aplikacji, ładowanie konfiguracji, tworzenie tabów.

### 📄 main_window.py

- **Status:** ✅ UKOŃCZONA ANALIZA
- **Data ukończenia:** 2025-06-28
- **Business impact:** Plik jest odpowiedzialny za inicjalizację głównego okna aplikacji, ładowanie konfiguracji i tworzenie zakładek. Analiza wykazała, że jego struktura jest poprawna i nie wymaga bezpośrednich zmian.
- **Pliki wynikowe:**
  - `AUDYT/corrections/main_window_correction.md`
  - `AUDYT/patches/main_window_patch_code.md`
    ├── pairing_tab.py 🟢 - Placeholder dla przyszłej funkcjonalności parowania.
    ├── preview_window.py 🟡🟡 - Wyświetla podglądy obrazów w osobnym oknie dialogowym.
    ├── rules.py ⚫⚫⚫⚫ - Zawiera logikę decyzyjną dla interakcji z folderami (scanner/galeria).

### 📄 rules.py

- **Status:** ✅ UKOŃCZONA ANALIZA
- **Data ukończenia:** 2025-06-28
- **Business impact:** Plik zawiera kluczową logikę decyzyjną dla aplikacji. Analiza wykazała, że kod jest dobrze zorganizowany, ale wymaga drobnych optymalizacji i poprawek stylistycznych (przeniesienie importu `time`, uproszczenie tworzenia słowników błędów).
- **Pliki wynikowe:**
  - `AUDYT/corrections/rules_correction.md`
  - `AUDYT/patches/rules_patch_code.md`
    ├── scanner.py ⚫⚫⚫⚫ - Główna logika biznesowa skanowania folderów, parowania plików, tworzenia assetów i miniatur.

### 📄 scanner.py

- **Status:** ✅ UKOŃCZONA ANALIZA
- **Data ukończenia:** 2025-06-28
- **Business impact:** Plik zawiera kluczową logikę biznesową skanowania folderów, parowania plików, tworzenia assetów i miniatur. Analiza wykazała, że kod jest solidny, ale wymaga drobnych optymalizacji i poprawek stylistycznych (uproszczenie wyszukiwania plików, usunięcie nieużywanego importu, optymalizacja logowania).
- **Pliki wynikowe:**
  - `AUDYT/corrections/scanner_correction.md`
  - `AUDYT/patches/scanner_patch_code.md`
    ├── thumbnail.py ⚫⚫⚫⚫ - Obsługuje przetwarzanie obrazów i zarządzanie miniaturami (generowanie, cache, walidacja).

### 📄 thumbnail.py

- **Status:** ✅ UKOŃCZONA ANALIZA
- **Data ukończenia:** 2025-06-28
- **Business impact:** Plik jest krytyczny dla wydajności UI i wizualizacji assetów poprzez zarządzanie miniaturami. Refaktoryzacja uściśliła obsługę wyjątków w trzech kluczowych miejscach: `_save_thumbnail_atomic`, `_is_cache_valid` i `clear_thumbnail_cache`, co poprawia debugowanie i stabilność aplikacji bez wpływu na funkcjonalność.
- **Pliki wynikowe:**
  - `AUDYT/corrections/thumbnail_correction.md`
  - `AUDYT/patches/thumbnail_patch_code.md`
    ├── thumbnail_tile.py 🔴🔴🔴 - Komponent UI do wyświetlania miniatur assetów i folderów, obsługa drag & drop.
    └── tools_tab.py 🟢 - Placeholder dla przyszłych narzędzi.

#### **core/amv_controllers/** (core/amv_controllers/)

core/amv_controllers/
└── amv_controller.py ⚫⚫⚫⚫ - Kontroler dla zakładki AMV, łączy model z widokiem, obsługuje interakcje użytkownika, orkiestruje operacje.

### 📄 amv_controller.py

- **Status:** ✅ UKOŃCZONA ANALIZA
- **Data ukończenia:** 2025-06-28
- **Business impact:** Plik jest odpowiedzialny za orkiestrację komponentów MVC i obsługę interakcji użytkownika. Analiza wykazała, że kod jest dobrze zorganizowany, ale wymaga usunięcia nieużywanego importu `shutil`.
- **Pliki wynikowe:**
  - `AUDYT/corrections/amv_controller_correction.md`
  - `AUDYT/patches/amv_controller_patch_code.md`

#### **core/amv_models/** (core/amv_models/)

core/amv_models/
├── amv_model.py ⚫⚫⚫⚫ - Główny model dla zakładki AMV, agreguje inne modele i zarządza ogólnym stanem.

### 📄 amv_model.py

- **Status:** ✅ UKOŃCZONA ANALIZA
- **Data ukończenia:** 2025-06-28
- **Business impact:** Plik jest odpowiedzialny za agregację innych modeli i zarządzanie ogólnym stanem aplikacji. Analiza wykazała, że kod jest dobrze zorganizowany, ale wymaga usunięcia nieużywanego importu `AssetTileModel` oraz uściślenia logowania w przypadku błędu inicjalizacji.
- **Pliki wynikowe:**
  - `AUDYT/corrections/amv_model_correction.md`
  - `AUDYT/patches/amv_model_patch_code.md`
    ├── asset_grid_model.py 🔴🔴🔴 - Zarządza danymi assetów wyświetlanych w siatce, ładowanie, filtrowanie, sortowanie, przeliczanie kolumn.
    ├── asset_tile_model.py 🟡🟡 - Model danych dla pojedynczego kafelka assetu, przechowuje dane i zarządza stanem zaznaczenia.
    ├── config_manager_model.py 🔴🔴🔴 - Zarządza konfiguracją aplikacji, ładowanie, przechowywanie i udostępnianie ustawień.
    ├── control_panel_model.py 🟡🟡 - Model danych dla panelu kontrolnego, zarządza paskiem postępu, rozmiarem miniatur i stanem zaznaczenia.
    ├── drag_drop_model.py 🔴🔴🔴 - Zarządza logiką operacji przeciągnij i upuść.
    ├── file_operations_model.py ⚫⚫⚫⚫ - Odpowiedzialny za operacje na plikach (przenoszenie, usuwanie) w osobnym wątku.

### 📄 file_operations_model.py

- **Status:** ✅ UKOŃCZONA ANALIZA
- **Data ukończenia:** 2025-06-28
- **Business impact:** Plik jest odpowiedzialny za operacje na plikach (przenoszenie, usuwanie) w osobnym wątku. Analiza wykazała, że kod zawiera błędy logiczne w aktualizacji metadanych assetów po przeniesieniu oraz kruche parsowanie komunikatów, co wymaga poprawek.
- **Pliki wynikowe:**
  - `AUDYT/corrections/file_operations_model_correction.md`
  - `AUDYT/patches/file_operations_model_patch_code.md`
    ├── folder_system_model.py 🔴🔴🔴 - Zarządza strukturą folderów i ich stanem w drzewie.
    └── selection_model.py 🟡🟡 - Zarządza zaznaczeniem assetów.
    └── workspace_folders_model.py 🟡🟡 - Zarządza listą folderów roboczych z konfiguracji.

#### **core/amv_views/** (core/amv_views/)

core/amv_views/
├── amv_view.py 🔴🔴🔴 - Główny widok dla zakładki AMV, zawiera elementy UI i obsługuje ich układ.
├── asset_tile_view.py 🟡🟡 - Widok dla pojedynczego kafelka assetu, wyświetla miniaturkę i informacje.
├── folder_tree_view.py 🟡🟡 - Widok drzewa folderów, wyświetla hierarchiczną strukturę.
└── gallery_widgets.py 🟡🟡 - Zawiera widgety używane w galerii, takie jak kontener dla kafelków.

### 🎯 DYNAMICZNE PRIORYTETY ANALIZY

**Wygenerowano na podstawie analizy kodu i kontekstu biznesowego: sobota, 28 czerwca 2025**

#### **⚫⚫⚫⚫ KRYTYCZNE** - Podstawowa funkcjonalność aplikacji

**Uzasadnienie:** Te elementy implementują główne algorytmy biznesowe, są odpowiedzialne za wydajność krytycznych procesów, zarządzają głównymi danymi biznesowymi, są częścią UI krytycznego dla UX lub orkiestrują kluczowe operacje.

- `core/amv_tab.py` - Główny punkt wejścia dla zakładki AMV, inicjalizuje całą logikę i widoki.
- `core/main_window.py` - Główny punkt wejścia aplikacji, zarządza konfiguracją i strukturą.
- `core/rules.py` - Implementuje kluczową logikę decyzyjną dla interakcji z folderami.
- `core/scanner.py` - Realizuje podstawowy proces biznesowy skanowania, parowania i tworzenia assetów.
- `core/thumbnail.py` - Krytyczny dla wydajności UI i wizualizacji assetów poprzez zarządzanie miniaturami.
- `core/amv_controllers/amv_controller.py` - Orkiestruje większość interakcji użytkownika i procesów biznesowych w zakładce AMV.
- `core/amv_models/amv_model.py` - Agreguje i zarządza stanem wszystkich podmodeli AMV.
- `core/amv_models/file_operations_model.py` - Odpowiedzialny za bezpieczne operacje na plikach użytkownika (przenoszenie, usuwanie).

#### **🔴🔴🔴 WYSOKIE** - Ważne operacje biznesowe

**Uzasadnienie:** Te elementy implementują ważne operacje biznesowe, zarządzają cache i optymalizacjami, są częścią serwisów biznesowych lub wpływają na wydajność, ale nie są krytyczne dla podstawowej funkcjonalności.

- `core/folder_scanner_worker.py` - Wykonuje skanowanie folderów w tle, co jest kluczowe dla responsywności.
- `core/thumbnail_tile.py` - Bezpośredni komponent UI dla assetów, w tym obsługa drag & drop.
- `core/amv_models/asset_grid_model.py` - Zarządza danymi i układem siatki assetów, wpływając na wydajność wyświetlania.
- `core/amv_models/config_manager_model.py` - Zarządza konfiguracją, która wpływa na wiele aspektów działania aplikacji.
- `core/amv_models/drag_drop_model.py` - Implementuje kluczową interakcję użytkownika (przeciągnij i upuść).
- `core/amv_models/folder_system_model.py` - Zarządza strukturą nawigacji folderów.
- `core/amv_views/amv_view.py` - Główny widok, który integruje wszystkie komponenty UI zakładki AMV.

#### **🟡🟡 ŚREDNIE** - Funkcjonalności pomocnicze

**Uzasadnienie:** Te elementy implementują funkcjonalności pomocnicze, są częścią systemu, ale nie krytyczne, zarządzają konfiguracją i walidacją, lub są komponentami UI bez złożonej logiki biznesowej.

- `core/json_utils.py` - Narzędzia do obsługi JSON, wspierające ładowanie/zapisywanie danych.
- `core/preview_window.py` - Okno podglądu, wspierające UX, ale nie kluczowe dla zarządzania assetami.
- `core/amv_models/asset_tile_model.py` - Model danych dla pojedynczego kafelka, reprezentacja danych.
- `core/amv_models/control_panel_model.py` - Zarządza stanem panelu kontrolnego, wpływając na interakcję, ale nie na podstawowe procesy.
- `core/amv_models/selection_model.py` - Zarządza zaznaczeniem, wspierając operacje na wielu assetach.
- `core/amv_models/workspace_folders_model.py` - Zarządza listą folderów roboczych.
- `core/amv_views/asset_tile_view.py` - Widok dla pojedynczego kafelka, prezentacja danych.
- `core/amv_views/folder_tree_view.py` - Widok drzewa folderów, prezentacja struktury.
- `core/amv_views/gallery_widgets.py` - Ogólne widgety galerii.

#### **🟢 NISKIE** - Funkcjonalności dodatkowe

**Uzasadnienie:** Te elementy implementują funkcjonalności dodatkowe, są odpowiedzialne za logowanie, narzędzia, lub nie mają bezpośredniego wpływu na procesy biznesowe.

- `core/pairing_tab.py` - Placeholder, brak zaimplementowanej logiki biznesowej.
- `core/tools_tab.py` - Placeholder, brak zaimplementowanej logiki biznesowej.

#### **📈 METRYKI PRIORYTETÓW**

**Na podstawie analizy kodu:**

- **Plików krytycznych:** 8
- **Plików wysokich:** 7
- **Plików średnich:** 9
- **Plików niskich:** 2
- **Łącznie przeanalizowanych:** 26

**Rozkład priorytetów:**

- Krytyczne: 30.77%
- Wysokie: 26.92%
- Średnie: 34.62%
- Niskie: 7.69%
