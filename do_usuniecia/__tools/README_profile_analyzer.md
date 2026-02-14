# 📊 Skrypt Profilowania CFAB Browser

## 🎯 Cel

Skrypt `profile_analyzer.py` służy do analizy wydajności aplikacji CFAB Browser za pomocą modułu `cProfile`. Pozwala na:

- Profilowanie całej aplikacji przez określony czas
- Analizę pojedynczych funkcji
- Generowanie szczegółowych raportów wydajności
- Identyfikację wąskich gardeł

## 🚀 Użycie

### Podstawowe profilowanie aplikacji

```bash
# Profiluj aplikację przez 30 sekund (domyślnie)
python __tools/profile_analyzer.py

# Profiluj przez określony czas (w sekundach)
python __tools/profile_analyzer.py --duration 60

# Profiluj inny skrypt
python __tools/profile_analyzer.py --script run.py --duration 45
```

### Analiza istniejącego pliku .stats

```bash
# Analizuj istniejący plik statystyk
python __tools/profile_analyzer.py --stats __raports/profile_stats_20250105_143022.stats

# Analizuj z większą liczbą top funkcji
python __tools/profile_analyzer.py --stats profile_stats.stats --top 100
```

## 📁 Struktura Wyjściowa

Skrypt generuje pliki w katalogu `__raports/`:

```
__raports/
├── profile_stats_20250105_143022.stats    # Plik statystyk cProfile
├── profile_report_20250105_143022.txt     # Czytelny raport
└── analysis_existing_stats_20250105_143022.txt  # Analiza istniejących danych
```

## 📊 Format Raportu

Raport zawiera:

### 1. Statystyki Ogólne

- Całkowity czas wykonania
- Liczba wywołań funkcji
- Liczba pierwotnych wywołań

### 2. Top Funkcje Według Czasu

- Funkcje z największym czasem wykonania
- Sortowane według czasu kumulacyjnego

### 3. Top Funkcje Według Wywołań

- Funkcje z największą liczbą wywołań
- Sortowane według liczby wywołań

### 4. Analiza Wąskich Gardeł

- Funkcje z czasem > 0.1s
- Rekomendacje optymalizacyjne

## 🔧 Opcje Skryptu

| Opcja        | Opis                               | Domyślna          |
| ------------ | ---------------------------------- | ----------------- |
| `--script`   | Ścieżka do skryptu aplikacji       | `cfab_browser.py` |
| `--duration` | Czas profilowania w sekundach      | `30`              |
| `--stats`    | Analizuj istniejący plik .stats    | -                 |
| `--top`      | Liczba top funkcji do wyświetlenia | `50`              |

## 💡 Przykłady Użycia

### 1. Szybka Analiza Wydajności

```bash
python __tools/profile_analyzer.py --duration 10
```

### 2. Szczegółowa Analiza

```bash
python __tools/profile_analyzer.py --duration 120 --top 100
```

### 3. Analiza Konkretnej Funkcji

```python
from __tools.profile_analyzer import ProfileAnalyzer

analyzer = ProfileAnalyzer()

# Profiluj konkretną funkcję
def moja_funkcja():
    # kod do sprofilowania
    pass

result = analyzer.profile_function(moja_funkcja)
```

### 4. Analiza Istniejących Danych

```bash
# Znajdź pliki .stats
find __raports/ -name "*.stats"

# Analizuj konkretny plik
python __tools/profile_analyzer.py --stats __raports/profile_stats_20250105_143022.stats
```

## 🎯 Interpretacja Wyników

### Dobra Wydajność

- Brak funkcji z czasem > 0.1s
- Równomierne rozłożenie wywołań
- Niska złożoność cyklomatyczna

### Problemy do Naprawy

- Funkcje z czasem > 1s
- Duża liczba wywołań prostych funkcji
- Długie pętle lub operacje I/O

## 🔍 Rekomendacje Optymalizacyjne

### 1. Cachowanie

```python
# Przed optymalizacją
def kosztowna_funkcja():
    # długie obliczenia
    pass

# Po optymalizacji
from functools import lru_cache

@lru_cache(maxsize=128)
def kosztowna_funkcja():
    # długie obliczenia
    pass
```

### 2. Asynchroniczność

```python
# Przed optymalizacją
def operacja_io():
    # blokująca operacja I/O
    pass

# Po optymalizacji
import asyncio

async def operacja_io():
    # asynchroniczna operacja I/O
    pass
```

### 3. Optymalizacja Pętli

```python
# Przed optymalizacją
for item in lista:
    if item > 0:
        wynik.append(item * 2)

# Po optymalizacji
wynik = [item * 2 for item in lista if item > 0]
```

## ⚠️ Uwagi

1. **Czas Profilowania**: Dłuższy czas = dokładniejsze wyniki, ale większe pliki
2. **Wpływ Profilowania**: cProfile dodaje overhead ~10-30%
3. **Pamięć**: Duże aplikacje mogą generować duże pliki .stats
4. **Środowisko**: Profiluj w środowisku produkcyjnym dla dokładnych wyników

## 🛠️ Rozwiązywanie Problemów

### Błąd: "Plik nie istnieje"

```bash
# Sprawdź czy plik istnieje
ls -la cfab_browser.py

# Użyj pełnej ścieżki
python __tools/profile_analyzer.py --script ./cfab_browser.py
```

### Błąd: "Brak uprawnień"

```bash
# Nadaj uprawnienia wykonywania
chmod +x __tools/profile_analyzer.py
```

### Duży Plik .stats

```bash
# Użyj krótszego czasu profilowania
python __tools/profile_analyzer.py --duration 10
```

## 📈 Integracja z CI/CD

Możesz zintegrować profilowanie z pipeline'em CI/CD:

```yaml
# .github/workflows/profile.yml
name: Performance Profiling
on: [push, pull_request]

jobs:
  profile:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run profiling
        run: python __tools/profile_analyzer.py --duration 30
      - name: Upload results
        uses: actions/upload-artifact@v2
        with:
          name: profile-results
          path: __raports/
```

## 📞 Wsparcie

W przypadku problemów:

1. Sprawdź logi w konsoli
2. Zweryfikuj uprawnienia plików
3. Sprawdź czy aplikacja uruchamia się poprawnie
4. Użyj krótszego czasu profilowania dla testów
