#!/usr/bin/env python3
"""
Skrypt do kompilacji CFAB Browser z PyInstaller - ZOPTYMALIZOWANA WERSJA
"""

import argparse
import datetime
import json
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

from PIL import Image


def get_folder_size(folder_path):
    """Oblicza rozmiar folderu w bajtach"""
    total_size = 0
    if os.path.exists(folder_path):
        for dirpath, dirnames, filenames in os.walk(folder_path):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                if os.path.exists(file_path):
                    total_size += os.path.getsize(file_path)
    return total_size


def parse_arguments():
    """Parsuje argumenty wiersza poleceń"""
    parser = argparse.ArgumentParser(
        description="CFAB Browser - Kompilator PyInstaller"
    )
    parser.add_argument(
        "--debug", action="store_true", help="Tryb debug - z konsolą i logami"
    )
    parser.add_argument(
        "--release", action="store_true", help="Tryb release - bez konsoli (domyślny)"
    )
    parser.add_argument("--version", type=str, help="Wersja aplikacji (np. 1.2.3)")
    parser.add_argument(
        "--auto-test", action="store_true", help="Automatyczne testowanie po kompilacji"
    )
    parser.add_argument(
        "--create-zip", action="store_true", help="Tworzenie archiwum ZIP z buildem"
    )
    parser.add_argument(
        "--clean-only", action="store_true", help="Tylko wyczyść poprzednie buildy"
    )
    parser.add_argument(
        "--no-upx", action="store_true", help="Wyłącz kompresję UPX (rozwiąż problemy z kompresją)"
    )

    return parser.parse_args()


def get_version_info():
    """Pobiera informacje o wersji z config.json lub daty"""
    try:
        with open("config.json", "r", encoding="utf-8") as f:
            config = json.load(f)
            version = config.get("version", "1.0.0")
    except (FileNotFoundError, json.JSONDecodeError):
        # Jeśli nie ma config.json, użyj daty
        version = datetime.datetime.now().strftime("%Y.%m.%d")

    return version


def clean_build_dirs():
    """Czyści katalogi build i dist oraz pliki tymczasowe"""
    dirs_to_clean = ["build", "dist", "_dist", "__pycache__"]

    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"Usuwanie katalogu: {dir_name}")
            shutil.rmtree(dir_name)

    # Usuń pliki spec
    spec_files = ["cfab_browser.spec", "CFAB_Browser.spec"]
    for spec_file in spec_files:
        if os.path.exists(spec_file):
            print(f"Usuwanie pliku spec: {spec_file}")
            os.remove(spec_file)

    # Usuń stare pliki exe
    exe_files = ["CFAB_Browser.exe", "CFAB_Browser_*.exe"]
    for exe_pattern in exe_files:
        for exe_file in Path(".").glob(exe_pattern):
            print(f"Usuwanie pliku exe: {exe_file}")
            exe_file.unlink()

    # Usuń logi
    log_files = ["*.log", "build_*.txt"]
    for log_pattern in log_files:
        for log_file in Path(".").glob(log_pattern):
            print(f"Usuwanie loga: {log_file}")
            log_file.unlink()


def check_required_files():
    """Sprawdza obecność wszystkich wymaganych plików"""
    required_files = [
        "cfab_browser.py",
        "config.json",
        "core/resources/img/icon.png",
        "core/resources/styles.qss",
    ]

    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)

    if missing_files:
        print("❌ Brakujące wymagane pliki:")
        for file_path in missing_files:
            print(f"   • {file_path}")
        return False

    print("✅ Wszystkie wymagane pliki są obecne")
    return True


def check_pyinstaller():
    """Sprawdza czy PyInstaller jest zainstalowany"""
    try:
        result = subprocess.run(
            ["pyinstaller", "--version"], capture_output=True, text=True
        )
        if result.returncode == 0:
            print(f"✅ PyInstaller version: {result.stdout.strip()}")
            return True
        else:
            print("❌ PyInstaller nie jest zainstalowany")
            return False
    except FileNotFoundError:
        print("❌ PyInstaller nie jest zainstalowany")
        return False


