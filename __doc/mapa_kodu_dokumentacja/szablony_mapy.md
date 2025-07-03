# 📊 SZABLONY MAPY KODU - AUDYT

**Dokumentacja szablonów i formatów mapy logiki biznesowej.**

Szablony i formaty mapy logiki biznesowej aplikacji.

> **LOKALIZACJA:** `mapa_kodu_dokumentacja/szablony_mapy.md`  
> **STATUS:** Szablony mapy kodu  
> **DATA UTWORZENIA:** 2024-12-19

---

## 🎯 CEL zadania

> **Szczegółowy cel, zakres i kryteria sukcesu budowania mapy zostały określone w pliku: `cel_budowania_mapy.md`.**
>
> **Przed kontynuowaniem zapoznaj się z jego zawartością, aby w pełni zrozumieć kontekst i wymagania.**

---

## 🎯 CEL DOKUMENTU

Szablony i formaty mapy logiki biznesowej aplikacji.

---

## 🚨 KRYTYCZNA ZASADA: PROGRESYWNE BUDOWANIE MAPY

**🔥 ABSOLUTNIE OBOWIĄZKOWE: Mapa MUSI być budowana progresywnie, jeden plik na raz!**

### LOKALIZACJA PLIKU WYNIKOWEGO

**📁 PLIK WYNIKOWY MAPY MUSI BYĆ W GŁÓWNYM FOLDERZE PROJEKTU:**

```
PROJEKT/
├── mapa_kodu.md                   # ← PLIK WYNIKOWY MAPY
├── src/
├── tests/
└── ...
```

**📋 WYMAGANIA DOTYCZĄCE PLIKU MAPY:**

- Plik mapy MUSI być nazwany: `mapa_kodu.md`
- Plik mapy MUSI być w głównym folderze projektu
- Plik mapy MUSI być w formacie Markdown
- Plik mapy MUSI zawierać wszystkie wymagane sekcje

### SZABLON PROGRESYWNEGO BUDOWANIA

**Na początku każdej sesji analizy:**

```markdown
## 📋 POSTĘP ANALIZY MAPY

**Status:** Progresywne budowanie - plik po pliku
**Ukończone analizy:** [LICZBA] / [CAŁKOWITA_LICZBA]
**Procent ukończenia:** [PROCENT]%
**Następny plik do analizy:** [NAZWA_PLIKU]
**Priorytet następnego pliku:** [PRIORYTET]

### 📄 ANALIZA PLIKU: [NAZWA_PLIKU].PY
```

**Po każdej ukończonej analizie:**

```markdown
### 📄 [NAZWA_PLIKU].PY - ✅ UKOŃCZONA ANALIZA

- **Status:** ✅ UKOŃCZONA ANALIZA
- **Data ukończenia:** [DATA]
- **Priorytet struktury:** [PRIORYTET_STRUKTURY] - [UZASADNIENIE]
- **Priorytet poprawek:** [PRIORYTET_POPRAWEK] - [UZASADNIENIE]
- **Finalny priorytet:** [FINALNY_PRIORYTET] - [UZASADNIENIE PROCESU MYŚLOWEGO]
- **Business impact:** [OPIS WPŁYWU NA PROCESY BIZNESOWEJ]
- **Następny plik do analizy:** [NAZWA_NASTĘPNEGO_PLIKU]
```

### ZASADY PROGRESYWNEGO BUDOWANIA

1. **JEDEN PLIK NA RAZ** - Analizuj tylko jeden plik w każdej sesji
2. **KOMPLETNA ANALIZA** - Każdy plik musi być w pełni przeanalizowany
3. **AKTUALIZACJA POSTĘPU** - Śledź postęp po każdej analizie
4. **WERYFIKACJA** - Sprawdź kompletność przed przejściem dalej
5. **NIE POMIJAJ** - Każdy plik .py musi być przeanalizowany

---

## 🗺️ SZABLON MAPY LOGIKI BIZNESOWEJ

### 📋 STRUKTURA MAPY

