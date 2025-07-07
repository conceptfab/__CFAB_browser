@echo off
echo ====================================
echo CFAB Browser - Instalator PyInstaller
echo ====================================

REM Sprawdź czy folder _dist istnieje
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
echo Znaleziono aplikację w: %APP_FOLDER%

REM Test uruchomienia
echo.
echo Testowanie aplikacji przed instalacją...
call test_exe.bat

REM Utwórz skrót na pulpicie
echo.
echo Tworzenie skrótu na pulpicie...
powershell "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\CFAB Browser.lnk'); $Shortcut.TargetPath = '%~dp0%APP_FOLDER%\CFAB_Browser.exe'; $Shortcut.Save()"

echo.
echo ====================================
echo Instalacja zakończona!
echo ====================================
echo Aplikacja dostępna:
echo 1. Skrót na pulpicie: "CFAB Browser"
echo 2. Folder aplikacji: %APP_FOLDER%
echo 3. Test z konsolą: test_exe.bat
echo ====================================
pause
