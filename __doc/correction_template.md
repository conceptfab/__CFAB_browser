**⚠️ KRYTYCZNE: Przed rozpoczęciem pracy zapoznaj się z ogólnymi zasadami refaktoryzacji, poprawek i testowania opisanymi w pliku [\_\_doc/refactoring_rules.md](../refactoring_rules.md).**

---

# 📋 ETAP [NUMER]: [NAZWA_PLIKU] - ANALIZA I REFAKTORYZACJA

**Data analizy:** [DATA]

### 📋 Identyfikacja

- **Plik główny:** `ścieżka/do/pliku.py`
- **Plik z kodem (patch):** `../patches/[NAZWA_PLIKU]_patch_code.md`
- **Priorytet:** [⚫⚫⚫⚫/🔴🔴🔴/🟡🟡/🟢]
- **Zależności:**
  - `plik_zalezny_1.py`
  - `plik_zalezny_2.py`

---

### 🔍 Analiza problemów

1.  **Błędy krytyczne:**

    - [Opis błędu 1]
    - [Opis błędu 2]

2.  **Optymalizacje:**

    - [Opis optymalizacji 1]
    - [Opis optymalizacji 2]

3.  **Refaktoryzacja:**

    - [Opis potrzebnej refaktoryzacji, np. podział pliku, uproszczenie logiki]

4.  **Logowanie:**
    - [Weryfikacja logowania, propozycja podziału na INFO/DEBUG]

---

### 🛠️ PLAN REFAKTORYZACJI

**Typ refaktoryzacji:** [Podział pliku/Optymalizacja kodu/Reorganizacja struktury/Usunięcie duplikatów]

#### KROK 1: PRZYGOTOWANIE 🛡️

- [ ] **BACKUP UTWORZONY:** `[nazwa_pliku]_backup_[data].py` w folderze `AUDYT/backups/`
- [ ] **ANALIZA ZALEŻNOŚCI:** Sprawdzenie wszystkich imports i wywołań
- [ ] **IDENTYFIKACJA API:** Lista publicznych metod używanych przez inne pliki
- [ ] **PLAN ETAPOWY:** Podział refaktoryzacji na małe, weryfikowalne kroki

#### KROK 2: IMPLEMENTACJA 🔧

- [ ] **ZMIANA 1:** [Opis pierwszej zmiany]
- [ ] **ZMIANA 2:** [Opis drugiej zmiany]
- [ ] **ZACHOWANIE API:** Wszystkie publiczne metody zachowane lub z deprecation warnings
- [ ] **BACKWARD COMPATIBILITY:** 100% kompatybilność wsteczna zachowana

#### KROK 3: WERYFIKACJA PO KAŻDEJ ZMIANIE 🧪

- [ ] **TESTY AUTOMATYCZNE:** Uruchomienie testów po każdej zmianie
- [ ] **URUCHOMIENIE APLIKACJI:** Sprawdzenie czy aplikacja się uruchamia
- [ ] **WERYFIKACJA FUNKCJONALNOŚCI:** Sprawdzenie czy wszystkie funkcje działają

#### KROK 4: INTEGRACJA FINALNA 🔗

- [ ] **TESTY INNYCH PLIKÓW:** Sprawdzenie czy inne moduły nadal działają
- [ ] **TESTY INTEGRACYJNE:** Pełne testy integracji z całą aplikacją
- [ ] **TESTY WYDAJNOŚCIOWE:** Wydajność nie pogorszona o więcej niż 5%

#### KRYTERIA SUKCESU REFAKTORYZACJI ✅

- [ ] **WSZYSTKIE TESTY PASS** - 100% testów przechodzi
- [ ] **APLIKACJA URUCHAMIA SIĘ** - bez błędów startowych
- [ ] **FUNKCJONALNOŚĆ ZACHOWANA** - wszystkie funkcje działają jak wcześniej
- [ ] **KOMPATYBILNOŚĆ WSTECZNA** - 100% backward compatibility

---

### 🧪 PLAN TESTÓW AUTOMATYCZNYCH

**Test funkcjonalności podstawowej:**

- [Opis testu 1]
- [Opis testu 2]

**Test integracji:**

- [Opis testu integracji z modułami zależnymi]

**Test wydajności:**

- [Opis testu wydajności, np. pomiar czasu wykonania kluczowej operacji]

---

### 📊 STATUS TRACKING

- [ ] Backup utworzony
- [ ] Plan refaktoryzacji przygotowany
- [ ] Kod zaimplementowany (krok po kroku)
- [ ] Testy podstawowe przeprowadzone (PASS)
- [ ] Testy integracji przeprowadzone (PASS)
- [ ] **WERYFIKACJA FUNKCJONALNOŚCI** - ręczne sprawdzenie kluczowych funkcji
- [ ] **WERYFIKACJA ZALEŻNOŚCI** - sprawdzenie, czy nie zepsuto innych modułów
- [ ] **WERYFIKACJA WYDAJNOŚCI** - porównanie z baseline
- [ ] Dokumentacja zaktualizowana
- [ ] **Gotowe do wdrożenia**

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

---
