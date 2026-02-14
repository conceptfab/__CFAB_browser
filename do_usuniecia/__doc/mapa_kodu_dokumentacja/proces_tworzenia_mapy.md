# 🗺️ PROCES TWORZENIA MAPY KODU - AUDYT

> **LOKALIZACJA:** `mapa_kodu_dokumentacja/proces_tworzenia_mapy.md`  
> **STATUS:** Proces tworzenia mapy kodu  
> **DATA UTWORZENIA:** 2024-12-19

---

## 🎯 CEL zadania

> **Szczegółowy cel, zakres i kryteria sukcesu budowania mapy zostały określone w pliku: `cel_budowania_mapy.md`.**
>
> **Przed kontynuowaniem zapoznaj się z jego zawartością, aby w pełni zrozumieć kontekst i wymagania.**

---

## 🎯 CEL DOKUMENTU

Dokumentacja procesu tworzenia mapy logiki biznesowej aplikacji.

---

## 🚨 KRYTYCZNA ZASADA: PROGRESYWNE BUDOWANIE MAPY PLIK PO PLIKU

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

**🚨 OBOWIĄZKOWE:**

- Plik mapy MUSI być nazwany: `mapa_kodu.md`
- Plik mapy MUSI być w głównym folderze projektu
- Plik mapy MUSI być w formacie Markdown
- Plik mapy MUSI zawierać wszystkie wymagane sekcje

### ZASADA PROGRESYWNEGO BUDOWANIA

1. **JEDEN PLIK NA RAZ** - Model MUSI analizować i dodawać do mapy tylko jeden plik w każdej sesji
2. **KOMPLETNA ANALIZA PLIKU** - Każdy plik musi być w pełni przeanalizowany przed przejściem do następnego
3. **AKTUALIZACJA MAPY** - Po każdej analizie pliku mapa musi być zaktualizowana
4. **ŚLEDZENIE POSTĘPU** - Model MUSI śledzić postęp analizy i informować o następnym pliku do analizy
5. **NIE WOLNO POMIJAĆ** - Każdy plik .py musi być przeanalizowany, bez wyjątków

### PROCES PROGRESYWNEGO BUDOWANIA

**KROK 1: IDENTYFIKACJA NASTĘPNEGO PLIKU**

- Model MUSI sprawdzić aktualny postęp analizy
- Wybrać następny plik do analizy (według priorytetów)
- Zgłosić który plik będzie analizowany

**KROK 2: KOMPLETNA ANALIZA PLIKU**

- Przeanalizować zawartość pliku (funkcje, klasy, importy)
- Określić dwufazowe priorytety (struktura + poprawki)
- Uzasadnić finalny priorytet
- Opisać business impact
- Zmapować zależności

**KROK 3: AKTUALIZACJA MAPY**

- Dodać analizę pliku do mapy
- Zaktualizować statystyki
- Zaktualizować postęp analizy
- Wskazać następny plik do analizy

**KROK 4: WERYFIKACJA**

- Sprawdzić czy analiza jest kompletna
- Sprawdzić czy mapa jest aktualna
- Przygotować się do następnej sesji

### FORMAT PROGRESYWNEGO BUDOWANIA

**Na początku każdej sesji model MUSI:**

```markdown
## 📋 POSTĘP ANALIZY MAPY

**Status:** Progresywne budowanie - plik po pliku
**Ukończone analizy:** [LICZBA] / [CAŁKOWITA_LICZBA]
**Procent ukończenia:** [PROCENT]%
**Następny plik do analizy:** [NAZWA_PLIKU]
**Priorytet następnego pliku:** [PRIORYTET]

### 📄 ANALIZA PLIKU: [NAZWA_PLIKU].PY
```

**Po każdej analizie model MUSI:**

