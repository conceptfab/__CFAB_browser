# 🎯 KRYTERIA PRIORYTETÓW - AUDYT

> **LOKALIZACJA:** `mapa_kodu_dokumentacja/kryteria_priorytetow.md`  
> **STATUS:** Kryteria oceny priorytetów  
> **DATA UTWORZENIA:** 2024-12-19

---

## 🎯 CEL zadania

> **Szczegółowy cel, zakres i kryteria sukcesu budowania mapy zostały określone w pliku: `cel_budowania_mapy.md`.**
>
> **Przed kontynuowaniem zapoznaj się z jego zawartością, aby w pełni zrozumieć kontekst i wymagania.**

---

## 🎯 CEL DOKUMENTU

Szczegółowe kryteria oceny priorytetów dla mapy logiki biznesowej aplikacji.

---

## 📁 LOKALIZACJA PLIKU WYNIKOWEGO

**🚨 OBOWIĄZKOWE: Plik wynikowy mapy MUSI być w głównym folderze projektu!**

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

---

## 🎯 DWUFAZOWY PROCES OKREŚLANIA PRIORYTETÓW

### 📋 FAZA 1: PRIORYTET PLIKU W STRUKTURZE PROJEKTU

**Cel:** Określenie jak ważny jest dany plik w kontekście projektu i jaki ma wpływ na realizowanie logiki biznesowej.

#### ⚫⚫⚫⚫ KRYTYCZNE (Podstawowa funkcjonalność)

**Kryteria:**

- Główne algorytmy biznesowe aplikacji
- Core procesy przetwarzania danych
- Główne komponenty UI odpowiedzialne za UX
- Kontrolery koordynujące procesy biznesowe
- Modele danych biznesowych
- Serwisy odpowiedzialne za główne operacje

**Przykłady plików:**

- `main_window.py` - główny orkiestrator aplikacji
- `scanner.py` - kluczowe algorytmy skanowania
- `core_processor.py` - główne procesy przetwarzania
- `main_ui.py` - główny interfejs użytkownika

#### 🔴🔴🔴 WYSOKIE (Ważne operacje biznesowe)

**Kryteria:**

- Ważne algorytmy pomocnicze
- Komponenty UI drugiego poziomu
- Workery i serwisy pomocnicze
- Modele konfiguracji i cache
- Operacje na plikach i I/O

**Przykłady plików:**

- `cache_manager.py` - zarządzanie cache
- `file_processor.py` - operacje na plikach
- `secondary_ui.py` - komponenty UI drugiego poziomu
- `worker_service.py` - serwisy pomocnicze

#### 🟡🟡 ŚREDNIE (Funkcjonalności pomocnicze)

**Kryteria:**

- Komponenty UI pomocnicze
- Narzędzia i utility
- Modele pomocnicze
- Konfiguracje i walidacje

**Przykłady plików:**

- `helper_ui.py` - komponenty UI pomocnicze
- `utility_functions.py` - funkcje pomocnicze
- `config_validator.py` - walidacja konfiguracji
- `helper_models.py` - modele pomocnicze

#### 🟢 NISKIE (Funkcjonalności dodatkowe)

**Kryteria:**

- Logowanie i debugowanie
- Narzędzia deweloperskie
- Komponenty eksperymentalne
- Dokumentacja i testy

**Przykłady plików:**

- `logger.py` - system logowania
- `debug_tools.py` - narzędzia debugowania
- `experimental.py` - komponenty eksperymentalne
- `test_utils.py` - narzędzia testowe

---

### 📋 FAZA 2: PRIORYTET POTRZEBY POPRAWEK/REFAKTORYZACJI

**Cel:** Identyfikacja "złego/brudnego kodu" - określenie potrzeby wykonania poprawek.

#### ⚫⚫⚫⚫ KRYTYCZNE (Wymaga natychmiastowej poprawki)

**Kryteria:**

