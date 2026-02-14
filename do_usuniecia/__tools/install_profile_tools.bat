@echo off
REM Skrypt instalacyjny narzędzi profilowania CFAB Browser
REM Autor: CFAB Browser Team
REM Data: 2025-01-05

echo.
echo ========================================
echo    INSTALACJA NARZĘDZI PROFILOWANIA
echo ========================================
echo.

REM Sprawdź czy Python jest dostępny
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Błąd: Python nie jest zainstalowany lub nie jest w PATH
    echo    Zainstaluj Python z https://python.org
    pause
    exit /b 1
)

echo ✅ Python jest dostępny
echo.

REM Sprawdź czy pip jest dostępny
pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Błąd: pip nie jest dostępny
    echo    Zainstaluj pip lub zaktualizuj Python
    pause
    exit /b 1
)

echo ✅ pip jest dostępny
echo.

REM Aktualizuj pip
echo 🔄 Aktualizuję pip...
python -m pip install --upgrade pip

echo.
echo 📦 Instaluję podstawowe narzędzia profilowania...
echo.

REM Instaluj podstawowe narzędzia
echo 1️⃣ psutil - monitorowanie pamięci
pip install psutil>=5.9.0

echo 2️⃣ memory-profiler - profilowanie pamięci
pip install memory-profiler>=0.60.0

echo 3️⃣ pylint - analiza statyczna
pip install pylint>=2.17.0

echo 4️⃣ flake8 - linter
pip install flake8>=6.0.0

echo 5️⃣ black - formatowanie
pip install black>=23.0.0

echo 6️⃣ isort - sortowanie importów
pip install isort>=5.12.0

echo 7️⃣ radon - złożoność cyklomatyczna
pip install radon>=5.1.0

echo 8️⃣ bandit - bezpieczeństwo
pip install bandit>=1.7.0

echo 9️⃣ coverage - pokrycie testami
pip install coverage>=7.2.0

echo.
echo 📦 Instaluję opcjonalne narzędzia...
echo.

REM Instaluj opcjonalne narzędzia
echo 🔧 line-profiler - profilowanie liniowe
pip install line-profiler>=4.0.0

echo 🔧 py-spy - profilowanie z małym overhead
pip install py-spy>=0.3.0

echo 🔧 matplotlib - wykresy
pip install matplotlib>=3.7.0

echo.
echo ✅ Instalacja zakończona!
echo.
echo 📋 Zainstalowane narzędzia:
echo    • cProfile (wbudowany w Python)
echo    • psutil - monitorowanie pamięci
echo    • memory-profiler - profilowanie pamięci
echo    • pylint - analiza statyczna
echo    • flake8 - linter
echo    • black - formatowanie
echo    • isort - sortowanie importów
echo    • radon - złożoność cyklomatyczna
echo    • bandit - bezpieczeństwo
echo    • coverage - pokrycie testami
echo    • line-profiler - profilowanie liniowe
echo    • py-spy - profilowanie z małym overhead
echo    • matplotlib - wykresy
echo.
echo 🚀 Możesz teraz używać narzędzi profilowania:
echo    • python __tools/profile_analyzer.py
echo    • python __tools/quick_profile.py
echo    • python -m cProfile cfab_browser.py
echo.
pause 