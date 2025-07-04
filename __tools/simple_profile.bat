@echo off
REM Prosty skrypt do profilowania CFAB Browser
REM Autor: CFAB Browser Team
REM Data: 2025-01-05

echo.
echo ========================================
echo    PROSTE PROFILOWANIE CFAB BROWSER
echo ========================================
echo.

REM Sprawdź czy Python jest dostępny
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Błąd: Python nie jest zainstalowany
    pause
    exit /b 1
)

REM Sprawdź czy skrypt profilowania istnieje
if not exist "profile_analyzer.py" (
    echo ❌ Błąd: Plik profile_analyzer.py nie istnieje
    pause
    exit /b 1
)

REM Sprawdź czy główny skrypt aplikacji istnieje
if not exist "..\cfab_browser.py" (
    echo ❌ Błąd: Plik cfab_browser.py nie istnieje
    pause
    exit /b 1
)

echo 🚀 Uruchamiam profilowanie aplikacji...
echo 💡 Aplikacja będzie działać normalnie - możesz ją testować!
echo ⏱️  Profilowanie potrwa 30 sekund
echo.

REM Uruchom profilowanie
python profile_analyzer.py --script "..\cfab_browser.py" --duration 30

echo.
echo ✅ Profilowanie zakończone!
echo 📁 Sprawdź wyniki w katalogu __raports
echo.

pause 