def convert_png_to_ico(force_regenerate=False):
    """Konwertuje PNG na ICO dla Windows"""
    png_path = "core/resources/img/icon.png"
    ico_path = "core/resources/img/icon.ico"

    if os.path.exists(ico_path) and not force_regenerate:
        print(f"✅ Ikona ICO już istnieje: {ico_path}")
        return ico_path

    if not os.path.exists(png_path):
        print(f"❌ Nie znaleziono pliku ikony: {png_path}")
        return None

    try:
        # Otwórz obraz PNG
        img = Image.open(png_path)

        # Konwertuj na RGBA jeśli nie jest
        if img.mode != "RGBA":
            img = img.convert("RGBA")

        # Zapisz jako ICO z pełnym zestawem rozmiarów dla Windows
        img.save(
            ico_path,
            format="ICO",
            sizes=[
                (16, 16),  # Małe ikony
                (24, 24),  # Małe ikony (alternatywne)
                (32, 32),  # Średnie ikony
                (40, 40),  # Średnie ikony (alternatywne)
                (48, 48),  # Duże ikony
                (64, 64),  # Duże ikony (alternatywne)
                (96, 96),  # Bardzo duże ikony
                (128, 128),  # Ekstra duże ikony
                (256, 256),  # Maksymalne ikony
            ],
        )
        print(f"✅ Skonwertowano ikonę: {png_path} → {ico_path}")
        return ico_path
    except Exception as e:
        print(f"❌ Błąd konwersji ikony: {e}")
        return None


def check_upx():
    """Sprawdza czy UPX jest dostępny dla dodatkowej kompresji - POPRAWIONA WERSJA"""
    # Sprawdź czy UPX jest w PATH
    try:
        result = subprocess.run(["upx", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            version_line = result.stdout.split("\n")[0]
            version = (
                version_line.split()[1]
                if len(version_line.split()) > 1
                else "wersja nieznana"
            )
            print(f"✅ UPX dostępny w PATH: {version}")
            return True
    except FileNotFoundError:
        pass
    
    # Sprawdź czy UPX jest w katalogu projektu
    upx_paths = ["./upx.exe", "./upx", "upx.exe", "upx"]
    for upx_path in upx_paths:
        if os.path.exists(upx_path):
            print(f"✅ UPX znaleziony lokalnie: {upx_path}")
            return True
    
    print("ℹ️  UPX niedostępny - kompilacja bez dodatkowej kompresji")
    print("   💡 Aby włączyć UPX: pobierz upx.exe i umieść w katalogu projektu")
    return False


def install_pyinstaller():
    """Instaluje PyInstaller"""
    print("📦 Instalowanie PyInstaller...")
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "pyinstaller"],
            check=True,
            capture_output=False,
        )
        print("✅ PyInstaller zainstalowany pomyślnie!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Błąd podczas instalacji PyInstaller: {e}")
        return False


