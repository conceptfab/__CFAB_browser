# 🗺️ MAPA LOGIKI BIZNESOWEJ - SZABLON UNIWERSALNY

> **⚠️ KRYTYCZNE: Przed rozpoczęciem pracy zapoznaj się z ogólnymi zasadami refaktoryzacji, poprawek i testowania opisanymi w pliku [\_\_doc/refactoring_rules.md](__doc/refactoring_rules.md).**

## 📊 PRZEGLĄD OGÓLNY

**Data analizy:** [DATA]
**Wersja aplikacji:** [WERSJA]
**Analizowane pliki:** [LICZBA] z [CAŁKOWITA_LICZBA]

## 🎯 DWUFAZOWY PROCES OKREŚLANIA PRIORYTETÓW

**Szczegółowe kryteria priorytetów znajdują się w [\_\_doc/refactoring_rules.md](__doc/refactoring_rules.md).**

### 📋 FAZA 1: PRIORYTET PLIKU W STRUKTURZE PROJEKTU

**Cel:** Określenie jak ważny jest dany plik w kontekście projektu i jaki ma wpływ na realizowanie logiki biznesowej.

### 📋 FAZA 2: PRIORYTET POTRZEBY POPRAWEK/REFAKTORYZACJI

**Cel:** Identyfikacja "złego/brudnego kodu" - określenie potrzeby wykonania poprawek.

### 🎯 FINALNY PRIORYTET IMPLEMENTACJI

**Reguła:** Jeśli plik ma dwa niskie priorytety → może zostać pominięty w analizie.

## 🗺️ MAPA STRUKTURY PROJEKTU

### 📁 GŁÓWNE KATALOGI Z LOGIKĄ BIZNESOWĄ

**[KATALOG_1]** ([ŚCIEŻKA_KATALOGU])

- **Rola w logice biznesowej:** [OPIS ROLI]
- **Priorytet struktury:** [PRIORYTET_FAZY_1]
- **Priorytet poprawek:** [PRIORYTET_FAZY_2]
- **Finalny priorytet:** [PRIORYTET_FINALNY]

**[KATALOG_2]** ([ŚCIEŻKA_KATALOGU])

- **Rola w logice biznesowej:** [OPIS ROLI]
- **Priorytet struktury:** [PRIORYTET_FAZY_1]
- **Priorytet poprawek:** [PRIORYTET_FAZY_2]
- **Finalny priorytet:** [PRIORYTET_FINALNY]

### 📄 SZCZEGÓŁOWA ANALIZA PLIKÓW

#### **[NAZWA_KATALOGU_1]** ([ŚCIEŻKA_KATALOGU])

##### `[NAZWA_PLIKU_1].py`

- **Funkcjonalność biznesowa:** [OPIS_FUNKCJI_BIZNESOWEJ]
- **Priorytet struktury:** [PRIORYTET_FAZY_1] - [UZASADNIENIE]
- **Priorytet poprawek:** [PRIORYTET_FAZY_2] - [UZASADNIENIE]
- **Finalny priorytet:** [PRIORYTET_FINALNY]
- **Główne funkcje:** [LISTA_FUNKCJI]
- **Zależności:** [LISTA_ZALEŻNOŚCI]
- **Wpływ na biznes:** [OPIS_WPŁYWU]

##### `[NAZWA_PLIKU_2].py`

- **Funkcjonalność biznesowa:** [OPIS_FUNKCJI_BIZNESOWEJ]
- **Priorytet struktury:** [PRIORYTET_FAZY_1] - [UZASADNIENIE]
- **Priorytet poprawek:** [PRIORYTET_FAZY_2] - [UZASADNIENIE]
- **Finalny priorytet:** [PRIORYTET_FINALNY]
- **Główne funkcje:** [LISTA_FUNKCJI]
- **Zależności:** [LISTA_ZALEŻNOŚCI]
- **Wpływ na biznes:** [OPIS_WPŁYWU]

#### **[NAZWA_KATALOGU_2]** ([ŚCIEŻKA_KATALOGU])

##### `[NAZWA_PLIKU_3].py`

- **Funkcjonalność biznesowa:** [OPIS_FUNKCJI_BIZNESOWEJ]
- **Priorytet struktury:** [PRIORYTET_FAZY_1] - [UZASADNIENIE]
- **Priorytet poprawek:** [PRIORYTET_FAZY_2] - [UZASADNIENIE]
- **Finalny priorytet:** [PRIORYTET_FINALNY]
- **Główne funkcje:** [LISTA_FUNKCJI]
- **Zależności:** [LISTA_ZALEŻNOŚCI]
- **Wpływ na biznes:** [OPIS_WPŁYWU]

## 🎯 FINALNA LISTA PLIKÓW WYMAGAJĄCYCH ANALIZY

### ⚫⚫⚫⚫ KRYTYCZNE (Analiza wymagana)