- Błędy logiczne wpływające na funkcjonalność
- Memory leaks w długotrwałych procesach
- Thread safety issues w UI
- Performance bottlenecks w głównych algorytmach
- Błędy w obsłudze błędów (error handling)

**Przykłady problemów:**

- Błędy w algorytmach biznesowych
- Memory leaks w długotrwałych operacjach
- Problemy z thread safety w UI
- Wolne algorytmy wpływające na UX
- Nieprawidłowa obsługa błędów

#### 🔴🔴🔴 WYSOKIE (Wymaga poprawki w najbliższym czasie)

**Kryteria:**

- Code smells (duplikacja, długie funkcje, magic numbers)
- Problemy z wydajnością w operacjach I/O
- Nieoptymalne algorytmy
- Problemy z zarządzaniem pamięcią
- Brak walidacji danych

**Przykłady problemów:**

- Duplikacja kodu między modułami
- Długie funkcje (>50 linii)
- Magic numbers w kodzie
- Wolne operacje I/O
- Brak walidacji danych wejściowych

#### 🟡🟡 ŚREDNIE (Warto poprawić)

**Kryteria:**

- Nieczytelny kod
- Brak dokumentacji
- Nieoptymalne wzorce projektowe
- Problemy z konfiguracją

**Przykłady problemów:**

- Kod trudny do zrozumienia
- Brak docstringów i komentarzy
- Nadmiernie złożone wzorce projektowe
- Problemy z konfiguracją aplikacji

#### 🟢 NISKIE (Można poprawić przy okazji)

**Kryteria:**

- Styl kodu
- Brak komentarzy
- Nieużywane importy
- Drobne optymalizacje

**Przykłady problemów:**

- Niezgodność ze stylem kodu
- Brak komentarzy w prostych funkcjach
- Nieużywane importy
- Drobne optymalizacje wydajnościowe

---

## 🎯 FINALNY PRIORYTET IMPLEMENTACJI

### REGUŁA OKREŚLANIA FINALNEGO PRIORYTETU

**Reguła:** Wyższy z dwóch priorytetów (lub POMINIĘTY jeśli oba są 🟢)

### PRZYKŁADY FINALNYCH PRIORYTETÓW

#### Przykład 1: Priorytet struktury przeważa

```
Plik: main_window.py
Priorytet struktury: ⚫⚫⚫⚫ (główny orkiestrator)
Priorytet poprawek: 🟡🟡 (średnie problemy)
Finalny priorytet: ⚫⚫⚫⚫
Uzasadnienie: Krytyczny dla struktury aplikacji, mimo średnich problemów w kodzie
```

#### Przykład 2: Priorytet poprawek przeważa

```
Plik: cache_manager.py
Priorytet struktury: 🟡🟡 (pomocniczy)
Priorytet poprawek: ⚫⚫⚫⚫ (krytyczne memory leaks)
Finalny priorytet: ⚫⚫⚫⚫
Uzasadnienie: Pomocniczy w strukturze, ale krytyczne problemy wymagają natychmiastowej naprawy
```

#### Przykład 3: Oba priorytety równe

```
Plik: scanner.py
Priorytet struktury: ⚫⚫⚫⚫ (kluczowy algorytm)
Priorytet poprawek: ⚫⚫⚫⚫ (krytyczne błędy)
Finalny priorytet: ⚫⚫⚫⚫
Uzasadnienie: Podwójna krytyczność - kluczowy dla struktury i ma krytyczne problemy
```

#### Przykład 4: Pominięty

```
Plik: debug_tools.py
Priorytet struktury: 🟢 (narzędzia debugowania)
Priorytet poprawek: 🟢 (drobne problemy stylu)
Finalny priorytet: POMINIĘTY
Uzasadnienie: Oba priorytety niskie - może zostać pominięty w analizie
```

---

## 🔍 PYTANIA WERYFIKACYJNE

### PYTANIA DLA FAZY 1: PRIORYTET STRUKTURY