```markdown
### 📄 [NAZWA_PLIKU].PY - ✅ UKOŃCZONA ANALIZA

- **Status:** ✅ UKOŃCZONA ANALIZA
- **Data ukończenia:** [DATA]
- **Priorytet struktury:** [PRIORYTET_STRUKTURY] - [UZASADNIENIE]
- **Priorytet poprawek:** [PRIORYTET_POPRAWEK] - [UZASADNIENIE]
- **Finalny priorytet:** [FINALNY_PRIORYTET] - [UZASADNIENIE PROCESU MYŚLOWEGO]
- **Business impact:** [OPIS WPŁYWU NA PROCESY BIZNESOWE]
- **Następny plik do analizy:** [NAZWA_NASTĘPNEGO_PLIKU]
```

### ZABRONIONE ZACHOWANIA

**🚨 ABSOLUTNIE ZABRONIONE:**

1. **NIE analizuj wielu plików jednocześnie** - tylko jeden na raz!
2. **NIE pomijaj analizy pliku** - każdy plik musi być przeanalizowany
3. **NIE generuj całej mapy od razu** - buduj progresywnie
4. **NIE pomijaj aktualizacji postępu** - śledź każdy krok
5. **NIE pomijaj uzasadnień** - każdy priorytet musi być uzasadniony

### WERYFIKACJA PROGRESYWNEGO BUDOWANIA

**Po każdej analizie pliku model MUSI sprawdzić:**

- ✅ Czy plik został w pełni przeanalizowany?
- ✅ Czy priorytety są uzasadnione?
- ✅ Czy mapa została zaktualizowana?
- ✅ Czy postęp został zaktualizowany?
- ✅ Czy wskazano następny plik do analizy?

---

## 🗺️ ETAP 1: DYNAMICZNE ODKRYWANIE STRUKTURY

**🚨 KRYTYCZNE: Mapa NIE jest statyczna! Musi być generowana na podstawie aktualnego kodu za każdym razem.**

### KROK 1: ANALIZA STRUKTURY PROJEKTU

```bash
# Model MUSI wykonać te komendy aby odkryć aktualną strukturę:
find . -name "*.py" -type f | head -50  # Znajdź wszystkie pliki .py
ls -la                                 # Sprawdź główne katalogi
tree . -I "__pycache__|*.pyc"          # Pełna struktura (jeśli dostępna)
```

### KROK 2: IDENTYFIKACJA KATALOGÓW Z LOGIKĄ BIZNESOWĄ

Model MUSI przeanalizować każdy katalog i określić czy zawiera logikę biznesową:

**Pytania weryfikacyjne:**

- Czy ten katalog zawiera pliki z logiką biznesową?
- Czy są tu algorytmy przetwarzania danych?
- Czy są tu komponenty UI odpowiedzialne za UX?
- Czy są tu workery lub serwisy biznesowe?
- Czy są tu kontrolery koordynujące procesy?
- Czy są tu modele danych biznesowych?

### KROK 3: ANALIZA PLIKÓW LOGIKI BIZNESOWEJ

Dla każdego odkrytego pliku .py model MUSI:

1. **Przeanalizować zawartość** - funkcje, klasy, importy
2. **Zidentyfikować funkcje biznesowe** - algorytmy, operacje na danych
3. **Określić priorytet** na podstawie dwufazowej analizy
4. **Dokumentować zależności** - importy, wywołania

---

## 🎯 ETAP 2: DWUFAZOWY PROCES OKREŚLANIA PRIORYTETÓW

### FAZA 1: PRIORYTET PLIKU W STRUKTURZE PROJEKTU

**Cel:** Określenie jak ważny jest dany plik w kontekście projektu.

**Kryteria oceny:**

**⚫⚫⚫⚫ KRYTYCZNE (Podstawowa funkcjonalność)**

- Główne algorytmy biznesowe aplikacji
- Core procesy przetwarzania danych
- Główne komponenty UI odpowiedzialne za UX
- Kontrolery koordynujące procesy biznesowe
- Modele danych biznesowych
- Serwisy odpowiedzialne za główne operacje

**🔴🔴🔴 WYSOKIE (Ważne operacje biznesowe)**

- Ważne algorytmy pomocnicze
- Komponenty UI drugiego poziomu
- Workery i serwisy pomocnicze
- Modele konfiguracji i cache
- Operacje na plikach i I/O

**🟡🟡 ŚREDNIE (Funkcjonalności pomocnicze)**