```markdown
# MAPA LOGIKI BIZNESOWEJ

**Wygenerowano na podstawie aktualnego kodu:** [DATA]
**Cel audytu:** Eliminacja over-engineering przy zachowaniu funkcjonalności

## 🎯 DWUFAZOWE PRIORYTETY

### FAZA 1: PRIORYTET STRUKTURY

- ⚫⚫⚫⚫ KRYTYCZNE - Podstawowa funkcjonalność
- 🔴🔴🔴 WYSOKIE - Ważne operacje biznesowe
- 🟡🟡 ŚREDNIE - Funkcjonalności pomocnicze
- 🟢 NISKIE - Funkcjonalności dodatkowe

### FAZA 2: PRIORYTET POPRAWEK

- ⚫⚫⚫⚫ KRYTYCZNE - Wymaga natychmiastowej poprawki
- 🔴🔴🔴 WYSOKIE - Wymaga poprawki w najbliższym czasie
- 🟡🟡 ŚREDNIE - Warto poprawić
- 🟢 NISKIE - Można poprawić przy okazji

## 📁 MAPA PLIKÓW FUNKCJONALNOŚCI BIZNESOWEJ

### [NAZWA_KATALOGU] ([ŚCIEŻKA])
```

[ŚCIEŻKA]/
├── [nazwa_pliku].py [PRIORYTET_STRUKTURY]/[PRIORYTET_POPRAWEK] → FINALNY: [FINALNY] - [OPIS FUNKCJI BIZNESOWEJ]
├── [nazwa_pliku].py [PRIORYTET_STRUKTURY]/[PRIORYTET_POPRAWEK] → FINALNY: [FINALNY] - [OPIS FUNKCJI BIZNESOWEJ]
└── [nazwa_pliku].py [PRIORYTET_STRUKTURY]/[PRIORYTET_POPRAWEK] → FINALNY: [FINALNY] - [OPIS FUNKCJI BIZNESOWEJ]

```

## 📄 SZCZEGÓŁOWA ANALIZA PLIKÓW

### 📄 [NAZWA_PLIKU].PY

- **Status:** ⏳ OCZEKUJE ANALIZY / ✅ UKOŃCZONA ANALIZA
- **Data analizy:** [DATA]
- **Priorytet struktury:** [PRIORYTET_STRUKTURY] - [UZASADNIENIE]
- **Priorytet poprawek:** [PRIORYTET_POPRAWEK] - [UZASADNIENIE]
- **Finalny priorytet:** [FINALNY_PRIORYTET] - [UZASADNIENIE PROCESU MYŚLOWEGO]
- **Business impact:** [OPIS WPŁYWU NA PROCESY BIZNESOWE]
- **Główne funkcje biznesowe:**
  - `function_name()` - [OPIS ROLI W LOGICE BIZNESOWEJ]
  - `class_name.method()` - [OPIS ROLI W LOGICE BIZNESOWEJ]

## 📊 STATYSTYKI MAPY

### 📈 Rozkład priorytetów
- **⚫⚫⚫⚫ KRYTYCZNE:** [LICZBA] plików
- **🔴🔴🔴 WYSOKIE:** [LICZBA] plików
- **🟡🟡 ŚREDNIE:** [LICZBA] plików
- **🟢 NISKIE:** [LICZBA] plików
- **❌ POMINIĘTE:** [LICZBA] plików

### 🎯 Analiza finalnych priorytetów
- **Plików finalnie krytycznych (⚫⚫⚫⚫):** [LICZBA]
- **Plików finalnie wysokich (🔴🔴🔴):** [LICZBA]
- **Plików finalnie średnich (🟡🟡):** [LICZBA]
- **Plików finalnie niskich (🟢):** [LICZBA]
- **Plików pominiętych (🟢/🟢):** [LICZBA]

### 📋 Postęp analizy
- **Ukończone analizy:** [LICZBA] / [CAŁKOWITA_LICZBA]
- **Procent ukończenia:** [PROCENT]%
- **Następny plik do analizy:** [NAZWA_PLIKU]

## 🔗 MAPA ZALEŻNOŚCI

### Zależności między plikami
```

[PLIK_A] → [PLIK_B] (zależność funkcjonalna)
[PLIK_B] → [PLIK_C] (zależność danych)
[PLIK_C] → [PLIK_D] (zależność modelu)

```

### Grupy plików powiązanych
- **Grupa 1:** [PLIK_A], [PLIK_B], [PLIK_C] - [OPIS GRUPY]
- **Grupa 2:** [PLIK_D], [PLIK_E] - [OPIS GRUPY]
- **Grupa 3:** [PLIK_F], [PLIK_G], [PLIK_H] - [OPIS GRUPY]
```