#### ⚫⚫⚫⚫ KRYTYCZNE

1. Czy plik zawiera główne algorytmy biznesowe aplikacji?
2. Czy plik jest odpowiedzialny za core procesy przetwarzania danych?
3. Czy plik zawiera główne komponenty UI odpowiedzialne za UX?
4. Czy plik jest kontrolerem koordynującym procesy biznesowe?
5. Czy plik zawiera modele danych biznesowych?
6. Czy plik jest serwisem odpowiedzialnym za główne operacje?

#### 🔴🔴🔴 WYSOKIE

1. Czy plik zawiera ważne algorytmy pomocnicze?
2. Czy plik zawiera komponenty UI drugiego poziomu?
3. Czy plik jest workerem lub serwisem pomocniczym?
4. Czy plik zawiera modele konfiguracji i cache?
5. Czy plik jest odpowiedzialny za operacje na plikach i I/O?

#### 🟡🟡 ŚREDNIE

1. Czy plik zawiera komponenty UI pomocnicze?
2. Czy plik zawiera narzędzia i utility?
3. Czy plik zawiera modele pomocnicze?
4. Czy plik zawiera konfiguracje i walidacje?

#### 🟢 NISKIE

1. Czy plik zawiera logowanie i debugowanie?
2. Czy plik zawiera narzędzia deweloperskie?
3. Czy plik zawiera komponenty eksperymentalne?
4. Czy plik zawiera dokumentację i testy?

### PYTANIA DLA FAZY 2: PRIORYTET POPRAWEK

#### ⚫⚫⚫⚫ KRYTYCZNE

1. Czy kod ma błędy logiczne wpływające na funkcjonalność?
2. Czy kod ma memory leaks w długotrwałych procesach?
3. Czy kod ma thread safety issues w UI?
4. Czy kod ma performance bottlenecks w głównych algorytmach?
5. Czy kod ma błędy w obsłudze błędów (error handling)?

#### 🔴🔴🔴 WYSOKIE

1. Czy kod ma code smells (duplikacja, długie funkcje, magic numbers)?
2. Czy kod ma problemy z wydajnością w operacjach I/O?
3. Czy kod ma nieoptymalne algorytmy?
4. Czy kod ma problemy z zarządzaniem pamięcią?
5. Czy kod ma brak walidacji danych?

#### 🟡🟡 ŚREDNIE

1. Czy kod jest nieczytelny?
2. Czy kod ma brak dokumentacji?
3. Czy kod ma nieoptymalne wzorce projektowe?
4. Czy kod ma problemy z konfiguracją?

#### 🟢 NISKIE

1. Czy kod ma problemy ze stylem?
2. Czy kod ma brak komentarzy?
3. Czy kod ma nieużywane importy?
4. Czy kod wymaga drobnych optymalizacji?

---

## 📊 METRYKI JAKOŚCI PRIORYTETÓW

### KRYTERIA JAKOŚCI

1. **Spójność** - Priorytety są spójne w całej aplikacji
2. **Uzasadnienie** - Każdy priorytet ma jasne uzasadnienie
3. **Obiektywność** - Priorytety są oparte na faktach, nie opiniach
4. **Kompletność** - Wszystkie pliki mają określone priorytety
5. **Aktualność** - Priorytety odzwierciedlają aktualny stan kodu

### WERYFIKACJA PRIORYTETÓW

**Po określeniu priorytetów sprawdź:**

- ✅ Czy wszystkie pliki mają określone priorytety?
- ✅ Czy priorytety są uzasadnione analizą kodu?
- ✅ Czy finalne priorytety są logiczne?
- ✅ Czy nie ma sprzeczności w priorytetach?
- ✅ Czy priorytety odzwierciedlają rzeczywistą ważność plików?

---

**Dokument wygenerowany na podstawie analizy celów i założeń audytu.**  
**Ostatnia aktualizacja:** 2024-12-19  
**Wersja:** 1.0