- Komponenty UI pomocnicze
- Narzędzia i utility
- Modele pomocnicze
- Konfiguracje i walidacje

**🟢 NISKIE (Funkcjonalności dodatkowe)**

- Logowanie i debugowanie
- Narzędzia deweloperskie
- Komponenty eksperymentalne
- Dokumentacja i testy

### FAZA 2: PRIORYTET POTRZEBY POPRAWEK/REFAKTORYZACJI

**Cel:** Identyfikacja "złego/brudnego kodu" - określenie potrzeby wykonania poprawek.

**Kryteria oceny:**

**⚫⚫⚫⚫ KRYTYCZNE (Wymaga natychmiastowej poprawki)**

- Błędy logiczne wpływające na funkcjonalność
- Memory leaks w długotrwałych procesach
- Thread safety issues w UI
- Performance bottlenecks w głównych algorytmach
- Błędy w obsłudze błędów (error handling)

**🔴🔴🔴 WYSOKIE (Wymaga poprawki w najbliższym czasie)**

- Code smells (duplikacja, długie funkcje, magic numbers)
- Problemy z wydajnością w operacjach I/O
- Nieoptymalne algorytmy
- Problemy z zarządzaniem pamięcią
- Brak walidacji danych

**🟡🟡 ŚREDNIE (Warto poprawić)**

- Nieczytelny kod
- Brak dokumentacji
- Nieoptymalne wzorce projektowe
- Problemy z konfiguracją

**🟢 NISKIE (Można poprawić przy okazji)**

- Styl kodu
- Brak komentarzy
- Nieużywane importy
- Drobne optymalizacje

### FINALNY PRIORYTET IMPLEMENTACJI

**Reguła:** Wyższy z dwóch priorytetów (lub POMINIĘTY jeśli oba są 🟢)

**Przykłady:**

- Plik z priorytetem struktury ⚫⚫⚫⚫ i priorytetem poprawek 🔴🔴🔴 → **Finalny: ⚫⚫⚫⚫**
- Plik z priorytetem struktury 🔴🔴🔴 i priorytetem poprawek ⚫⚫⚫⚫ → **Finalny: ⚫⚫⚫⚫**
- Plik z priorytetem struktury 🟢 i priorytetem poprawek 🟢 → **Finalny: POMINIĘTY**

---

## 🔍 METODA ANALIZY FUNKCJI LOGIKI BIZNESOWEJ

### PYTANIA WERYFIKACYJNE DLA KAŻDEGO PLIKU

#### 🔍 FAZA 1: PRIORYTET W STRUKTURZE PROJEKTU

1. **⚫⚫⚫⚫ KRYTYCZNE - Czy plik zawiera:**

   - Główne algorytmy biznesowe aplikacji?
   - Core procesy przetwarzania danych?
   - Główne komponenty UI odpowiedzialne za UX?
   - Kontrolery koordynujące procesy biznesowe?
   - Modele danych biznesowych?

2. **🔴🔴🔴 WYSOKIE - Czy plik zawiera:**

   - Ważne algorytmy pomocnicze?
   - Komponenty UI drugiego poziomu?
   - Workery i serwisy pomocnicze?
   - Modele konfiguracji i cache?
   - Operacje na plikach i I/O?

3. **🟡🟡 ŚREDNIE - Czy plik zawiera:**

   - Komponenty UI pomocnicze?
   - Narzędzia i utility?
   - Modele pomocnicze?
   - Konfiguracje i walidacje?

4. **🟢 NISKIE - Czy plik zawiera:**
   - Logowanie i debugowanie?
   - Narzędzia deweloperskie?
   - Komponenty eksperymentalne?
   - Dokumentację i testy?

#### 🔍 FAZA 2: PRIORYTET POTRZEBY POPRAWEK

1. **⚫⚫⚫⚫ KRYTYCZNE - Czy kod ma:**

   - Błędy logiczne wpływające na funkcjonalność?
   - Memory leaks w długotrwałych procesach?
   - Thread safety issues w UI?
   - Performance bottlenecks w głównych algorytmach?
   - Błędy w obsłudze błędów (error handling)?

