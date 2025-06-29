# 📜 ZASADY REFAKTORYZACJI, POPRAWEK I TESTOWANIA PROJEKTU CFAB_3DHUB

**Ten dokument zawiera kluczowe zasady, których należy bezwzględnie przestrzegać podczas wszelkich prac refaktoryzacyjnych, wprowadzania poprawek oraz testowania w projekcie. Każdy plik `*_correction.md` musi zawierać odniesienie do tego dokumentu.**

---

## 🏛️ FILARY PRAC

Prace opierają się na trzech kluczowych filarach:

1.  **WYDAJNOŚĆ** ⚡: Optymalizacja czasu, redukcja zużycia pamięci, eliminacja wąskich gardeł.
2.  **STABILNOŚĆ** 🛡️: Niezawodność, proper error handling, thread safety, eliminacja memory leaks i deadlocków.
3.  **WYELIMINOWANIE OVER-ENGINEERING** 🎯: Upraszczanie kodu, eliminacja zbędnych abstrakcji, redukcja zależności, konsolidacja funkcjonalności.

---

## 🎯 DWUFAZOWY PROCES OKREŚLANIA PRIORYTETÓW

### 📋 FAZA 1: PRIORYTET PLIKU W STRUKTURZE PROJEKTU

**Cel:** Określenie jak ważny jest dany plik w kontekście projektu i jaki ma wpływ na realizowanie logiki biznesowej.

**Kryteria oceny:**

#### ⚫⚫⚫⚫ KRYTYCZNE (Podstawowa funkcjonalność)

- Główne algorytmy biznesowe aplikacji
- Core procesy przetwarzania danych
- Główne komponenty UI odpowiedzialne za UX
- Kontrolery koordynujące procesy biznesowe
- Modele danych biznesowych
- Serwisy odpowiedzialne za główne operacje

#### 🔴🔴🔴 WYSOKIE (Ważne operacje biznesowe)

- Ważne algorytmy pomocnicze
- Komponenty UI drugiego poziomu
- Workery i serwisy pomocnicze
- Modele konfiguracji i cache
- Operacje na plikach i I/O

#### 🟡🟡 ŚREDNIE (Funkcjonalności pomocnicze)

- Komponenty UI pomocnicze
- Narzędzia i utility
- Modele pomocnicze
- Konfiguracje i walidacje

#### 🟢 NISKIE (Funkcjonalności dodatkowe)

- Logowanie i debugowanie
- Narzędzia deweloperskie
- Komponenty eksperymentalne
- Dokumentacja i testy

### 📋 FAZA 2: PRIORYTET POTRZEBY POPRAWEK/REFAKTORYZACJI

**Cel:** Identyfikacja "złego/brudnego kodu" - określenie potrzeby wykonania poprawek.

**Kryteria oceny:**

#### ⚫⚫⚫⚫ KRYTYCZNE (Wymaga natychmiastowej poprawki)

- Błędy logiczne wpływające na funkcjonalność
- Memory leaks w długotrwałych procesach
- Thread safety issues w UI
- Performance bottlenecks w głównych algorytmach
- Błędy w obsłudze błędów (error handling)

#### 🔴🔴🔴 WYSOKIE (Wymaga poprawki w najbliższym czasie)

- Code smells (duplikacja, długie funkcje, magic numbers)
- Problemy z wydajnością w operacjach I/O
- Nieoptymalne algorytmy
- Problemy z zarządzaniem pamięcią
- Brak walidacji danych

#### 🟡🟡 ŚREDNIE (Warto poprawić)

- Nieczytelny kod
- Brak dokumentacji
- Nieoptymalne wzorce projektowe
- Problemy z konfiguracją

#### 🟢 NISKIE (Można poprawić przy okazji)

- Styl kodu
- Brak komentarzy
- Nieużywane importy
- Drobne optymalizacje

### 🎯 FINALNY PRIORYTET IMPLEMENTACJI

**Reguła:** Jeśli plik ma dwa niskie priorytety → może zostać pominięty w analizie.

**Przykłady:**

- Plik z priorytetem struktury ⚫⚫⚫⚫ i priorytetem poprawek 🔴🔴🔴 → **Finalny: ⚫⚫⚫⚫**
- Plik z priorytetem struktury 🔴🔴🔴 i priorytetem poprawek ⚫⚫⚫⚫ → **Finalny: ⚫⚫⚫⚫**
- Plik z priorytetem struktury 🟢 i priorytetem poprawek 🟢 → **Finalny: POMINIĘTY**

