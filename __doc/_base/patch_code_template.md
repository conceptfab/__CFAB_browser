# SZABLON FRAGMENTÓW KODU DO IMPLEMENTACJI - AUDYT LOGIKI BIZNESOWEJ


> **LOKALIZACJA:** `AUDYT/patches/[nazwa_pliku]_patch_code.md`  
> **STATUS:** Fragmenty kodu do implementacji dla pliku `[nazwa_pliku].py`  
> **DATA GENEROWANIA:** [DATA_GENEROWANIA]

---

## 📄 ANALIZOWANY PLIK

**Plik:** `[ŚCIEŻKA_DO_PLIKU]`  
**Priorytet struktury:** [PRIORYTET_STRUKTURY] - [UZASADNIENIE]  
**Priorytet poprawek:** [PRIORYTET_POPRAWEK] - [UZASADNIENIE]  
**Finalny priorytet:** [FINALNY_PRIORYTET] - [UZASADNIENIE PROCESU MYŚLOWEGO]

---

## 🎯 CEL POPRAWKI

[OPIS_CELU_POPRAWKI_NA_PODSTAWIE_ANALIZY_KODU]

---

## 💼 BUSINESS IMPACT

[OPIS_WPŁYWU_NA_PROCESY_BIZNESOWE_NA_PODSTAWIE_ANALIZY]

---

## 🔧 FRAGMENTY KODU DO IMPLEMENTACJI

### 1. [NAZWA_ZMIANY_1]

**Cel:** [OPIS_CELU_ZMIANY]  
**Lokalizacja:** [LINIE_KODU_LUB_KLASY]  
**Metoda:** [SZCZEGÓŁOWY_OPIS_METODY]

```python
# OLD (bieżący kod)
[BIEŻĄCY_KOD_DO_ZMIANY]

# NEW (proponowany kod)
[PROPONOWANY_KOD]
```

**Uzasadnienie:** [DLACZEGO TA ZMIANA JEST POTRZEBNA]

### 2. [NAZWA_ZMIANY_2]

**Cel:** [OPIS_CELU_ZMIANY]  
**Lokalizacja:** [LINIE_KODU_LUB_KLASY]  
**Metoda:** [SZCZEGÓŁOWY_OPIS_METODY]

```python
# OLD (bieżący kod)
[BIEŻĄCY_KOD_DO_ZMIANY]

# NEW (proponowany kod)
[PROPONOWANY_KOD]
```

**Uzasadnienie:** [DLACZEGO TA ZMIANA JEST POTRZEBNA]

---

## 📋 INSTRUKCJE IMPLEMENTACJI

### KROK 1: PRZYGOTOWANIE

1. **Utwórz backup** pliku w `AUDYT/backups/[nazwa_pliku]_backup_[data].py`
2. **Przeanalizuj zależności** - sprawdź wszystkie importy i wywołania
3. **Zidentyfikuj publiczne API** - lista metod używanych przez inne pliki
4. **Przygotuj testy regresji** - upewnij się, że możesz zweryfikować zmiany

### KROK 2: IMPLEMENTACJA

1. **Wprowadź zmiany krok po kroku** - jedna logiczna zmiana na raz
2. **Zachowaj kompatybilność wsteczną** - 100% backward compatibility
3. **Zachowaj publiczne API** - lub dodaj deprecation warnings
4. **Testuj po każdej zmianie** - upewnij się, że kod działa

### KROK 3: WERYFIKACJA

1. **Uruchom testy automatyczne** - wszystkie testy muszą przejść
2. **Sprawdź uruchomienie aplikacji** - aplikacja musi się uruchamiać
3. **Weryfikuj funkcjonalność** - wszystkie funkcje muszą działać
4. **Sprawdź integrację** - inne moduły muszą nadal działać

---

## ✅ CHECKLISTA WERYFIKACYJNA

**Każda zmiana musi przejść tę checklistę przed oznaczeniem jako ukończona:**

### 🛡️ Bezpieczeństwo refaktoryzacji

- [ ] **BACKUP PRZED ZMIANĄ** - Utworzono kopię bezpieczeństwa w `AUDYT/backups/`
- [ ] **INKREMENTALNE ZMIANY** - Wprowadzono małe, weryfikowalne kroki
- [ ] **ZACHOWANIE FUNKCJONALNOŚCI** - 100% backward compatibility
- [ ] **ROLLBACK PLAN** - Istnieje możliwość cofnięcia zmian
- [ ] **WERYFIKACJA INTEGRACJI** - Sprawdzono, że zmiana nie psuje innych części

### 🧪 Automatyczne testy

- [ ] **TESTY FUNKCJONALNOŚCI** - Wszystkie testy PASS (0 FAIL)
- [ ] **TESTY INTEGRACYJNE** - Zmiana nie psuje innych części systemu
- [ ] **TESTY WYDAJNOŚCI** - Wydajność nie pogorszona o więcej niż 5%
- [ ] **POKRYCIE KODU** - >80% dla nowych funkcji

### 📋 Funkcjonalności

- [ ] **PODSTAWOWA FUNKCJONALNOŚĆ** - Działa poprawnie
- [ ] **KOMPATYBILNOŚĆ API** - Zachowane publiczne interfejsy
- [ ] **OBSŁUGA BŁĘDÓW** - Proper error handling
- [ ] **WALIDACJA** - Dane są prawidłowo walidowane
- [ ] **LOGOWANIE** - Logi są generowane poprawnie
- [ ] **CACHE** - Cache działa prawidłowo
- [ ] **THREAD SAFETY** - Operacje są thread-safe
- [ ] **WYDAJNOŚĆ** - Nie ma regresji wydajności

### 🔗 Zależności

- [ ] **IMPORTY** - Wszystkie importy działają
- [ ] **ZALEŻNOŚCI ZEWNĘTRZNE** - Zewnętrzne biblioteki działają
- [ ] **ZALEŻNOŚCI WEWNĘTRZNE** - Wewnętrzne moduły działają
- [ ] **BRAK CYKLICZNYCH ZALEŻNOŚCI** - Nie ma cykli importów
- [ ] **KOMPATYBILNOŚĆ WSTECZNA** - Zachowana kompatybilność

### 📊 Dokumentacja

- [ ] **README** - Zaktualizowany jeśli potrzebne
- [ ] **API DOCS** - Zaktualizowane jeśli potrzebne
- [ ] **CHANGELOG** - Dodano wpis o zmianie
- [ ] **KOMENTARZE** - Kod jest odpowiednio udokumentowany

---

## 🚨 KRYTYCZNE: PO ZAKOŃCZENIU WSZYSTKICH POPRAWEK MODEL MUSI OBAWIĄZKOWO UZUPEŁNIĆ PLIKI:

1. **`AUDYT/business_logic_map.md`** - Status ukończenia analizy
2. **`AUDYT/implementation_plan.md`** - Dodanie poprawki do planu implementacji

**Format uzupełnienia w business_logic_map.md:**

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

**Dokument wygenerowany automatycznie na podstawie analizy pliku `[nazwa_pliku].py`.**  
**Ostatnia aktualizacja:** [DATA_AKTUALIZACJI]  
**Wersja:** 1.0
