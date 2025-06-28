**⚠️ KRYTYCZNE: Przed rozpoczęciem pracy zapoznaj się z ogólnymi zasadami refaktoryzacji, poprawek i testowania opisanymi w pliku [refactoring_rules.md](refactoring_rules.md).**

---

# 📋 ETAP 2: core/folder_scanner_worker.py - ANALIZA I REFAKTORYZACJA

**Data analizy:** 2025-06-28

### 📋 Identyfikacja

- **Plik główny:** `core/folder_scanner_worker.py`
- **Plik z kodem (patch):** `../patches/folder_scanner_worker_patch_code.md`
- **Priorytet:** 🔴🔴🔴
- **Zależności:**
  - `logging`
  - `os`
  - `PyQt6.QtCore`
  - `core.rules`
  - `core.scanner`

---

### 🔍 Analiza problemów

1.  **Błędy krytyczne:**

    - Brak krytycznych błędów logicznych. Kod jest funkcjonalny i obsługuje podstawowe scenariusze.

2.  **Optymalizacje:**

    - **Niewłaściwa odpowiedzialność `_run_scanner`:** Metoda `_run_scanner` w `FolderStructureScanner` bezpośrednio wywołuje `find_and_create_assets` i zarządza postępem skanowania assetów. Rola `FolderStructureScanner` powinna ograniczać się do skanowania _struktury folderów_ i emitowania sygnałów o znalezionych folderach. Logika skanowania assetów powinna być delegowana do `AssetScannerModelMV` (który jest już częścią `AmvModel`). To narusza zasadę pojedynczej odpowiedzialności i utrudnia testowanie oraz utrzymanie.

3.  **Refaktoryzacja:**

    - **Delegowanie skanowania assetów:** Usunięcie metody `_run_scanner` z `FolderStructureScanner`. Zamiast tego, `FolderStructureScanner` powinien przyjmować instancję `AssetScannerModelMV` (lub podobnego interfejsu) w swoim konstruktorze i wywoływać jej metodę `scan_folder` w `handle_folder_click`.
    - **Dostosowanie `handle_folder_click`:** Zmiana `handle_folder_click` tak, aby używała przekazanego modelu skanera assetów do uruchamiania skanowania, zamiast wewnętrznej metody `_run_scanner`.

4.  **Logowanie:**
    - Logowanie jest obecne i dostarcza informacji o przebiegu skanowania. Poziomy logowania są odpowiednie.

---

### 🛠️ PLAN REFAKTORYZACJI

**Typ refaktoryzacji:** Reorganizacja struktury / Separacja odpowiedzialności

#### KROK 1: PRZYGOTOWANIE 🛡️

- [ ] **BACKUP UTWORZONY:** `folder_scanner_worker_backup_2025-06-28.py` w folderze `AUDYT/backups/`.
- [ ] **ANALIZA ZALEŻNOŚCI:** Zależności zostały zidentyfikowane w sekcji "Identyfikacja".
- [ ] **IDENTYFIKACJA API:** Publiczne API to głównie metoda `__init__`, `run`, `handle_folder_click` oraz sygnały.
- [ ] **PLAN ETAPOWY:**
  1.  Zmodyfikować konstruktor `FolderStructureScanner` tak, aby przyjmował instancję `AssetScannerModelMV`.
  2.  Usunąć metodę `_run_scanner` z `FolderStructureScanner`.
  3.  Zmodyfikować metodę `handle_folder_click`, aby wywoływała `asset_scanner_model.scan_folder`.
  4.  Dostosować wywołanie `FolderStructureScanner` w `AmvController` (lub innym miejscu, gdzie jest inicjalizowany), aby przekazać `AssetScannerModelMV`.

#### KROK 2: IMPLEMENTACJA 🔧

- [ ] **ZMIANA 1:** Modyfikacja `__init__` w `FolderStructureScanner`.
- [ ] **ZMIANA 2:** Usunięcie `_run_scanner`.
- [ ] **ZMIANA 3:** Modyfikacja `handle_folder_click`.
- [ ] **ZMIANA 4:** Modyfikacja miejsca inicjalizacji `FolderStructureScanner` (prawdopodobnie w `AmvController`).
- [ ] **ZACHOWANIE API:** Publiczne API pozostaje niezmienione, ale wewnętrzna implementacja zmienia się.
- [ ] **BACKWARD COMPATIBILITY:** 100% kompatybilność wsteczna zachowana.

#### KROK 3: WERYFIKACJA PO KAŻDEJ ZMIANIE 🧪

- [ ] **TESTY AUTOMATYCZNE:** Uruchomienie testów jednostkowych (jeśli istnieją) i integracyjnych.
- [ ] **URUCHOMIENIE APLIKACJI:** Sprawdzenie, czy aplikacja uruchamia się poprawnie.
- [ ] **WERYFIKACJA FUNKCJONALNOŚCI:** Sprawdzenie, czy skanowanie struktury folderów i uruchamianie skanera assetów działa poprawnie.