---

## 🛡️ BEZPIECZEŃSTWO REFAKTORYZACJI

**REFAKTORING MUSI BYĆ WYKONANY MAKSYMALNIE BEZPIECZNIE!**

- **BACKUP PRZED KAŻDĄ ZMIANĄ**: Kopia bezpieczeństwa wszystkich modyfikowanych plików w `AUDYT/backups/`.
- **INKREMENTALNE ZMIANY**: Małe, weryfikowalne kroki. Jedna logiczna zmiana = jeden commit.
- **ZACHOWANIE FUNKCJONALNOŚCI**: 100% backward compatibility, zero breaking changes.
- **TESTY NA KAŻDYM ETAPIE**: Obowiązkowe testy automatyczne po każdej zmianie.
- **ROLLBACK PLAN**: Musi istnieć możliwość cofnięcia każdej zmiany.
- **WERYFIKACJA INTEGRACJI**: Sprawdzenie, że zmiana nie psuje innych części systemu.

**Czerwone linie (CZEGO NIE WOLNO ROBIĆ):**

- **NIE USUWAJ** funkcjonalności bez pewności, że jest nieużywana.
- **NIE ZMIENIAJ** publicznych API bez absolutnej konieczności.
- **NIE WPROWADZAJ** breaking changes.
- **NIE REFAKTORYZUJ** bez pełnego zrozumienia kodu.
- **NIE OPTYMALIZUJ** kosztem czytelności i maintainability.
- **NIE ŁĄCZ** wielu zmian w jednym commit.
- **NIE POMIJAJ** testów po każdej zmianie.

---

## 🧪 KRYTYCZNY WYMÓG: AUTOMATYCZNE TESTY

**KAŻDA POPRAWKA MUSI BYĆ PRZETESTOWANA! BRAK TESTÓW = BRAK WDROŻENIA.**

**Proces testowania:**

1.  Implementacja poprawki.
2.  Uruchomienie testów automatycznych (`pytest`).
3.  Analiza wyników (PASS/FAIL). Jeśli FAIL, napraw błędy i powtórz.
4.  Weryfikacja funkcjonalności i zależności.
5.  Dopiero po uzyskaniu PASS można przejść do następnego etapu.

**Wymagane rodzaje testów:**

1.  **Test funkcjonalności podstawowej**: Czy funkcja działa poprawnie.
2.  **Test integracji**: Czy zmiana nie psuje innych części systemu.
3.  **Test wydajności**: Czy zmiana nie spowalnia aplikacji.

**Kryteria sukcesu testów:**

- Wszystkie testy **PASS** (0 FAIL).
- Pokrycie kodu **>80%** dla nowych funkcji.
- Brak regresji w istniejących testach.
- Wydajność nie pogorszona o więcej niż 5%.

---

## 📁 STANDARDY ORGANIZACJI PLIKÓW

### 🗂️ Struktura katalogów wynikowych

**Wszystkie pliki wynikowe audytu MUSZĄ być zapisywane w katalogu `AUDYT/`:**

```
AUDYT/
├── business_logic_map.md          # Mapa logiki biznesowej
├── implementation_plan.md         # Plan implementacji poprawek
├── corrections/                   # Analizy poprawek
│   ├── [nazwa_pliku]_correction.md
│   └── ...
├── patches/                       # Fragmenty kodu do implementacji
│   ├── [nazwa_pliku]_patch_code.md
│   └── ...
└── backups/                       # Kopie bezpieczeństwa
    ├── [nazwa_pliku]_backup_[data].py
    └── ...
```

### 📅 Standardy formatowania

- **Format dat:** YYYY-MM-DD (np. 2024-01-15)
- **Statusy implementacji:** ⏳ OCZEKUJE / 🔄 W TRAKCIE / ✅ UKOŃCZONE
- **Nazwy plików:** snake_case dla plików wynikowych

---

## 🔄 PROCEDURY AKTUALIZACJI DOKUMENTÓW

### 📋 Obowiązkowe kroki po każdej analizie pliku

1. ✅ **Ukończ analizę pliku** - utwórz correction.md i patch_code.md
2. ✅ **UZUPEŁNIJ business_logic_map.md** - dodaj status ukończenia
3. ✅ **UZUPEŁNIJ implementation_plan.md** - dodaj poprawkę do planu implementacji
4. ✅ **Sprawdź postęp** - podaj procent ukończenia
5. ✅ **Określ następny etap** - nazwa kolejnego pliku do analizy

