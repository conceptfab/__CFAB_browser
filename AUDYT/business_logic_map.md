### 🗺️ MAPA PLIKÓW FUNKCJONALNOŚCI BIZNESOWEJ

**Wygenerowano na podstawie aktualnego kodu: 2024-05-22**

**Odkryte katalogi z logiką biznesową:**

- `.` - Główny plik uruchomieniowy aplikacji.
- `core` - Rdzeń aplikacji, zawiera główną logikę biznesową oraz komponenty interfejsu użytkownika.
- `__tools` - Narzędzia pomocnicze i skrypty automatyzujące.

#### **Główny katalog** (`./`)

```
./
└── cfab_browser.py 🔴🔴🔴 WYSOKIE - Punkt startowy aplikacji, odpowiedzialny za inicjalizację głównego okna i wczytanie konfiguracji.
```

#### **Rdzeń aplikacji** (`core/`)

```
core/
├── main_window.py ⚫⚫⚫⚫ KRYTYCZNE - [Zarządzanie konfiguracją i cyklem życia aplikacji]
├── scanner.py ⚫⚫⚫⚫ KRYTYCZNE - [Kluczowy moduł do parowania plików i tworzenia metadanych]
├── gallery_tab.py ⚫⚫⚫⚫ KRYTYCZNE - Główny komponent UI do przeglądania zasobów, zarządzania siatką kafelków i skanowania w tle. Krytyczny dla UX.
├── thumbnail.py ⚫⚫⚫⚫ KRYTYCZNE - Odpowiedzialny za przetwarzanie obrazów, generowanie i cache'owanie miniatur. Kluczowy dla wydajności wizualnej.
├── thumbnail_tile.py 🔴🔴🔴 WYSOKIE - Komponent UI reprezentujący pojedynczy kafelek w galerii. Ważny dla interakcji z użytkownikiem.
├── folder_scanner_worker.py 🔴🔴🔴 WYSOKIE - Worker działający w tle do skanowania folderów, zapewnia responsywność UI podczas operacji I/O.
├── rules.py 🔴🔴🔴 WYSOKIE - Zawiera reguły biznesowe wykorzystywane w różnych częściach aplikacji.
├── tools_tab.py 🟢 NISKIE - Placeholder na przyszłe narzędzia. Obecnie niska istotność.
├── pairing_tab.py 🟢 NISKIE - Placeholder na przyszłe narzędzia do parowania. Obecnie niska istotność.
└── __init__.py 🟢 NISKIE - Plik inicjalizacyjny pakietu.
```

#### **Narzędzia** (`__tools/`)

```
__tools/
├── add_texture.py 🟢 NISKIE - Skrypt pomocniczy.
├── blend_move.py 🟢 NISKIE - Skrypt pomocniczy.
├── blend_zip.py 🟢 NISKIE - Skrypt pomocniczy.
├── clear_space.py 🟢 NISKIE - Skrypt pomocniczy.
├── compress_max.py 🟢 NISKIE - Skrypt pomocniczy.
├── copy_texture.py 🟢 NISKIE - Skrypt pomocniczy.
├── remove_folder_suffix.py 🟢 NISKIE - Skrypt pomocniczy.
├── rename_files.py 🟢 NISKIE - Skrypt pomocniczy.
├── supply_tex.py 🟢 NISKIE - Skrypt pomocniczy.
└── __clean_cache.py 🟢 NISKIE - Skrypt do czyszczenia cache.
```

### 🎯 DYNAMICZNE PRIORYTETY ANALIZY

**Wygenerowano na podstawie analizy kodu i kontekstu biznesowego: 2024-05-22**

#### ⚫⚫⚫⚫ KRYTYCZNE - Podstawowa funkcjonalność aplikacji

**Uzasadnienie:** Te pliki zawierają logikę, która jest absolutnie niezbędna do działania podstawowych funkcji aplikacji, takich jak skanowanie, przetwarzanie danych i wyświetlanie głównego interfejsu. Błędy lub niska wydajność w tych modułach mają bezpośredni, krytyczny wpływ na użytkownika.

