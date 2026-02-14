# 🛠️ Narzędzia CFAB Browser

## 📊 Narzędzia Profilowania i Analizy

### 🚀 Szybki Start

1. **Instalacja narzędzi:**

   ```bash
   cd __tools
   install_profile_tools.bat
   ```

2. **Proste profilowanie:**

   ```bash
   cd __tools
   simple_profile.bat
   ```

3. **Zaawansowane profilowanie:**
   ```bash
   cd __tools
   run_profile.bat
   ```

## 📁 Struktura Plików

```
__tools/
├── profile_analyzer.py          # Główny skrypt profilowania
├── quick_profile.py             # Szybkie profilowanie funkcji
├── run_profile.bat              # Menu profilowania (Windows)
├── simple_profile.bat           # Proste profilowanie (Windows)
├── install_profile_tools.bat    # Instalacja narzędzi (Windows)
├── requirements_profile.txt     # Zależności Python
├── README_profile_analyzer.md   # Dokumentacja profilowania
└── README_TOOLS.md             # Ten plik
```

## 🔧 Dostępne Narzędzia

### 1. **Profile Analyzer** (`profile_analyzer.py`)

- **Cel:** Kompleksowe profilowanie aplikacji
- **Funkcje:**
  - Profilowanie całej aplikacji przez określony czas
  - Analiza pojedynczych funkcji
  - Generowanie szczegółowych raportów
  - Identyfikacja wąskich gardeł

**Użycie:**

```bash
# Profilowanie aplikacji przez 30 sekund
python profile_analyzer.py

# Profilowanie przez określony czas
python profile_analyzer.py --duration 60

# Analiza istniejącego pliku .stats
python profile_analyzer.py --stats __raports/profile_stats_20250105_143022.stats
```

### 2. **Quick Profile** (`quick_profile.py`)

- **Cel:** Szybkie profilowanie konkretnych funkcji
- **Funkcje:**
  - Profilowanie pojedynczych funkcji
  - Analiza czasu importu modułów
  - Profilowanie operacji na plikach
  - Monitorowanie użycia pamięci

**Użycie:**

```bash
# Uruchom przykłady
python quick_profile.py

# Użyj w kodzie
from quick_profile import quick_profile_function
result = quick_profile_function(moja_funkcja, argumenty)
```

### 3. **Skrypty Batch (Windows)**

#### `simple_profile.bat`

- **Cel:** Proste profilowanie bez menu
- **Użycie:** Podwójne kliknięcie
- **Czas:** 30 sekund

#### `run_profile.bat`

- **Cel:** Menu z opcjami profilowania
- **Opcje:**
  1. Szybkie profilowanie (30s)
  2. Średnie profilowanie (60s)
  3. Długie profilowanie (120s)
  4. Własny czas profilowania
  5. Szybkie profilowanie funkcji
  6. Analiza istniejącego pliku .stats
  7. Wyjście

#### `install_profile_tools.bat`

- **Cel:** Instalacja wszystkich narzędzi
- **Instaluje:**
  - psutil (monitorowanie pamięci)
  - memory-profiler (profilowanie pamięci)
  - pylint (analiza statyczna)
  - flake8 (linter)
  - black (formatowanie)
  - isort (sortowanie importów)
  - radon (złożoność cyklomatyczna)
  - bandit (bezpieczeństwo)
  - coverage (pokrycie testami)

## 📊 Raporty i Wyniki

### Struktura Wyjściowa

```
__raports/
├── profile_stats_20250105_143022.stats    # Plik statystyk cProfile
├── profile_report_20250105_143022.txt     # Czytelny raport
├── function_profile_nazwa_20250105_143022.stats  # Profil funkcji
├── function_report_nazwa_20250105_143022.txt     # Raport funkcji
└── analysis_existing_stats_20250105_143022.txt   # Analiza istniejących danych
```

### Format Raportu

1. **Statystyki Ogólne**

   - Całkowity czas wykonania
   - Liczba wywołań funkcji
   - Liczba pierwotnych wywołań

2. **Top Funkcje Według Czasu**

   - Funkcje z największym czasem wykonania
   - Sortowane według czasu kumulacyjnego

3. **Top Funkcje Według Wywołań**

   - Funkcje z największą liczbą wywołań
   - Sortowane według liczby wywołań

4. **Analiza Wąskich Gardeł**
   - Funkcje z czasem > 0.1s
   - Rekomendacje optymalizacyjne

## 🎯 Przykłady Użycia

### 1. Szybka Analiza Wydajności

```bash
cd __tools
simple_profile.bat
```

### 2. Szczegółowa Analiza

```bash
cd __tools
python profile_analyzer.py --duration 120 --top 100
```

### 3. Analiza Konkretnej Funkcji

```python
from __tools.quick_profile import quick_profile_function

def moja_funkcja():
    # kod do sprofilowania
    pass

result = quick_profile_function(moja_funkcja, iterations=1000)
```

### 4. Analiza Istniejących Danych

```bash
cd __tools
python profile_analyzer.py --stats ../__raports/profile_stats_20250105_143022.stats
```

## 🔍 Interpretacja Wyników

### Dobra Wydajność ✅

- Brak funkcji z czasem > 0.1s
- Równomierne rozłożenie wywołań
- Niska złożoność cyklomatyczna

### Problemy do Naprawy ⚠️

- Funkcje z czasem > 1s
- Duża liczba wywołań prostych funkcji
- Długie pętle lub operacje I/O

## 💡 Rekomendacje Optymalizacyjne

### 1. Cachowanie

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def kosztowna_funkcja():
    # długie obliczenia
    pass
```

### 2. Asynchroniczność

```python
import asyncio

async def operacja_io():
    # asynchroniczna operacja I/O
    pass
```

### 3. Optymalizacja Pętli

```python
# Przed
for item in lista:
    if item > 0:
        wynik.append(item * 2)

# Po
wynik = [item * 2 for item in lista if item > 0]
```

## ⚠️ Uwagi

1. **Czas Profilowania:** Dłuższy czas = dokładniejsze wyniki
2. **Wpływ Profilowania:** cProfile dodaje overhead ~10-30%
3. **Pamięć:** Duże aplikacje mogą generować duże pliki .stats
4. **Środowisko:** Profiluj w środowisku produkcyjnym dla dokładnych wyników

## 🛠️ Rozwiązywanie Problemów

### Błąd: "Plik nie istnieje"

```bash
# Sprawdź czy plik istnieje
ls -la cfab_browser.py

# Użyj pełnej ścieżki
python profile_analyzer.py --script ./cfab_browser.py
```

### Błąd: "Brak uprawnień"

```bash
# Nadaj uprawnienia wykonywania
chmod +x profile_analyzer.py
```

### Duży Plik .stats

```bash
# Użyj krótszego czasu profilowania
python profile_analyzer.py --duration 10
```

## 📈 Integracja z CI/CD

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
        run: pip install -r __tools/requirements_profile.txt
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
5. Sprawdź czy wszystkie zależności są zainstalowane

## 🔄 Aktualizacje

Aby zaktualizować narzędzia:

```bash
cd __tools
pip install -r requirements_profile.txt --upgrade
```

## 📚 Dodatkowe Zasoby

- [Dokumentacja cProfile](https://docs.python.org/3/library/profile.html)
- [Dokumentacja psutil](https://psutil.readthedocs.io/)
- [Dokumentacja pylint](https://pylint.pycqa.org/)
- [Dokumentacja black](https://black.readthedocs.io/)
- [Dokumentacja radon](https://radon.readthedocs.io/)