---

## 📄 SZABLON SZCZEGÓŁOWEJ ANALIZY PLIKU

### 📄 FORMAT ANALIZY PLIKU

```markdown
### 📄 [NAZWA_PLIKU].PY

- **Status:** ⏳ OCZEKUJE ANALIZY / ✅ UKOŃCZONA ANALIZA
- **Data analizy:** [DATA]
- **Priorytet struktury:** [PRIORYTET_STRUKTURY] - [UZASADNIENIE]
- **Priorytet poprawek:** [PRIORYTET_POPRAWEK] - [UZASADNIENIE]
- **Finalny priorytet:** [FINALNY_PRIORYTET] - [UZASADNIENIE PROCESU MYŚLOWEGO]
- **Business impact:** [OPIS WPŁYWU NA PROCESY BIZNESOWE]
- **Główne funkcje biznesowe:**
  - `function_name()` - [OPIS ROLI W LOGICE BIZNESOWEJ]
  - `class_name.method()` - [OPIS ROLI W LOGICE BIZNESOWEJ]
- **Zależności:**
  - Importuje: [LISTA_PLIKÓW_KTÓRE_IMPORTUJE]
  - Importowany przez: [LISTA_PLIKÓW_KTÓRE_GO_IMPORTUJĄ]
- **Opis funkcjonalności:**
  - [SZCZEGÓŁOWY_OPIS_CO_ROBI_PLIK]
```

---

## 📊 SZABLON STATYSTYK MAPY

### 📈 ROZKŁAD PRIORYTETÓW

```markdown
### 📈 Rozkład priorytetów

- **⚫⚫⚫⚫ KRYTYCZNE:** [LICZBA] plików ([PROCENT]%)
- **🔴🔴🔴 WYSOKIE:** [LICZBA] plików ([PROCENT]%)
- **🟡🟡 ŚREDNIE:** [LICZBA] plików ([PROCENT]%)
- **🟢 NISKIE:** [LICZBA] plików ([PROCENT]%)
- **❌ POMINIĘTE:** [LICZBA] plików ([PROCENT]%)

**Łącznie przeanalizowanych:** [CAŁKOWITA_LICZBA] plików
```

### 🎯 ANALIZA FINALNYCH PRIORYTETÓW

```markdown
### 🎯 Analiza finalnych priorytetów

- **Plików finalnie krytycznych (⚫⚫⚫⚫):** [LICZBA] ([PROCENT]%)
- **Plików finalnie wysokich (🔴🔴🔴):** [LICZBA] ([PROCENT]%)
- **Plików finalnie średnich (🟡🟡):** [LICZBA] ([PROCENT]%)
- **Plików finalnie niskich (🟢):** [LICZBA] ([PROCENT]%)
- **Plików pominiętych (🟢/🟢):** [LICZBA] ([PROCENT]%)

**Analiza przyczyn finalnych priorytetów:**

- **Plików krytycznych ze względu na strukturę:** [LICZBA]
- **Plików krytycznych ze względu na poprawki:** [LICZBA]
- **Plików o podwyższonym priorytecie przez poprawki:** [LICZBA]
- **Plików o podwyższonym priorytecie przez strukturę:** [LICZBA]
```

### 📋 POSTĘP ANALIZY

```markdown
### 📋 Postęp analizy

- **Ukończone analizy:** [LICZBA] / [CAŁKOWITA_LICZBA]
- **Procent ukończenia:** [PROCENT]%
- **Następny plik do analizy:** [NAZWA_PLIKU]
- **Szacowany czas do ukończenia:** [CZAS]
```

---

## 🔗 SZABLON MAPY ZALEŻNOŚCI

### ZALEŻNOŚCI MIĘDZY PLIKAMI

```markdown
### Zależności między plikami
```

[PLIK_A] → [PLIK_B] (zależność funkcjonalna)
[PLIK_B] → [PLIK_C] (zależność danych)
[PLIK_C] → [PLIK_D] (zależność modelu)
[PLIK_E] → [PLIK_F] (zależność UI)
[PLIK_G] → [PLIK_H] (zależność konfiguracji)

````

### GRUPY PLIKÓW POWIĄZANYCH

