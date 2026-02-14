# SZABLON POPRAWEK
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



## 📄 PLIK: `[NAZWA_PLIKU].py`

## 🔧 POPRAWKA 1: [NAZWA_PROBLEMU]

### Problem:

```python
# LINIE [X-Y] - CO JEST NIE TAK
[FRAGMENT_KODU_Z_PROBLEMEM]
```

### Rozwiązanie:

```python
# NOWY KOD DO WKLEJENIA
[POPRAWIONY_KOD]
```

### Instrukcja:

1. Znajdź linie [X-Y]
2. Zastąp stary kod nowym
3. Sprawdź czy nie ma błędów składni

---

## 🔧 POPRAWKA 2: [NAZWA_PROBLEMU]

### Problem:

```python
# LINIE [X-Y] - CO JEST NIE TAK
[FRAGMENT_KODU_Z_PROBLEMEM]
```

### Rozwiązanie:

```python
# NOWY KOD DO WKLEJENIA
[POPRAWIONY_KOD]
```

### Instrukcja:

1. Znajdź linie [X-Y]
2. Zastąp stary kod nowym
3. Sprawdź czy nie ma błędów składni

---

## 🔧 POPRAWKA 3: [NAZWA_PROBLEMU]

### Problem:

```python
# LINIE [X-Y] - CO JEST NIE TAK
[FRAGMENT_KODU_Z_PROBLEMEM]
```

### Rozwiązanie:

```python
# NOWY KOD DO WKLEJENIA
[POPRAWIONY_KOD]
```

### Instrukcja:

1. Znajdź linie [X-Y]
2. Zastąp stary kod nowym
3. Sprawdź czy nie ma błędów składni

---

## ✅ WERYFIKACJA

### Po każdej poprawce:

- [ ] Kod się kompiluje
- [ ] Funkcjonalność działa
- [ ] Nie zepsułeś nic innego

### Testy:

```python
# PRZYKŁAD TESTU
[KOD_DO_PRZETESTOWANIA_POPRAWKI]
```

## 🔄 ROLLBACK

Jeśli coś pójdzie źle:

1. Przywróć backup pliku
2. Spróbuj poprawkę ponownie
3. Sprawdź czy nie ma konfliktów z innymi zmianami