- `core/main_window.py` - ✅ **Analiza ukończona.** Jako główny orkiestrator, zarządza całym cyklem życia aplikacji.
- `core/scanner.py` - ✅ **Analiza ukończona.** Implementuje kluczowy proces biznesowy parowania zasobów, który jest fundamentem działania programu.
- `core/gallery_tab.py` - Odpowiada za główny interfejs użytkownika; jego wydajność i stabilność są kluczowe dla UX.
- `core/thumbnail.py` - Krytyczny dla wydajności moduł obsługujący generowanie i cache'owanie miniatur, co jest podstawą galerii.

#### 🔴🔴🔴 WYSOKIE - Ważne operacje biznesowe

**Uzasadnienie:** Komponenty o wysokim priorytecie są kluczowe dla płynności działania, responsywności interfejsu i integralności danych. Nie są one fundamentem architektury, ale ich nieprawidłowe działanie znacząco pogorszy doświadczenie użytkownika.

- `cfab_browser.py` - Punkt wejścia aplikacji, inicjalizuje krytyczne komponenty.
- `core/thumbnail_tile.py` - Bezpośrednio wpływa na interakcję użytkownika z danymi w galerii.
- `core/folder_scanner_worker.py` - Zapewnia responsywność UI podczas długotrwałych operacji I/O.
- `core/rules.py` - Centralne miejsce dla reguł biznesowych, wpływające na spójność przetwarzania danych.

#### 🟡🟡 ŚREDNIE - Funkcjonalności pomocnicze

**Uzasadnienie:** W tej analizie nie zidentyfikowano plików o średnim priorytecie. Logika aplikacji jest wyraźnie podzielona na krytyczne komponenty główne i niskopriorytetowe narzędzia pomocnicze.

#### 🟢 NISKIE - Funkcjonalności dodatkowe

**Uzasadnienie:** Pliki te zawierają funkcjonalności, które są pomocnicze, w fazie rozwoju (placeholdery) lub nie są częścią głównego, interaktywnego przepływu pracy użytkownika.

- `core/tools_tab.py` - Pusty placeholder na przyszłe funkcje.
- `core/pairing_tab.py` - Pusty placeholder na przyszłe funkcje.
- `core/__init__.py` - Standardowy plik pakietu, bez logiki biznesowej.
- `Pliki w __tools/` - Zestaw skryptów narzędziowych uruchamianych niezależnie od głównej aplikacji.

#### 📈 METRYKI PRIORYTETÓW

**Na podstawie analizy kodu:**

- **Plików krytycznych:** 4
- **Plików wysokich:** 4
- **Plików średnich:** 0
- **Plików niskich:** 12
- **Łącznie przeanalizowanych:** 20

**Rozkład priorytetów:** Krytyczne (20%), Wysokie (20%), Średnie (0%), Niskie (60%)

### 📄 main_window.py

- **Status:** ✅ UKOŃCZONA ANALIZA
- **Data ukończenia:** 2024-05-22
- **Business impact:** Poprawiono solidność i bezpieczeństwo ładowania konfiguracji poprzez wprowadzenie klasy `AppConfig` z walidacją typów. Uspójniono logowanie, co ułatwi diagnozowanie problemów.
- **Pliki wynikowe:**
  - `AUDYT/corrections/main_window_correction.md`
  - `AUDYT/patches/main_window_patch_code.md`

### 📄 scanner.py

- **Status:** ✅ UKOŃCZONA ANALIZA
- **Data ukończenia:** 2024-05-22
- **Business impact:** Poprawa wydajności skanowania, zwiększenie niezawodności parowania plików i wprowadzenie transakcyjności przy tworzeniu zasobów, co zapobiega niespójnym stanom.
- **Pliki wynikowe:**
  - `AUDYT/corrections/scanner_correction.md`
  - `AUDYT/patches/scanner_patch_code.md`