### 📝 Format uzupełnienia w business_logic_map.md

```markdown
### 📄 [NAZWA_PLIKU].PY

- **Status:** ✅ UKOŃCZONA ANALIZA
- **Data ukończenia:** [DATA]
- **Business impact:** [OPIS WPŁYWU NA PROCESY BIZNESOWE]
- **Pliki wynikowe:**
  - `AUDYT/corrections/[nazwa_pliku]_correction.md`
  - `AUDYT/patches/[nazwa_pliku]_patch_code.md`
```

---

## 🔧 KROKI REFAKTORYZACJI

### KROK 0: ANALIZA I PODZIAŁ KODU

- **Analiza kodu źródłowego**: Przeanalizuj kod źródłowy, który ma zostać podzielony na mniejsze fragmenty/moduły.
- **Zaznaczenie fragmentów**: W kodzie źródłowym wyraźnie zaznacz fragmenty do przeniesienia do nowych modułów, dodając komentarze z instrukcjami, co ma zostać uzupełnione w kodzie (np. `TODO: Przenieś tę funkcjonalność do nowego modułu X`).
- **Weryfikacja po podziale (przed refaktoryzacją)**: Po podziale kodu na mniejsze moduły, ale PRZED jakąkolwiek bezpośrednią refaktoryzacją, upewnij się, że wszystkie funkcjonalności i interfejs użytkownika (UI) są w 100% zgodne z wersją przed zmianami.
- **Potwierdzenie przez użytkownika i testy**: Uzyskaj wyraźne potwierdzenie od użytkownika, że kod działa poprawnie. Potwierdź to również poprzez uruchomienie wszystkich testów automatycznych (jednostkowych, integracyjnych, wydajnościowych).
- **Refaktoryzacja i optymalizacja**: Bezpośrednia refaktoryzacja i optymalizacja mogą być przeprowadzone TYLKO na kodzie, który w 100% działa i został zweryfikowany po podziale.

### KROK 1: PRZYGOTOWANIE

- Utwórz backup pliku.
- Przeanalizuj wszystkie zależności (imports, calls).
- Zidentyfikuj publiczne API.
- Przygotuj plan refaktoryzacji z podziałem na małe, weryfikowalne kroki.

### KROK 2: IMPLEMENTACJA

- Implementuj **JEDNĄ** zmianę na raz.
- Zachowaj wszystkie publiczne metody i ich sygnatury (lub dodaj `DeprecationWarning`).
- Zachowaj 100% kompatybilność wsteczną.

### KROK 3: WERYFIKACJA

- Uruchom testy automatyczne po każdej małej zmianie.
- Sprawdź, czy aplikacja się uruchamia i działa poprawnie.
- Sprawdź, czy nie ma błędów importów.
- Sprawdź, czy inne pliki zależne działają.
- Uruchom testy integracyjne i wydajnościowe.

---

## ✅ CHECKLISTA WERYFIKACYJNA

**Każdy plik `patch.md` musi zawierać poniższą checklistę do weryfikacji przed oznaczeniem etapu jako ukończony.**

- **Funkcjonalności:** Podstawowa funkcjonalność, kompatybilność API, obsługa błędów, walidacja, logowanie, cache, thread safety, wydajność.
- **Zależności:** Importy, zależności zewnętrzne i wewnętrzne, brak cyklicznych zależności, kompatybilność wsteczna.
- **Testy:** Jednostkowe, integracyjne, regresyjne, wydajnościowe.
- **Dokumentacja:** Aktualność README, API docs, changelog.

---

## 📊 DOKUMENTACJA I KONTROLA POSTĘPU

- **PROGRESYWNE UZUPEŁNIANIE**: Po każdej analizie pliku **NATYCHMIAST** aktualizuj pliki wynikowe (`business_logic_map.md`, `*_correction.md`, `*_patch.md`).
- **OSOBNE PLIKI**: Każdy analizowany plik musi mieć swój własny `_correction.md` i `_patch.md`.
- **KONTROLA POSTĘPU**: Po każdym etapie raportuj postęp (X/Y ukończonych, %, następny etap).
- **COMMITY**: Commity wykonuj dopiero po pozytywnych testach użytkownika, z jasnym komunikatem, np. `ETAP X: [NAZWA_PLIKU] - [OPIS] - ZAKOŃCZONY`.

**Pamiętaj: Żaden etap nie może być pominięty. Wszystkie etapy muszą być wykonywane sekwencyjnie.**
