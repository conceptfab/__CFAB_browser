# SZABLON MAPY LOGIKI BIZNESOWEJ - AUDYT LOGIKI BIZNESOWEJ

> **LOKALIZACJA:** `AUDYT/business_logic_map.md`  
> **STATUS:** Mapa logiki biznesowej aplikacji  
> **DATA GENEROWANIA:** [DATA_GENEROWANIA]

---

## 🎯 CEL DOKUMENTU

Mapa logiki biznesowej przedstawia strukturę i priorytety plików zawierających logikę biznesową aplikacji. Dokument jest generowany dynamicznie na podstawie analizy aktualnego kodu i kontekstu biznesowego.

---

## 📊 DWUFAZOWY PROCES OKREŚLANIA PRIORYTETÓW

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
- Problemy z zarządzaniem pamięci
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

## 🗺️ MAPA PLIKÓW FUNKCJONALNOŚCI BIZNESOWEJ

**Wygenerowano na podstawie aktualnego kodu: [DATA]**

**Odkryte katalogi z logiką biznesową:**

- [KATALOG_1] - [OPIS ROLI W LOGICE BIZNESOWEJ]
- [KATALOG_2] - [OPIS ROLI W LOGICE BIZNESOWEJ]
- [KATALOG_3] - [OPIS ROLI W LOGICE BIZNESOWEJ]

### **[NAZWA_KATALOGU_1]** ([ŚCIEŻKA_KATALOGU])

```
[ŚCIEŻKA_KATALOGU]/
├── [nazwa_pliku].py [PRIORYTET_STRUKTURY]/[PRIORYTET_POPRAWEK] → FINALNY: [FINALNY] - [OPIS FUNKCJI BIZNESOWEJ]
├── [nazwa_pliku].py [PRIORYTET_STRUKTURY]/[PRIORYTET_POPRAWEK] → FINALNY: [FINALNY] - [OPIS FUNKCJI BIZNESOWEJ]
└── [nazwa_pliku].py [PRIORYTET_STRUKTURY]/[PRIORYTET_POPRAWEK] → FINALNY: [FINALNY] - [OPIS FUNKCJI BIZNESOWEJ]
```

### **[NAZWA_KATALOGU_2]** ([ŚCIEŻKA_KATALOGU])

```
[ŚCIEŻKA_KATALOGU]/
├── [nazwa_pliku].py [PRIORYTET_STRUKTURY]/[PRIORYTET_POPRAWEK] → FINALNY: [FINALNY] - [OPIS FUNKCJI BIZNESOWEJ]
├── [nazwa_pliku].py [PRIORYTET_STRUKTURY]/[PRIORYTET_POPRAWEK] → FINALNY: [FINALNY] - [OPIS FUNKCJI BIZNESOWEJ]
└── [nazwa_pliku].py [PRIORYTET_STRUKTURY]/[PRIORYTET_POPRAWEK] → FINALNY: [FINALNY] - [OPIS FUNKCJI BIZNESOWEJ]
```

---

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
- **Pliki wynikowe:**
  - `AUDYT/corrections/[nazwa_pliku]_correction.md`
  - `AUDYT/patches/[nazwa_pliku]_patch_code.md`

---

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

---

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

---

## 🚨 KRYTYCZNE ZASADY - MODEL MUSI PAMIĘTAĆ!

### 📋 **OBOWIĄZKOWE UZUPEŁNIANIE DOKUMENTÓW AUDYTU**

**🚨 MODEL MUSI PAMIĘTAĆ: Po każdej ukończonej analizie pliku logiki biznesowej OBAWIĄZKOWO uzupełnić pliki:**

- `AUDYT/business_logic_map.md` - status ukończenia analizy
- `AUDYT/implementation_plan.md` - dodanie poprawki do planu implementacji

**OBOWIĄZKOWE KROKI PO KAŻDEJ ANALIZIE:**

1. ✅ **Ukończ analizę pliku** - utwórz correction.md i patch_code.md
2. ✅ **OTWÓRZ business_logic_map.md** - znajdź sekcję z analizowanym plikiem
3. ✅ **DODAJ status ukończenia** - zaznacz że analiza została ukończona
4. ✅ **DODAJ datę ukończenia** - aktualna data w formacie YYYY-MM-DD
5. ✅ **DODAJ business impact** - opis wpływu na procesy biznesowe
6. ✅ **DODAJ ścieżki do plików wynikowych** - correction.md i patch_code.md
7. ✅ **OTWÓRZ implementation_plan.md** - dodaj poprawkę do odpowiedniej sekcji priorytetowej
8. ✅ **ZAKTUALIZUJ statystyki** - liczba plików i poprawek w planie implementacji

**FORMAT UZUPEŁNIENIA W BUSINESS_LOGIC_MAP.MD:**

```markdown
### 📄 [NAZWA_PLIKU].PY

- **Status:** ✅ UKOŃCZONA ANALIZA
- **Data ukończenia:** [DATA]
- **Business impact:** [OPIS WPŁYWU NA PROCESY BIZNESOWE]
- **Pliki wynikowe:**
  - `AUDYT/corrections/[nazwa_pliku]_correction.md`
  - `AUDYT/patches/[nazwa_pliku]_patch_code.md`
```

**🚨 MODEL NIE MOŻE ZAPOMNIEĆ O TYM KROKU!**

---

**Dokument wygenerowany automatycznie na podstawie analizy kodu i kontekstu biznesowego.**  
**Ostatnia aktualizacja:** [DATA_AKTUALIZACJI]  
**Wersja:** 1.0
