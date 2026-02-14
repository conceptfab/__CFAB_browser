# 📋 SZCZEGÓŁOWA ANALIZA PLIKU - INSTRUKCJE

## 🎯 CEL ZADANIA

**Szczegółowy cel tego zadania znajduje się w pliku `cel_zadania.md`**

Analizujemy **JEDEN WYBRANY PLIK** logiki biznesowej i przygotowujemy konkretne poprawki.

**Co robimy:**

- ✅ Analizujemy JEDEN plik pod kątem problemów
- ✅ Identyfikujemy konkretne błędy i nieoptymalności
- ✅ Przygotowujemy gotowe poprawki z kodem
- ✅ Tworzymy prosty plan implementacji

**⚠️ KRYTYCZNE:** Zachowanie 100% funkcjonalności pliku jest OBOWIĄZKOWE!

## 📋 INSTRUKCJA ANALIZY

### KROK 1: Wybierz plik

- Otwórz plik `.py` z logiką biznesową
- Sprawdź czy ma wpływ na wydajność/stabilność
- Upewnij się że wymaga poprawek

### KROK 2: Przeanalizuj kod

**Co szukasz:**

- **Błędy logiczne** - nieprawidłowe algorytmy, edge cases
- **Problemy wydajnościowe** - wolne algorytmy, memory leaks
- **Code smells** - duplikacja, długie funkcje, magic numbers
- **Problemy stabilności** - thread safety, error handling
- **Over-engineering** - niepotrzebne abstrakcje, złożone wzorce

**Jak analizować:**

1. **Przeczytaj kod** - zrozum co robi
2. **Zidentyfikuj problemy** - zapisz co jest nie tak
3. **Oceń wpływ** - jak problem wpływa na aplikację
4. **Ustal priorytet** - krytyczne/wysokie/średnie/niskie

### KROK 3: Przygotuj poprawki

**Dla każdego problemu:**

1. **Opisz problem** - co jest nie tak
2. **Zaproponuj rozwiązanie** - jak to naprawić
3. **Przygotuj kod** - gotowe fragmenty do wklejenia
4. **Oszacuj czas** - ile zajmie implementacja

### KROK 4: Stwórz plan

**Plan implementacji:**

1. **Kolejność** - w jakiej kolejności wprowadzać zmiany
2. **Kroki** - szczegółowe instrukcje
3. **Testy** - jak zweryfikować poprawki
4. **Rollback** - jak cofnąć jeśli coś pójdzie źle

## 📄 SZABLONY DO UŻYCIA

### 0. `cel_zadania.md` - Cel całego audytu

Ten plik zawiera:

- Cel całego audytu aplikacji
- Obszary do przeanalizowania
- Kryteria sukcesu refaktoryzacji
- Plan działania na poziomie projektu

### 1. `szablon_analizy.md` - Analiza problemów

Użyj tego szablonu do:

- Opisania wszystkich problemów w pliku
- Ustalenia priorytetów
- Przygotowania rozwiązań
- Stworzenia planu implementacji

### 2. `szablon_poprawek.md` - Gotowe poprawki

Użyj tego szablonu do:

- Przygotowania konkretnego kodu do wklejenia
- Instrukcji implementacji
- Weryfikacji poprawek
- Procedury rollback

## 🎯 KRYTERIA WYBORU PLIKU

- Plik z logiką biznesową (nie testy, nie dokumentacja)
- Plik który ma wpływ na wydajność/stabilność
- Plik który faktycznie wymaga poprawek

## 📊 WYNIK KOŃCOWY

1. **Analiza problemów** - lista tego co jest nie tak
2. **Gotowe poprawki** - kod do wklejenia
3. **Plan implementacji** - jak to wdrożyć

## 🚀 JAK ZACZĄĆ

1. Przeczytaj `cel_zadania.md` - poznaj cel audytu
2. Wybierz plik do analizy
3. Skopiuj `szablon_analizy.md` jako `analiza_[NAZWA_PLIKU].md` i wypełnij
4. Skopiuj `szablon_poprawek.md` jako `poprawki_[NAZWA_PLIKU].md` i wypełnij
5. Zaimplementuj poprawki krok po kroku

**To wszystko. Proste i praktyczne.**