2. **🔴🔴🔴 WYSOKIE - Czy kod ma:**

   - Code smells (duplikacja, długie funkcje, magic numbers)?
   - Problemy z wydajnością w operacjach I/O?
   - Nieoptymalne algorytmy?
   - Problemy z zarządzaniem pamięcią?
   - Brak walidacji danych?

3. **🟡🟡 ŚREDNIE - Czy kod ma:**

   - Nieczytelny kod?
   - Brak dokumentacji?
   - Nieoptymalne wzorce projektowe?
   - Problemy z konfiguracją?

4. **🟢 NISKIE - Czy kod ma:**
   - Problemy ze stylem kodu?
   - Brak komentarzy?
   - Nieużywane importy?
   - Drobne optymalizacje?

---

## 🚨 KRYTYCZNE ZASADY TWORZENIA MAPY

### OBOWIĄZKOWE ZASADY

1. **DYNAMICZNE GENEROWANIE** - Mapa musi być generowana na podstawie aktualnego kodu
2. **DWUFAZOWE PRIORYTETY** - Każdy plik musi mieć priorytet struktury i priorytet poprawek
3. **UZASADNIENIE PROCESU MYŚLOWEGO** - Każdy finalny priorytet musi być uzasadniony
4. **BUSINESS IMPACT** - Każdy plik musi mieć opis wpływu na procesy biznesowe
5. **ZALEŻNOŚCI** - Muszą być zmapowane zależności między plikami

### CZEGO NIE WOLNO ROBIĆ

1. **NIE używaj statycznej mapy** - zawsze generuj na podstawie aktualnego kodu
2. **NIE pomijaj analizy kodu** - każdy plik musi być przeanalizowany
3. **NIE grupuj plików** - każdy plik ma swój priorytet
4. **NIE pomijaj uzasadnienia** - każdy priorytet musi być uzasadniony
5. **NIE pomijaj business impact** - każdy plik musi mieć opis wpływu

### WERYFIKACJA MAPY

**Po wygenerowaniu mapy model MUSI sprawdzić:**

- ✅ Czy wszystkie pliki .py zostały przeanalizowane?
- ✅ Czy priorytety są uzasadnione analizą kodu?
- ✅ Czy opisy funkcji biznesowych są dokładne?
- ✅ Czy nie pominięto krytycznych plików?
- ✅ Czy mapa odzwierciedla aktualny stan kodu?
- ✅ Czy zależności są prawidłowo zmapowane?

---

## 🔄 AKTUALIZACJA MAPY

### KIEDY AKTUALIZOWAĆ

**Mapa MUSI być aktualizowana:**

- Przy każdej nowej analizie
- Po zmianach w strukturze projektu
- Po dodaniu/usunięciu plików
- Po zmianie priorytetów

### FORMAT AKTUALIZACJI

**Po każdej ukończonej analizie pliku:**

```markdown
### 📄 [NAZWA_PLIKU].PY

- **Status:** ✅ UKOŃCZONA ANALIZA
- **Data ukończenia:** [DATA]
- **Business impact:** [OPIS WPŁYWU NA PROCESY BIZNESOWE]
```

---

## 🎯 KRYTERIA SUKCESU MAPY

### MAPA JEST GOTOWA GDY:

1. **Wszystkie pliki .py** zostały przeanalizowane
2. **Dwufazowe priorytety** są określone dla każdego pliku
3. **Finalne priorytety** są uzasadnione procesem myślowym
4. **Business impact** jest opisany dla każdego pliku
5. **Zależności** są zmapowane
6. **Statystyki** są kompletne
7. **Postęp analizy** jest śledzony

### METRYKI JAKOŚCI MAPY

- **Kompletność:** 100% plików .py przeanalizowanych
- **Dokładność:** Priorytety zgodne z analizą kodu
- **Uzasadnienie:** Każdy priorytet ma proces myślowy
- **Aktualność:** Mapa odzwierciedla aktualny stan kodu
- **Przydatność:** Mapa prowadzi do konkretnych działań

---

**Dokument wygenerowany na podstawie analizy celów i założeń audytu.**  
**Ostatnia aktualizacja:** 2024-12-19  
**Wersja:** 1.0