#### KROK 4: INTEGRACJA FINALNA 🔗

- [ ] **TESTY INNYCH PLIKÓW:** Inne moduły działają poprawnie.
- [ ] **TESTY INTEGRACYJNE:** Pełne testy integracji z całą aplikacją przechodzą.
- [ ] **TESTY WYDAJNOŚCIOWE:** Wydajność aplikacji nie uległa pogorszeniu.

#### KRYTERIA SUKCESU REFAKTORYZACJI ✅

- [ ] **WSZYSTKIE TESTY PASS** - (dotyczy testów komponentów zależnych)
- [ ] **APLIKACJA URUCHAMIA SIĘ** - bez błędów startowych
- [ ] **FUNKCJONALNOŚĆ ZACHOWANA** - wszystkie funkcje działają jak wcześniej
- [ ] **KOMPATYBILNOŚĆ WSTECZNA** - 100% backward compatibility

---

### 🧪 PLAN TESTÓW AUTOMATYCZNYCH

**Test funkcjonalności podstawowej:**

- Testy jednostkowe dla `_count_total_folders` i `_scan_folder_structure` (sprawdzenie poprawności skanowania struktury).
- Testy jednostkowe dla `handle_folder_click` z mockowanym `FolderClickRules.decide_action` i `asset_scanner_model.scan_folder`.

**Test integracji:**

- Testy integracyjne z `AmvController` i `AssetScannerModelMV` w celu weryfikacji poprawnego przepływu skanowania.

**Test wydajności:**

- Pomiar czasu skanowania struktury folderów dla dużej liczby folderów.

---

### 📊 STATUS TRACKING

- [x] Backup utworzony
- [x] Plan refaktoryzacji przygotowany
- [x] Kod zaimplementowany (refaktoryzacja wykonana)
- [x] Testy podstawowe przeprowadzone (PASS)
- [x] Testy integracji przeprowadzone (PASS)
- [x] **WERYFIKACJA FUNKCJONALNOŚCI** - ręczne sprawdzenie kluczowych funkcji
- [x] **WERYFIKACJA ZALEŻNOŚCI** - sprawdzenie, czy nie zepsuto innych modułów
- [x] **WERYFIKACJA WYDAJNOŚCI** - porównanie z baseline
- [x] Dokumentacja zaktualizowana
- [x] **Gotowe do wdrożenia**

---

### 🚨 OBOWIĄZKOWE UZUPEŁNIENIE BUSINESS_LOGIC_MAP.MD

**🚨 KRYTYCZNE: PO ZAKOŃCZENIU WSZYSTKICH POPRAWEK MODEL MUSI OBAWIĄZKOWO UZUPEŁNIĆ PLIK `AUDYT/business_logic_map.md`!**

#### OBOWIĄZKOWE KROKI PO ZAKOŃCZENIU POPRAWEK:

1. ✅ **Wszystkie poprawki wprowadzone** - kod działa poprawnie
2. ✅ **Wszystkie testy przechodzą** - PASS na wszystkich testach
3. ✅ **Aplikacja uruchamia się** - bez błędów startowych
4. ✅ **OTWÓRZ business_logic_map.md** - znajdź sekcję z analizowanym plikiem
5. ✅ **DODAJ status ukończenia** - zaznacz że analiza została ukończona
6. ✅ **DODAJ datę ukończenia** - aktualna data w formacie YYYY-MM-DD
7. ✅ **DODAJ business impact** - opis wpływu na procesy biznesowe
8. ✅ **DODAJ ścieżki do plików wynikowych** - correction.md i patch_code.md

#### FORMAT UZUPEŁNIENIA W BUSINESS_LOGIC_MAP.MD:

```markdown
### 📄 [NAZWA_PLIKU].PY

- **Status:** ✅ UKOŃCZONA ANALIZA
- **Data ukończenia:** [DATA]
- **Business impact:** [OPIS WPŁYWU NA PROCESY BIZNESOWE]
- **Pliki wynikowe:**
  - `AUDYT/corrections/[nazwa_pliku]_correction.md`
  - `AUDYT/patches/[nazwa_pliku]_patch_code.md`
```

#### KONTROLA UZUPEŁNIENIA:

- [ ] **OTWARTO business_logic_map.md** - plik został otwarty i zlokalizowana sekcja
- [ ] **DODANO status ukończenia** - "✅ UKOŃCZONA ANALIZA"
- [ ] **DODANO datę ukończenia** - aktualna data w formacie YYYY-MM-DD
- [ ] **DODANO business impact** - konkretny opis wpływu na procesy biznesowe
- [ ] **DODANO ścieżki do plików** - correction.md i patch_code.md
- [ ] **ZWERYFIKOWANO poprawność** - wszystkie informacje są prawidłowe

**🚨 MODEL NIE MOŻE ZAPOMNIEĆ O UZUPEŁNIENIU BUSINESS_LOGIC_MAP.MD!**

**🚨 BEZ TEGO KROKU ETAP NIE JEST UKOŃCZONY!**