1. `[ŚCIEŻKA_DO_PLIKU_1]` - [OPIS_FUNKCJI_BIZNESOWEJ]

   - **Uzasadnienie:** [DLACZEGO KRYTYCZNY]
   - **Szacowany czas analizy:** [CZAS]

2. `[ŚCIEŻKA_DO_PLIKU_2]` - [OPIS_FUNKCJI_BIZNESOWEJ]
   - **Uzasadnienie:** [DLACZEGO KRYTYCZNY]
   - **Szacowany czas analizy:** [CZAS]

### 🔴🔴🔴 WYSOKIE (Analiza zalecana)

3. `[ŚCIEŻKA_DO_PLIKU_3]` - [OPIS_FUNKCJI_BIZNESOWEJ]

   - **Uzasadnienie:** [DLACZEGO WYSOKI]
   - **Szacowany czas analizy:** [CZAS]

4. `[ŚCIEŻKA_DO_PLIKU_4]` - [OPIS_FUNKCJI_BIZNESOWEJ]
   - **Uzasadnienie:** [DLACZEGO WYSOKI]
   - **Szacowany czas analizy:** [CZAS]

### 🟡🟡 ŚREDNIE (Analiza opcjonalna)

5. `[ŚCIEŻKA_DO_PLIKU_5]` - [OPIS_FUNKCJI_BIZNESOWEJ]
   - **Uzasadnienie:** [DLACZEGO ŚREDNI]
   - **Szacowany czas analizy:** [CZAS]

### 🟢 NISKIE (Pominięte w analizie)

- `[ŚCIEŻKA_DO_PLIKU_6]` - [OPIS] - **Pominięty:** Oba priorytety niskie
- `[ŚCIEŻKA_DO_PLIKU_7]` - [OPIS] - **Pominięty:** Oba priorytety niskie

## 🔗 ZALEŻNOŚCI ARCHITEKTURALNE

**Pliki które MUSZĄ być przeanalizowane przed innymi:**

- **[PLIK_A]** → **[PLIK_B]** (zależność architekturalna)
- **[PLIK_C]** → **[PLIK_D]** (zależność modelu)
- **[PLIK_E]** → **[PLIK_F]** (zależność serwisu)

## 📊 PODSUMOWANIE ANALIZY

### 🔍 GŁÓWNE PROBLEMY ZIDENTYFIKOWANE

1. **[PROBLEM 1]** - [OPIS] - [PRIORYTET]
2. **[PROBLEM 2]** - [OPIS] - [PRIORYTET]
3. **[PROBLEM 3]** - [OPIS] - [PRIORYTET]

### ⚡ BOTTLENECKI WYDAJNOŚCI

1. **[BOTTLENECK 1]** - [OPIS] - [WPŁYW NA WYDAJNOŚĆ]
2. **[BOTTLENECK 2]** - [OPIS] - [WPŁYW NA WYDAJNOŚĆ]
3. **[BOTTLENECK 3]** - [OPIS] - [WPŁYW NA WYDAJNOŚĆ]

### 🏗️ PROBLEMY ARCHITEKTURALNE

1. **[PROBLEM ARCHITEKTURALNY 1]** - [OPIS] - [PRIORYTET]
2. **[PROBLEM ARCHITEKTURALNY 2]** - [OPIS] - [PRIORYTET]
3. **[PROBLEM ARCHITEKTURALNY 3]** - [OPIS] - [PRIORYTET]

## 📈 METRYKI SUKCESU

- **Wydajność:** [CEL] - [AKTUALNY STAN]
- **Stabilność:** [CEL] - [AKTUALNY STAN]
- **Kod:** [CEL] - [AKTUALNY STAN]

---

**Status:** [W TRAKCIE/ZAKOŃCZONY]
**Ostatnia aktualizacja:** [DATA]

### 🚀 Następne kroki

**Po ukończeniu mapy:**

1. **Przegląd priorytetów** - Weryfikacja poprawności ocen
2. **Plan implementacji** - Utworzenie planu implementacji poprawek
3. **Kickoff** - Rozpoczęcie analizy zgodnie z priorytetami
4. **Monitoring** - Śledzenie postępu wg zdefiniowanych metryk

### 📚 PLIKI REFERENCYJNE

- `__doc/audyt_logiki_biznesowej.md` - **GŁÓWNY DOKUMENT AUDYTU** (procedury i zasady)
- `__doc/implementation_plan_template.md` - **SZABLON PLANU IMPLEMENTACJI** (finalny dokument)
- `__doc/correction_template.md` - **SZABLON ANALIZ POPRAWEK**
- `__doc/patch_code_template.md` - **SZABLON FRAGMENTÓW KODU**
- `__doc/refactoring_rules.md` - **GŁÓWNE ZASADY REFAKTORYZACJI**