def auto_test_application(exe_path):
    """Automatycznie testuje skompilowaną aplikację"""
    print(f"🧪 Testowanie aplikacji: {exe_path}")

    if not os.path.exists(exe_path):
        print(f"❌ Plik {exe_path} nie istnieje")
        return False

    try:
        # Uruchom aplikację w tle na krótko
        process = subprocess.Popen(
            [exe_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )

        # Poczekaj 3 sekundy
        try:
            stdout, stderr = process.communicate(timeout=3)
            if process.returncode == 0:
                print("✅ Aplikacja uruchomiła się pomyślnie")
                return True
            else:
                print(f"⚠️  Aplikacja zakończyła się z kodem: {process.returncode}")
                if stderr:
                    print(f"Błędy: {stderr}")
                return False
        except subprocess.TimeoutExpired:
            # Zakończ proces
            process.terminate()
            print("✅ Aplikacja uruchomiła się (test timeout)")
            return True

    except Exception as e:
        print(f"❌ Błąd podczas testowania: {e}")
        return False


def create_zip_archive(exe_path, version):
    """Tworzy archiwum ZIP z buildem"""
    zip_name = f"CFAB_Browser_v{version}.zip"

    try:
        with zipfile.ZipFile(zip_name, "w", zipfile.ZIP_DEFLATED) as zipf:
            # Dodaj plik exe
            zipf.write(exe_path, os.path.basename(exe_path))

            # Dodaj folder core/resources
            if os.path.exists("core/resources"):
                for root, dirs, files in os.walk("core/resources"):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arc_name = os.path.relpath(file_path, ".")
                        zipf.write(file_path, arc_name)

            # Dodaj config.json
            if os.path.exists("config.json"):
                zipf.write("config.json", "config.json")

            # Dodaj README
            if os.path.exists("README_pyinstaller.txt"):
                zipf.write("README_pyinstaller.txt", "README.txt")

        print(f"✅ Utworzono archiwum: {zip_name}")
        return zip_name
    except Exception as e:
        print(f"❌ Błąd podczas tworzenia archiwum: {e}")
        return None


def copy_required_files(exe_name):
    """Kopiuje wymagane pliki do folderu _dist po kompilacji"""
    dist_folder = os.path.join("_dist", exe_name)

    if not os.path.exists(dist_folder):
        print(f"❌ Folder {dist_folder} nie istnieje")
        return False

    print(f"📁 Kopiowanie wymaganych plików do {dist_folder}...")

    # Kopiuj config.json
    if os.path.exists("config.json"):
        config_dest = os.path.join(dist_folder, "config.json")
        shutil.copy2("config.json", config_dest)
        print(f"✅ Skopiowano: config.json → {config_dest}")
    else:
        print("⚠️  config.json nie istnieje")

    # Kopiuj folder core/resources
    if os.path.exists("core/resources"):
        resources_dest = os.path.join(dist_folder, "core", "resources")
        if os.path.exists(resources_dest):
            shutil.rmtree(resources_dest)
        shutil.copytree("core/resources", resources_dest)
        print(f"✅ Skopiowano: core/resources → {resources_dest}")
    else:
        print("⚠️  core/resources nie istnieje")

    return True


def build_with_pyinstaller(debug_mode=False, version="1.0.0", upx_available=False):
    """Kompiluje aplikację z PyInstaller - ZOPTYMALIZOWANA WERSJA"""

    # Główny plik aplikacji
    main_file = "cfab_browser.py"

    # Konwertuj ikonę PNG na ICO dla Windows (wymuszenie regeneracji)
    icon_path = convert_png_to_ico(force_regenerate=True)
    if not icon_path:
        print("⚠️  Kompilacja bez ikony - używam domyślnej")
        icon_path = ""

    # Sprawdź dostępność UPX dla dodatkowej kompresji (już sprawdzone w main())
    # upx_available jest przekazywane z main()

    # Nazwa pliku exe z wersją
    exe_name = f"CFAB_Browser_v{version}" if version != "1.0.0" else "CFAB_Browser"

    # ⚡ OPTYMALIZACJE WYDAJNOŚCI I ROZMIARU
    pyinstaller_options = [
        "pyinstaller",
        "--onedir",  # Kompletny folder z aplikacją
        "--name=" + exe_name,  # Nazwa aplikacji
        # 🚀 OPTYMALIZACJE KOMPRESJI I WYDAJNOŚCI
        "--optimize=2",  # Maksymalna optymalizacja bytecode
        "--clean",  # Wyczyść cache przed budowaniem
        "--noconfirm",  # Nie pytaj o nadpisanie
    ]

    # Dodaj tryb debug lub release
    if debug_mode:
        print("🐛 Tryb DEBUG - z konsolą i logami")
        # W trybie debug nie używamy --windowed
    else:
        print("🚀 Tryb RELEASE - bez konsoli")
        pyinstaller_options.append("--windowed")  # Bez konsoli na Windows

    # Dodaj ikonę jeśli dostępna
    if icon_path:
        pyinstaller_options.append(f"--icon={icon_path}")

    # 🔧 STRIP TYLKO NA LINUX/MAC (na Windows powoduje błędy)
    if os.name != "nt":  # Nie Windows
        pyinstaller_options.append("--strip")

    # 💾 DODAJ UPX JEŚLI DOSTĘPNY (dodatkowa kompresja) - POPRAWIONA WERSJA
    if upx_available:
        # Sprawdź czy UPX jest w katalogu projektu
        upx_local_paths = ["./upx.exe", "./upx", "upx.exe", "upx"]
        upx_found = False
        for upx_path in upx_local_paths:
            if os.path.exists(upx_path):
                pyinstaller_options.append(f"--upx-dir={os.path.dirname(upx_path) or '.'}")
                upx_found = True
                break
        
        if not upx_found:
            # Jeśli UPX jest w PATH, użyj domyślnej ścieżki
            pyinstaller_options.append("--upx-dir=.")
        
        # Dodaj wykluczenia dla problematycznych plików
        pyinstaller_options.extend([
            "--upx-exclude=ucrtbase.dll",
            "--upx-exclude=VCRUNTIME140.dll",
            "--upx-exclude=VCRUNTIME140_1.dll",
            "--upx-exclude=Qt6*.dll",
            "--upx-exclude=MSVCP140.dll",
            "--upx-exclude=python3.dll",
            "--upx-exclude=libcrypto-3.dll",
            "--upx-exclude=libssl-3.dll",
            "--upx-exclude=libffi-8.dll",
            "--upx-exclude=*.pyd"  # Wyklucz wszystkie pliki .pyd
        ])

    pyinstaller_options.extend(
        [
            # 🎯 WYKLUCZENIA NIEPOTRZEBNYCH MODUŁÓW (redukcja rozmiaru)
            "--exclude-module=tkinter",  # Nie używamy tkinter
            "--exclude-module=matplotlib",  # Nie używamy matplotlib
            "--exclude-module=numpy",  # Jeśli nie używamy numpy
            "--exclude-module=pandas",  # Jeśli nie używamy pandas
            "--exclude-module=scipy",  # Jeśli nie używamy scipy
            "--exclude-module=IPython",  # Nie używamy IPython
            "--exclude-module=jupyter",  # Nie używamy jupyter
            "--exclude-module=notebook",  # Nie używamy notebook
            "--exclude-module=pydoc",  # Nie używamy pydoc
            "--exclude-module=doctest",  # Nie używamy doctest
            "--exclude-module=unittest",  # Nie używamy unittest w exe
            "--exclude-module=test",  # Nie używamy test modules
            # 🎯 WYKLUCZENIA PYQT6 - TYLKO POTRZEBNE MODUŁY
            # UWAGA: Jeśli używasz któregoś z tych modułów, usuń odpowiednią linię
            "--exclude-module=PyQt6.QtNetwork",  # Jeśli nie używamy sieci
            "--exclude-module=PyQt6.QtSql",  # Jeśli nie używamy SQL
            "--exclude-module=PyQt6.QtTest",  # Nie używamy testów Qt
            "--exclude-module=PyQt6.QtBluetooth",  # Nie używamy Bluetooth
            "--exclude-module=PyQt6.QtLocation",  # Nie używamy lokalizacji
            "--exclude-module=PyQt6.QtMultimedia",  # Jeśli nie używamy multimediów
            "--exclude-module=PyQt6.QtWebEngineWidgets",  # Jeśli nie używamy web
            # 📁 ŚCIEŻKI I ZASOBY
            "--add-data=core/resources;core/resources",  # Zasoby aplikacji
            "--add-data=config.json;.",  # Plik konfiguracyjny
            # 🔧 HIDDEN IMPORTS - TYLKO NIEZBĘDNE
            "--hidden-import=PyQt6.QtCore",
            "--hidden-import=PyQt6.QtGui",
            "--hidden-import=PyQt6.QtWidgets",
            # 🏗️ CORE MODULES - TYLKO UŻYWANE
            "--hidden-import=core.main_window",
            "--hidden-import=core.json_utils",
            "--hidden-import=core.amv_tab",
            "--hidden-import=core.pairing_tab",
            "--hidden-import=core.tools_tab",
            "--hidden-import=core.file_utils",
            "--hidden-import=core.scanner",
            # 📊 PODSTAWOWE IMPORTS
            "--hidden-import=logging",
            "--hidden-import=json",
            # 📤 OUTPUT DIRECTORY
            "--distpath=_dist",  # Folder z aplikacją w _dist/
            "--workpath=build",  # Pliki robocze w build/
            "--specpath=.",  # Plik spec w głównym katalogu
            # 🎯 TRYB PRODUKCYJNY (BEZ DEBUG!)
            # USUNIĘTO: "--debug=all" - drastycznie zmniejsza rozmiar i zwiększa wydajność!
            # 📄 GŁÓWNY PLIK
            main_file,
        ]
    )

    print("🚀 Rozpoczynam ZOPTYMALIZOWANĄ kompilację z PyInstaller...")
    print(f"🎯 Tryb: {'DEBUG' if debug_mode else 'RELEASE'}")
    print("⚡ Optymalizacje: kompresja, excludes, brak debug")
    if os.name == "nt":
        print("🪟 Windows: STRIP WYŁĄCZONY (nie jest dostępny)")
    else:
        print("🐧 Unix/Linux: STRIP WŁĄCZONY")
    if upx_available:
        print("💾 UPX compression: WŁĄCZONY")
    else:
        print("💾 UPX compression: NIEDOSTĘPNY")

    # Pokazuj tylko pierwsze 10 opcji w komunikacie
    cmd_preview = " ".join(pyinstaller_options[:10])
    remaining = len(pyinstaller_options) - 10
    print(f"🔧 Komenda: {cmd_preview}... (+{remaining} więcej opcji)")

    try:
        subprocess.run(pyinstaller_options, check=True, capture_output=False)
        print("✅ Kompilacja zakończona pomyślnie!")
        print("🎯 Zastosowane optymalizacje:")
        print("   • Usunięto --debug=all (mniejszy rozmiar)")
        print("   • Dodano --optimize=2 (szybszy kod)")
        if os.name != "nt":
            print("   • Dodano --strip (mniejszy rozmiar)")
        else:
            print("   • Strip pominięty (Windows)")
        print("   • Wykluczono niepotrzebne moduły")
        print("   • Zoptymalizowano PyQt6 imports")
        if upx_available:
            print("   • UPX compression (dodatkowa kompresja)")
        else:
            print("   • UPX compression niedostępny")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Błąd podczas kompilacji: {e}")
        return False


def create_installer_script():
    """Tworzy skrypt instalacyjny"""
    installer_content = """@echo off
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
for /d %%d in (_dist\\*) do (
    if exist "%%d\\CFAB_Browser.exe" (
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
powershell "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\\Desktop\\CFAB Browser.lnk'); $Shortcut.TargetPath = '%~dp0%APP_FOLDER%\\CFAB_Browser.exe'; $Shortcut.Save()"

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
"""

    with open("install_pyinstaller.bat", "w", encoding="utf-8") as f:
        f.write(installer_content)

    print("✅ Utworzono skrypt instalacyjny: install_pyinstaller.bat")


def create_readme():
    """Tworzy README dla skompilowanej aplikacji"""
    readme_content = """# CFAB Browser - PyInstaller Build

## Instalacja

1. Uruchom `install_pyinstaller.bat` aby utworzyć skrót na pulpicie
2. Lub przejdź do folderu `_dist/CFAB_Browser/` i uruchom `CFAB_Browser.exe`

## Testowanie

- **Test z konsolą**: Uruchom `test_exe.bat` - pokaże błędy jeśli występują
- **Normalny test**: Przejdź do folderu `_dist/CFAB_Browser/` i kliknij dwukrotnie `CFAB_Browser.exe`

## Wymagania systemowe

- Windows 10/11 (64-bit)
- 4 GB RAM
- 200 MB wolnego miejsca na dysku

## Informacje o buildzie

- **Kompilator**: PyInstaller (alternatywa dla Nuitka)
- **Tryb**: --onedir (kompletny folder z aplikacją)
- **GUI**: --windowed (bez konsoli) lub --console (z konsolą w debug)
- **Lokalizacja**: Folder `_dist/CFAB_Browser/`

## Zalety PyInstaller vs Nuitka

✅ Stabilniejszy z PyQt6
✅ Mniej problemów z reference counting
✅ Szybsza kompilacja
✅ Lepsze wsparcie dla bibliotek GUI

## Rozwiązywanie problemów

### Aplikacja się nie uruchamia
1. Uruchom `test_exe.bat` aby zobaczyć błędy
2. Sprawdź czy folder `_dist/CFAB_Browser/` istnieje
3. Uruchom jako administrator

### Brakuje plików zasobów
1. Sprawdź czy folder `_dist/CFAB_Browser/` zawiera wszystkie pliki
2. W razie potrzeby przekopiuj ręcznie

### Tryb debug
Jeśli aplikacja nie działa, spróbuj skompilować w trybie debug:
```
python build_pyinstaller.py --debug
```

## Wsparcie

W przypadku problemów:
1. Uruchom `test_exe.bat` dla szczegółów błędów
2. Sprawdź logi aplikacji
3. Porównaj z oryginalną wersją Python
"""

    with open("README_pyinstaller.txt", "w", encoding="utf-8") as f:
        f.write(readme_content)

    print("✅ Utworzono README: README_pyinstaller.txt")


def main():
    """Główna funkcja - ZOPTYMALIZOWANA WERSJA"""
    args = parse_arguments()

    print("🔨 CFAB Browser - Kompilator PyInstaller OPTIMIZED")
    print("=" * 60)
    print("⚡ OPTYMALIZACJE: wydajność, stabilność, redukcja rozmiaru")
    print("=" * 60)

    # ZAWSZE czyść buildy i pliki po poprzednich kompilacjach
    print("🧹 Automatyczne czyszczenie poprzednich buildów...")
    clean_build_dirs()

    # Sprawdź czy główny plik istnieje
    if not os.path.exists("cfab_browser.py"):
        print("❌ Nie znaleziono cfab_browser.py")
        return False

    # Sprawdź wymagane pliki
    if not check_required_files():
        return False

    # Sprawdź czy PIL jest zainstalowany (potrzebny do konwersji ikon)
    try:
        from PIL import Image

        print("✅ PIL/Pillow dostępny - konwersja ikon włączona")
    except ImportError:
        print("📦 Instalowanie Pillow (PIL) dla konwersji ikon...")
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "pillow"],
                check=True,
                capture_output=False,
            )
            print("✅ Pillow zainstalowany pomyślnie!")
        except subprocess.CalledProcessError:
            print("⚠️  Nie udało się zainstalować Pillow - ikona może nie działać")

    # Sprawdź/zainstaluj PyInstaller
    if not check_pyinstaller():
        print("🔄 Próba instalacji PyInstaller...")
        if not install_pyinstaller():
            return False

    # Sprawdź UPX dla dodatkowej kompresji
    print("🔍 Sprawdzanie dostępności UPX...")
    upx_available = check_upx()
    
    # Sprawdź czy użytkownik wyłączył UPX
    if args.no_upx:
        print("🚫 UPX wyłączony przez użytkownika (--no-upx)")
        upx_available = False

    # Pobierz wersję
    version = args.version if args.version else get_version_info()
    print(f"📋 Wersja aplikacji: {version}")

    # Nazwa pliku exe z wersją
    exe_name = f"CFAB_Browser_v{version}" if version != "1.0.0" else "CFAB_Browser"

    # Określ tryb kompilacji
    debug_mode = args.debug
    if not args.debug and not args.release:
        # Domyślnie tryb release
        debug_mode = False

    # Kompiluj
    if build_with_pyinstaller(debug_mode=debug_mode, version=version, upx_available=upx_available):
        # Znajdź utworzony plik exe w folderze _dist
        exe_pattern = (
            f"CFAB_Browser_v{version}.exe" if version != "1.0.0" else "CFAB_Browser.exe"
        )
        dist_exe_path = os.path.join("_dist", exe_name, exe_pattern)
        if os.path.exists(dist_exe_path):
            actual_exe = dist_exe_path
        elif os.path.exists(os.path.join("_dist", exe_name, "CFAB_Browser.exe")):
            actual_exe = os.path.join("_dist", exe_name, "CFAB_Browser.exe")
        else:
            print(
                "\n❌ Nie znaleziono pliku wykonywalnego po kompilacji w folderze _dist"
            )
            return False

        print("\n🎉 ZOPTYMALIZOWANA KOMPILACJA ZAKOŃCZONA!")
        print("=" * 60)
        print(f"📁 Folder aplikacji: _dist/{exe_name}/")
        print(f"📁 Plik wykonywalny: {actual_exe}")
        print(
            f"📊 Rozmiar folderu: {get_folder_size('_dist/' + exe_name) / (1024*1024):.1f} MB"
        )
        print("⚡ ZASTOSOWANE OPTYMALIZACJE:")
        print("   ✅ Usunięto --debug (50-70% mniejszy rozmiar)")
        print("   ✅ Dodano --optimize=2 (szybszy kod)")
        if os.name != "nt":
            print("   ✅ Dodano --strip (mniejszy rozmiar)")
        else:
            print("   ✅ Strip pominięty (Windows)")
        print("   ✅ Wykluczono niepotrzebne moduły")
        print("   ✅ Zoptymalizowano PyQt6 imports")
        if os.path.exists("core/resources/img/icon.ico"):
            print("   ✅ Dodano ikonę aplikacji")
        else:
            print("   ⚠️  Ikona aplikacji niedostępna")
        if check_upx():
            print("   ✅ UPX compression (dodatkowa kompresja)")
        print("=" * 60)

        # Automatyczne testowanie
        if args.auto_test:
            print("\n🧪 Automatyczne testowanie aplikacji...")
            if auto_test_application(actual_exe):
                print("✅ Test zakończony pomyślnie!")
            else:
                print("⚠️  Test wykrył problemy - sprawdź aplikację ręcznie")

        # Tworzenie archiwum ZIP
        if args.create_zip:
            print("\n📦 Tworzenie archiwum ZIP...")
            zip_file = create_zip_archive(actual_exe, version)
            if zip_file:
                print(f"✅ Archiwum utworzone: {zip_file}")

        # Utwórz dodatkowe pliki
        create_installer_script()
        create_readme()

        print("📋 Pliki pomocnicze:")
        print("   • install_pyinstaller.bat - Instalator")
        print("   • README_pyinstaller.txt - Dokumentacja")
        print("   • test_exe.bat - Skrypt testowy")

        # Test uruchomienia
        print("\n🧪 Aby przetestować aplikację:")
        print("   1. Uruchom: test_exe.bat (pokazuje błędy w konsoli)")
        print(f"   2. Lub kliknij dwukrotnie: {actual_exe}")
        print(f"   3. Lub przejdź do folderu: _dist/{exe_name}/")
        print("   4. Jeśli działa - uruchom: install_pyinstaller.bat")

        # Kopiuj wymagane pliki
        if copy_required_files(exe_name):
            print("\n📁 Wymagane pliki skopiowane do folderu _dist")
        else:
            print("\n❌ Nie udało się skopiować wymaganych plików")

        return True
    else:
        print("\n❌ Kompilacja nie powiodła się")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)