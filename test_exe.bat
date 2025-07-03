@echo off
echo ====================================
echo CFAB Browser - Test uruchomienia
echo ====================================

REM Sprawdź czy istnieje folder _dist
if not exist "_dist" (
    echo Błąd: Nie znaleziono folderu _dist
    echo Uruchom najpierw build_pyinstaller.py
    pause
    exit /b 1
)

REM Znajdź folder z aplikacją
for /d %%d in (_dist\*) do (
    if exist "%%d\CFAB_Browser.exe" (
        set APP_FOLDER=%%d
        goto :found_app
    )
)

echo Błąd: Nie znaleziono CFAB_Browser.exe w folderze _dist
echo Uruchom najpierw build_pyinstaller.py
pause
exit /b 1

:found_app
echo.
echo Znaleziono aplikację w: %APP_FOLDER%
echo Uruchamianie CFAB_Browser.exe z konsolą...
echo (Zamknij aplikację aby zakończyć test)
echo.

"%APP_FOLDER%\CFAB_Browser.exe"

echo.
echo ====================================
echo Test zakończony
echo ====================================
pause 