```markdown
### Grupy plików powiązanych

- **Grupa 1 - Core Business Logic:** [PLIK_A], [PLIK_B], [PLIK_C] - Główne algorytmy biznesowe
- **Grupa 2 - UI Components:** [PLIK_D], [PLIK_E] - Komponenty interfejsu użytkownika
- **Grupa 3 - Data Models:** [PLIK_F], [PLIK_G], [PLIK_H] - Modele danych i cache
- **Grupa 4 - Utilities:** [PLIK_I], [PLIK_J] - Narzędzia pomocnicze
````

---

## 📋 SZABLON FORMATU PRIORYTETÓW

### FORMAT DWUFAZOWYCH PRIORYTETÓW

```markdown
[nazwa_pliku].py [PRIORYTET_STRUKTURY]/[PRIORYTET_POPRAWEK] → FINALNY: [FINALNY_PRIORYTET] - [OPIS FUNKCJI BIZNESOWEJ]
```

### PRZYKŁADY POPRAWNYCH FORMATÓW

```markdown
├── main_window.py ⚫⚫⚫⚫/🔴🔴🔴 → FINALNY: ⚫⚫⚫⚫ - Orkiestrator aplikacji, krytyczny dla struktury ale średnio złożone poprawki
├── scanner.py ⚫⚫⚫⚫/⚫⚫⚫⚫ → FINALNY: ⚫⚫⚫⚫ - Kluczowy algorytm biznesowy, wymaga natychmiastowych poprawek
├── thumbnail.py 🔴🔴🔴/⚫⚫⚫⚫ → FINALNY: ⚫⚫⚫⚫ - Ważny w strukturze, ale krytyczne problemy w kodzie
├── utility.py 🟢/🟢 → FINALNY: POMINIĘTY - Niski priorytet w strukturze i niski priorytet poprawek
├── helper.py 🟡🟡/🔴🔴🔴 → FINALNY: 🔴🔴🔴 - Średni w strukturze, ale wysokie potrzeby poprawek
```

---

## 🎯 SZABLON UZASADNIENIA PRIORYTETÓW

### FORMAT UZASADNIENIA

```markdown
**Uzasadnienie finalnego priorytetu:** [DLACZEGO TAKI FINALNY PRIORYTET - PROCES MYŚLOWY]
```

### PRZYKŁADY UZASADNIEŃ

```markdown
**Uzasadnienie finalnego priorytetu:** Plik krytyczny dla struktury aplikacji (⚫⚫⚫⚫) - główny orkiestrator, mimo średnich problemów w kodzie (🟡🟡), finalny priorytet wynika z kluczowej roli w architekturze.

**Uzasadnienie finalnego priorytetu:** Plik pomocniczy w strukturze (🟡🟡), ale ma krytyczne problemy wydajnościowe i memory leaks (⚫⚫⚫⚫), finalny priorytet wynika z pilnej potrzeby naprawy bugów.

**Uzasadnienie finalnego priorytetu:** Plik kluczowy dla struktury (⚫⚫⚫⚫) - główne algorytmy biznesowe, oraz ma krytyczne problemy architektoniczne (⚫⚫⚫⚫), finalny priorytet wynika z podwójnej krytyczności.
```

---

## 📊 SZABLON BUSINESS IMPACT

### FORMAT BUSINESS IMPACT

```markdown
**Business impact:** [OPIS WPŁYWU NA PROCESY BIZNESOWE]
```

### PRZYKŁADY BUSINESS IMPACT

```markdown
**Business impact:** Zwiększenie stabilności aplikacji, ułatwienie przyszłego rozwoju

**Business impact:** Znaczące zwiększenie responsywności UI, eliminacja crashy aplikacji

**Business impact:** Znaczące ułatwienie utrzymania kluczowej logiki biznesowej

**Business impact:** Poprawa wydajności przetwarzania danych, redukcja czasu ładowania

**Business impact:** Uproszczenie architektury, zmniejszenie złożoności kodu
```

---

## 🔄 SZABLON AKTUALIZACJI MAPY

### FORMAT AKTUALIZACJI

```markdown
### 📄 [NAZWA_PLIKU].PY

- **Status:** ✅ UKOŃCZONA ANALIZA
- **Data ukończenia:** [DATA]
- **Business impact:** [OPIS WPŁYWU NA PROCESY BIZNESOWE]
```

---

**Dokument wygenerowany na podstawie analizy celów i założeń audytu.**  
**Ostatnia aktualizacja:** 2024-12-19  
**Wersja:** 1.0
