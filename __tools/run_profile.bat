@echo off
REM Skrypt do uruchamiania profilowania CFAB Browser
REM Autor: CFAB Browser Team
REM Data: 2025-01-05

echo.
echo ========================================
echo    PROFILOWANIE CFAB BROWSER
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

REM Sprawdź czy skrypt profilowania istnieje
if not exist "profile_analyzer.py" (
    echo ❌ Błąd: Plik profile_analyzer.py nie istnieje
    echo    Upewnij się, że jesteś w katalogu __tools
    pause
    exit /b 1
)

REM Sprawdź czy główny skrypt aplikacji istnieje
if not exist "..\cfab_browser.py" (
    echo ❌ Błąd: Plik cfab_browser.py nie istnieje
    echo    Upewnij się, że jesteś w głównym katalogu projektu
    pause
    exit /b 1
)

:menu
echo 🎯 Wybierz opcję profilowania:
echo.
echo 1️⃣ Szybkie profilowanie (30s)
echo 2️⃣ Średnie profilowanie (60s)
echo 3️⃣ Długie profilowanie (120s)
echo 4️⃣ Własny czas profilowania
echo 5️⃣ Szybkie profilowanie funkcji
echo 6️⃣ Analiza istniejącego pliku .stats
echo 7️⃣ Wyjście
echo.
set /p choice="Wybierz opcję (1-7): "

if "%choice%"=="1" goto quick_profile
if "%choice%"=="2" goto medium_profile
if "%choice%"=="3" goto long_profile
if "%choice%"=="4" goto custom_profile
if "%choice%"=="5" goto function_profile
if "%choice%"=="6" goto analyze_stats
if "%choice%"=="7" goto exit
echo ❌ Nieprawidłowy wybór. Spróbuj ponownie.
goto menu

:quick_profile
echo.
echo 🚀 Uruchamiam szybkie profilowanie (30s)...
python profile_analyzer.py --script "..\cfab_browser.py" --duration 30
goto end

:medium_profile
echo.
echo 🚀 Uruchamiam średnie profilowanie (60s)...
python profile_analyzer.py --script "..\cfab_browser.py" --duration 60
goto end

:long_profile
echo.
echo 🚀 Uruchamiam długie profilowanie (120s)...
python profile_analyzer.py --script "..\cfab_browser.py" --duration 120
goto end

:custom_profile
echo.
set /p duration="Podaj czas profilowania w sekundach: "
echo 🚀 Uruchamiam profilowanie (%duration%s)...
python profile_analyzer.py --script "..\cfab_browser.py" --duration %duration%
goto end

:function_profile
echo.
echo 🚀 Uruchamiam szybkie profilowanie funkcji...
python quick_profile.py
goto end

:analyze_stats
echo.
echo 📁 Dostępne pliki .stats:
dir "..\__raports\*.stats" 2>nul
if errorlevel 1 (
    echo ❌ Brak plików .stats w katalogu __raports
    goto menu
)
echo.
set /p stats_file="Podaj nazwę pliku .stats (bez ścieżki): "
if exist "..\__raports\%stats_file%" (
    echo 📊 Analizuję plik: %stats_file%
    python profile_analyzer.py --stats "..\__raports\%stats_file%"
) else (
    echo ❌ Plik %stats_file% nie istnieje
)
goto end

:end
echo.
echo ✅ Profilowanie zakończone!
echo 📁 Sprawdź wyniki w katalogu __raports
echo.
set /p again="Czy chcesz uruchomić kolejne profilowanie? (t/n): "
if /i "%again%"=="t" goto menu
if /i "%again%"=="y" goto menu

:exit
echo.
echo �� Do widzenia!
pause 