@echo off
echo =============================================
echo  CHECKER KONFIGURACJI RUST + PyO3
echo  Sprawdzanie kompletności konfiguracji
echo =============================================
echo.

REM Sprawdź czy Python jest dostępny
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo BŁĄD: Python nie jest zainstalowany lub nie jest w PATH
    echo Zainstaluj Python z python.org
    pause
    exit /b 1
)

REM Uruchom checker
echo Uruchamianie checker-a...
echo.
python check_rust_setup.py

REM Sprawdź wynik
if %errorlevel% equ 0 (
    echo.
    echo =============================================
    echo  SUKCES: Konfiguracja jest kompletna!
    echo =============================================
) else (
    echo.
    echo =============================================
    echo  BŁĄD: Konfiguracja wymaga poprawek
    echo =============================================
)

echo.
pause 