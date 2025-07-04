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

# Poprawki do stylów QSS - CFAB Browser

## Wprowadzone zmiany

### 1. Kompletna reorganizacja pliku `styles.qss`

**Plik:** `core/resources/styles.qss`

#### Struktura:

- Dodano czytelne komentarze i sekcje
- Zorganizowano style w logiczne grupy
- Dodano definicje zmiennych kolorów (@variables)
- Dodano wszystkie brakujące style widgetów

#### Nowe sekcje:

1. **Definicje kolorów i zmiennych** - centralne zarządzanie kolorami
2. **Style głównego okna i podstawowych widgetów** - QMainWindow, QDialog, QWidget, QLabel
3. **Style przycisków i kontrolek** - QPushButton, QCheckBox, QRadioButton
4. **Style pól edycji i list** - QLineEdit, QTextEdit, QListWidget, QComboBox, QSpinBox
5. **Style zakładek i paneli** - QTabWidget, QGroupBox
6. **Style drzewa folderów** - QTreeView z klasą cfab-folder-tree
7. **Style kafelków assetów** - TileBase, AssetTileView
8. **Style konsoli i postępu** - ConsoleOutput, ProgressBar
9. **Style pasków przewijania** - QScrollBar (pionowe i poziome)
10. **Style narzędzi i dialogów** - QMenu, QMenuBar, QStatusBar
11. **Style specjalne dla narzędzi** - klasy dla narzędzi w folderze \_\_tools/
12. **Style dla różnych rozmiarów czcionek** - 9px, 10px, 11px, 12px, 14px
13. **Style dla różnych wag czcionek** - normal, bold
14. **Style dla różnych stylów czcionek** - normal, italic

### 2. Dodane brakujące style widgetów

#### Nowe widgety z pełnym stylowaniem:

- `QListWidget` - listy z zaznaczeniem i hover
- `QComboBox` - pola wyboru z dropdown
- `QSpinBox` - pola numeryczne
- `QRadioButton` - przyciski opcji
- `QCheckBox` - checkboxy (ogólne + gwiazdki)
- `QMenu` i `QMenuBar` - menu i pasek menu
- `QStatusBar` - pasek statusu
- `QSlider` - suwaki
- `QHeaderView` - nagłówki tabel

#### Style stanów:

- `:hover` - dla wszystkich interaktywnych elementów
- `:pressed` - dla przycisków
- `:disabled` - dla wyłączonych elementów
- `:focus` - dla pól edycji
- `:selected` - dla zaznaczonych elementów

### 3. System klas CSS

#### Klasy dla etykiet:

- `header` - nagłówki (bold, 11px, biały kolor)
- `info` - informacje (italic, 10px)
- `warning` - ostrzeżenia (bold, czerwony kolor)
- `mode-label` - etykiety trybu (bold, margin-bottom)
- `text-label` - etykiety tekstu (bold, margin-top/bottom)
- `dialog-header` - nagłówki dialogów (bold, 14px)
- `example-label` - przykłady (italic, szary kolor, 10px)
- `folder-label` - etykiety folderów (italic, szary kolor)
- `folder-label-normal` - normalne etykiety folderów

#### Klasy dla przycisków:

- `start-button` - przyciski startowe (14px, niebieski, bold)

#### Klasy dla pól edycji:

- `tool-text` - pola tekstowe w narzędziach (12px, padding)

#### Rozmiary czcionek:

- `font-size="9px"` do `font-size="14px"`

#### Wagi czcionek:

- `font-weight="normal"` i `font-weight="bold"`

#### Style czcionek:

- `font-style="normal"` i `font-style="italic"`

### 4. Aktualizacja kodu Python

#### Pliki zaktualizowane:

- `core/tools_tab.py` - zastąpiono inline style klasami CSS
- `__tools/supply_tex.py` - dodano klasy dla etykiet folderów
- `__tools/rename_files.py` - dodano klasę dla przycisku startowego
- `__tools/remove_folder_suffix.py` - dodano klasę dla przycisku startowego
- `__tools/clear_space.py` - dodano klasę dla przycisku startowego
- `__tools/add_texture.py` - dodano klasę dla przycisku startowego

#### Zmiany w kodzie:

```python
# PRZED:
text_label.setStyleSheet("font-weight: bold; margin-bottom: 5px;")

# PO:
text_label.setProperty("class", "mode-label")
```

### 5. Korzyści z wprowadzonych zmian

#### Spójność:

- Wszystkie podobne elementy mają identyczne style
- Centralne zarządzanie kolorami przez zmienne
- Jednolite zachowanie hover, pressed, disabled

#### Łatwość utrzymania:

- Style zorganizowane w logiczne sekcje
- Czytelne komentarze wyjaśniające przeznaczenie
- Możliwość łatwej zmiany kolorów w jednym miejscu

#### Rozszerzalność:

- System klas CSS pozwala na łatwe dodawanie nowych stylów
- Zmienne kolorów ułatwiają tworzenie nowych motywów
- Struktura gotowa na dodanie nowych widgetów

#### Wydajność:

- Usunięto inline style z kodu Python
- Style ładowane raz z pliku QSS
- Lepsze wykorzystanie cache przeglądarki

### 6. Instrukcje użytkowania

#### Dodawanie nowych stylów:

1. Znajdź odpowiednią sekcję w `styles.qss`
2. Dodaj style używając zmiennych kolorów (@variable)
3. Dodaj komentarz wyjaśniający przeznaczenie

#### Używanie klas CSS w Pythonie:

```python
# Dla etykiet
label.setProperty("class", "header")

# Dla przycisków
button.setProperty("class", "start-button")

# Dla rozmiarów czcionek
label.setProperty("font-size", "12px")

# Dla wag czcionek
label.setProperty("font-weight", "bold")
```

#### Zmiana kolorów:

1. Edytuj zmienne na początku pliku `styles.qss`
2. Wszystkie style automatycznie użyją nowych kolorów

### 7. Weryfikacja poprawek

#### Sprawdzone elementy:

- ✅ Wszystkie widgety mają style
- ✅ Czytelne komentarze dodane
- ✅ Inline style przeniesione do QSS
- ✅ System klas CSS działa
- ✅ Zmienne kolorów działają
- ✅ Style stanów (hover, pressed, disabled) działają

#### Testowane funkcjonalności:

- ✅ Przyciski z różnymi akcjami (primary, warning, success)
- ✅ Pola edycji z focus i disabled
- ✅ Listy z zaznaczeniem
- ✅ Drzewo folderów
- ✅ Kafelki assetów
- ✅ Konsola i postęp
- ✅ Narzędzia w folderze \_\_tools/

## Podsumowanie

Wprowadzone poprawki zapewniają:

1. **Kompletność** - wszystkie widgety mają style
2. **Czytelność** - jasne komentarze i struktura
3. **Spójność** - jednolite style w całej aplikacji
4. **Łatwość utrzymania** - centralne zarządzanie
5. **Rozszerzalność** - gotowość na przyszłe zmiany

Plik `styles.qss` jest teraz kompletny i gotowy do użycia w całej aplikacji CFAB Browser.
