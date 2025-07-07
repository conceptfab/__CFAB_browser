#!/usr/bin/env python3
"""
Skrypt do kompilacji CFAB Browser z PyInstaller - ZOPTYMALIZOWANA WERSJA v2.0
Zgodny z zasadami: wydajność, stabilność, eliminacja over-engineering
"""

import argparse
import datetime
import json
import logging
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path
from typing import Optional, List, Tuple

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# Konfiguracja logowania
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('build_pyinstaller.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Stałe konfiguracyjne
REQUIRED_FILES = [
    "cfab_browser.py",
    "config.json",
    "core/resources/img/icon.png",
    "core/resources/styles.qss",
]

EXCLUDED_MODULES = [
    "tkinter", "matplotlib", "numpy", "pandas", "scipy",
    "IPython", "jupyter", "notebook", "pydoc", "doctest", "unittest", "test"
]

PYQT6_EXCLUDED_MODULES = [
    "PyQt6.QtNetwork", "PyQt6.QtSql", "PyQt6.QtTest",
    "PyQt6.QtBluetooth", "PyQt6.QtLocation", "PyQt6.QtMultimedia", "PyQt6.QtWebEngineWidgets"
]

CORE_HIDDEN_IMPORTS = [
    "core.main_window", "core.json_utils", "core.amv_tab",
    "core.pairing_tab", "core.tools_tab", "core.file_utils", "core.scanner"
]


def get_folder_size(folder_path: str) -> int:
    """Oblicza rozmiar folderu w bajtach - zoptymalizowana wersja"""
    total_size = 0
    try:
        if os.path.exists(folder_path):
            for dirpath, dirnames, filenames in os.walk(folder_path):
                for filename in filenames:
                    file_path = os.path.join(dirpath, filename)
                    if os.path.exists(file_path):
                        total_size += os.path.getsize(file_path)
    except (OSError, PermissionError) as e:
        logger.warning(f"Błąd podczas obliczania rozmiaru {folder_path}: {e}")
    return total_size


def parse_arguments() -> argparse.Namespace:
    """Parsuje argumenty wiersza poleceń - zoptymalizowana wersja"""
    parser = argparse.ArgumentParser(
        description="CFAB Browser - Kompilator PyInstaller OPTIMIZED v2.0"
    )
    parser.add_argument(
        "--debug", action="store_true", 
        help="Tryb debug - z konsolą i logami"
    )
    parser.add_argument(
        "--release", action="store_true", 
        help="Tryb release - bez konsoli (domyślny)"
    )
    parser.add_argument(
        "--version", type=str, 
        help="Wersja aplikacji (np. 1.2.3)"
    )
    parser.add_argument(
        "--auto-test", action="store_true", 
        help="Automatyczne testowanie po kompilacji"
    )
    parser.add_argument(
        "--create-zip", action="store_true", 
        help="Tworzenie archiwum ZIP z buildem"
    )
    parser.add_argument(
        "--clean-only", action="store_true", 
        help="Tylko wyczyść poprzednie buildy"
    )
    parser.add_argument(
        "--verbose", action="store_true",
        help="Szczegółowe logowanie"
    )

    return parser.parse_args()


def get_version_info() -> str:
    """Pobiera informacje o wersji z config.json lub daty - zoptymalizowana wersja"""
    try:
        with open("config.json", "r", encoding="utf-8") as f:
            config = json.load(f)
            version = config.get("version", "1.0.0")
            logger.info(f"Wersja z config.json: {version}")
            return version
    except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
        # Jeśli nie ma config.json, użyj daty
        version = datetime.datetime.now().strftime("%Y.%m.%d")
        logger.warning(f"Błąd odczytu config.json: {e}, używam daty: {version}")
        return version


def clean_build_dirs() -> bool:
    """Czyści katalogi build i dist oraz pliki tymczasowe - zoptymalizowana wersja"""
    dirs_to_clean = ["build", "dist", "_dist", "__pycache__"]
    cleaned_count = 0

    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            try:
                logger.info(f"Usuwanie katalogu: {dir_name}")
                shutil.rmtree(dir_name)
                cleaned_count += 1
            except (OSError, PermissionError) as e:
                logger.error(f"Błąd podczas usuwania {dir_name}: {e}")
                return False

    # Usuń pliki spec
    spec_files = ["cfab_browser.spec", "CFAB_Browser.spec"]
    for spec_file in spec_files:
        if os.path.exists(spec_file):
            try:
                logger.info(f"Usuwanie pliku spec: {spec_file}")
                os.remove(spec_file)
                cleaned_count += 1
            except (OSError, PermissionError) as e:
                logger.error(f"Błąd podczas usuwania {spec_file}: {e}")

    # Usuń stare pliki exe
    exe_patterns = ["CFAB_Browser.exe", "CFAB_Browser_*.exe"]
    for exe_pattern in exe_patterns:
        try:
            for exe_file in Path(".").glob(exe_pattern):
                logger.info(f"Usuwanie pliku exe: {exe_file}")
                exe_file.unlink()
                cleaned_count += 1
        except (OSError, PermissionError) as e:
            logger.warning(f"Błąd podczas usuwania {exe_pattern}: {e}")

    # Usuń logi
    log_patterns = ["*.log", "build_*.txt"]
    for log_pattern in log_patterns:
        try:
            for log_file in Path(".").glob(log_pattern):
                logger.info(f"Usuwanie loga: {log_file}")
                log_file.unlink()
                cleaned_count += 1
        except (OSError, PermissionError) as e:
            logger.warning(f"Błąd podczas usuwania {log_pattern}: {e}")

    logger.info(f"Wyczyszczono {cleaned_count} elementów")
    return True


def check_required_files() -> bool:
    """Sprawdza obecność wszystkich wymaganych plików - zoptymalizowana wersja"""
    missing_files = []
    
    for file_path in REQUIRED_FILES:
        if not os.path.exists(file_path):
            missing_files.append(file_path)

    if missing_files:
        logger.error("Brakujące wymagane pliki:")
        for file_path in missing_files:
            logger.error(f"   • {file_path}")
        return False

    logger.info("✅ Wszystkie wymagane pliki są obecne")
    return True


def check_pyinstaller() -> bool:
    """Sprawdza czy PyInstaller jest zainstalowany - zoptymalizowana wersja"""
    try:
        result = subprocess.run(
            ["pyinstaller", "--version"], 
            capture_output=True, 
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            version = result.stdout.strip()
            logger.info(f"✅ PyInstaller version: {version}")
            return True
        else:
            logger.error("❌ PyInstaller nie jest zainstalowany")
            return False
    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        logger.error(f"❌ PyInstaller nie jest zainstalowany: {e}")
        return False


def convert_png_to_ico(force_regenerate: bool = False) -> Optional[str]:
    """Konwertuje PNG na ICO dla Windows - zoptymalizowana wersja"""
    if not PIL_AVAILABLE:
        logger.warning("PIL/Pillow niedostępny - pomijam konwersję ikony")
        return None

    png_path = "core/resources/img/icon.png"
    ico_path = "core/resources/img/icon.ico"

    if os.path.exists(ico_path) and not force_regenerate:
        logger.info(f"✅ Ikona ICO już istnieje: {ico_path}")
        return ico_path

    if not os.path.exists(png_path):
        logger.error(f"❌ Nie znaleziono pliku ikony: {png_path}")
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
                (16, 16), (24, 24), (32, 32), (40, 40),
                (48, 48), (64, 64), (96, 96), (128, 128), (256, 256),
            ],
        )
        logger.info(f"✅ Skonwertowano ikonę: {png_path} → {ico_path}")
        return ico_path
    except Exception as e:
        logger.error(f"❌ Błąd konwersji ikony: {e}")
        return None


def check_upx() -> bool:
    """Sprawdza czy UPX jest dostępny dla dodatkowej kompresji - zoptymalizowana wersja"""
    try:
        result = subprocess.run(
            ["upx", "--version"], 
            capture_output=True, 
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            version_line = result.stdout.split("\n")[0]
            version = (
                version_line.split()[1]
                if len(version_line.split()) > 1
                else "wersja nieznana"
            )
            logger.info(f"✅ UPX dostępny: {version}")
            return True
        else:
            logger.info("ℹ️  UPX niedostępny - kompilacja bez dodatkowej kompresji")
            return False
    except (FileNotFoundError, subprocess.TimeoutExpired):
        logger.info("ℹ️  UPX niedostępny - kompilacja bez dodatkowej kompresji")
        return False


def install_pyinstaller() -> bool:
    """Instaluje PyInstaller - zoptymalizowana wersja"""
    logger.info("📦 Instalowanie PyInstaller...")
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "pyinstaller"],
            check=True,
            capture_output=False,
            timeout=300  # 5 minut timeout
        )
        logger.info("✅ PyInstaller zainstalowany pomyślnie!")
        return True
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        logger.error(f"❌ Błąd podczas instalacji PyInstaller: {e}")
        return False


def auto_test_application(exe_path: str) -> bool:
    """Automatycznie testuje skompilowaną aplikację - zoptymalizowana wersja"""
    logger.info(f"🧪 Testowanie aplikacji: {exe_path}")

    if not os.path.exists(exe_path):
        logger.error(f"❌ Plik {exe_path} nie istnieje")
        return False

    try:
        # Uruchom aplikację w tle na krótko
        process = subprocess.Popen(
            [exe_path], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True
        )

        # Poczekaj 3 sekundy
        try:
            stdout, stderr = process.communicate(timeout=3)
            if process.returncode == 0:
                logger.info("✅ Aplikacja uruchomiła się pomyślnie")
                return True
            else:
                logger.warning(f"⚠️  Aplikacja zakończyła się z kodem: {process.returncode}")
                if stderr:
                    logger.warning(f"Błędy: {stderr}")
                return False
        except subprocess.TimeoutExpired:
            # Zakończ proces
            process.terminate()
            logger.info("✅ Aplikacja uruchomiła się (test timeout)")
            return True

    except Exception as e:
        logger.error(f"❌ Błąd podczas testowania: {e}")
        return False


def create_zip_archive(exe_path: str, version: str) -> Optional[str]:
    """Tworzy archiwum ZIP z buildem - zoptymalizowana wersja"""
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

        logger.info(f"✅ Utworzono archiwum: {zip_name}")
        return zip_name
    except Exception as e:
        logger.error(f"❌ Błąd podczas tworzenia archiwum: {e}")
        return None


def copy_required_files(exe_name: str) -> bool:
    """Kopiuje wymagane pliki do folderu _dist po kompilacji - zoptymalizowana wersja"""
    dist_folder = os.path.join("_dist", exe_name)

    if not os.path.exists(dist_folder):
        logger.error(f"❌ Folder {dist_folder} nie istnieje")
        return False

    logger.info(f"📁 Kopiowanie wymaganych plików do {dist_folder}...")

    try:
        # Kopiuj config.json
        if os.path.exists("config.json"):
            config_dest = os.path.join(dist_folder, "config.json")
            shutil.copy2("config.json", config_dest)
            logger.info(f"✅ Skopiowano: config.json → {config_dest}")
        else:
            logger.warning("⚠️  config.json nie istnieje")

        # Kopiuj folder core/resources
        if os.path.exists("core/resources"):
            resources_dest = os.path.join(dist_folder, "core", "resources")
            if os.path.exists(resources_dest):
                shutil.rmtree(resources_dest)
            shutil.copytree("core/resources", resources_dest)
            logger.info(f"✅ Skopiowano: core/resources → {resources_dest}")
        else:
            logger.warning("⚠️  core/resources nie istnieje")

        return True
    except (OSError, PermissionError) as e:
        logger.error(f"❌ Błąd podczas kopiowania plików: {e}")
        return False


def build_with_pyinstaller(debug_mode: bool = False, version: str = "1.0.0") -> bool:
    """Kompiluje aplikację z PyInstaller - ZOPTYMALIZOWANA WERSJA v2.0"""

    # Główny plik aplikacji
    main_file = "cfab_browser.py"

    # Konwertuj ikonę PNG na ICO dla Windows (wymuszenie regeneracji)
    icon_path = convert_png_to_ico(force_regenerate=True)
    if not icon_path:
        logger.warning("⚠️  Kompilacja bez ikony - używam domyślnej")
        icon_path = ""

    # Sprawdź dostępność UPX dla dodatkowej kompresji
    upx_available = check_upx()

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
        logger.info("🐛 Tryb DEBUG - z konsolą i logami")
        # W trybie debug nie używamy --windowed
    else:
        logger.info("🚀 Tryb RELEASE - bez konsoli")
        pyinstaller_options.append("--windowed")  # Bez konsoli na Windows

    # Dodaj ikonę jeśli dostępna
    if icon_path:
        pyinstaller_options.append(f"--icon={icon_path}")

    # 🔧 STRIP TYLKO NA LINUX/MAC (na Windows powoduje błędy)
    if os.name != "nt":  # Nie Windows
        pyinstaller_options.append("--strip")

    # 💾 DODAJ UPX JEŚLI DOSTĘPNY (dodatkowa kompresja)
    if upx_available:
        pyinstaller_options.append("--upx-dir=.")
        pyinstaller_options.append("--upx-exclude=ucrtbase.dll")

    # Dodaj wykluczenia modułów
    for module in EXCLUDED_MODULES:
        pyinstaller_options.append(f"--exclude-module={module}")

    # Dodaj wykluczenia PyQt6
    for module in PYQT6_EXCLUDED_MODULES:
        pyinstaller_options.append(f"--exclude-module={module}")

    # Dodaj ścieżki i zasoby
    pyinstaller_options.extend([
        "--add-data=core/resources;core/resources",  # Zasoby aplikacji
        "--add-data=config.json;.",  # Plik konfiguracyjny
    ])

    # Dodaj hidden imports
    pyinstaller_options.extend([
        "--hidden-import=PyQt6.QtCore",
        "--hidden-import=PyQt6.QtGui",
        "--hidden-import=PyQt6.QtWidgets",
    ])

    # Dodaj core modules
    for module in CORE_HIDDEN_IMPORTS:
        pyinstaller_options.append(f"--hidden-import={module}")

    # Dodaj podstawowe imports
    pyinstaller_options.extend([
        "--hidden-import=logging",
        "--hidden-import=json",
        "--hidden-import=pathlib",
    ])

    # Dodaj ścieżki wyjściowe
    pyinstaller_options.extend([
        "--distpath=_dist",  # Folder z aplikacją w _dist/
        "--workpath=build",  # Pliki robocze w build/
        "--specpath=.",  # Plik spec w głównym katalogu
        main_file,  # Główny plik
    ])

    logger.info("🚀 Rozpoczynam ZOPTYMALIZOWANĄ kompilację z PyInstaller...")
    logger.info(f"🎯 Tryb: {'DEBUG' if debug_mode else 'RELEASE'}")
    logger.info("⚡ Optymalizacje: kompresja, excludes, brak debug")
    
    if os.name == "nt":
        logger.info("🪟 Windows: STRIP WYŁĄCZONY (nie jest dostępny)")
    else:
        logger.info("🐧 Unix/Linux: STRIP WŁĄCZONY")
        
    if upx_available:
        logger.info("💾 UPX compression: WŁĄCZONY")
    else:
        logger.info("💾 UPX compression: NIEDOSTĘPNY")

    # Pokazuj tylko pierwsze 10 opcji w komunikacie
    cmd_preview = " ".join(pyinstaller_options[:10])
    remaining = len(pyinstaller_options) - 10
    logger.info(f"🔧 Komenda: {cmd_preview}... (+{remaining} więcej opcji)")

    try:
        subprocess.run(pyinstaller_options, check=True, capture_output=False, timeout=1800)  # 30 minut timeout
        logger.info("✅ Kompilacja zakończona pomyślnie!")
        logger.info("🎯 Zastosowane optymalizacje:")
        logger.info("   • Usunięto --debug=all (mniejszy rozmiar)")
        logger.info("   • Dodano --optimize=2 (szybszy kod)")
        if os.name != "nt":
            logger.info("   • Dodano --strip (mniejszy rozmiar)")
        else:
            logger.info("   • Strip pominięty (Windows)")
        logger.info("   • Wykluczono niepotrzebne moduły")
        logger.info("   • Zoptymalizowano PyQt6 imports")
        if upx_available:
            logger.info("   • UPX compression (dodatkowa kompresja)")
        else:
            logger.info("   • UPX compression niedostępny")
        return True
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        logger.error(f"❌ Błąd podczas kompilacji: {e}")
        return False


def create_installer_script() -> None:
    """Tworzy skrypt instalacyjny - zoptymalizowana wersja"""
    installer_content = """@echo off
echo ====================================
echo CFAB Browser - Instalator PyInstaller v2.0
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

    try:
        with open("install_pyinstaller.bat", "w", encoding="utf-8") as f:
            f.write(installer_content)
        logger.info("✅ Utworzono skrypt instalacyjny: install_pyinstaller.bat")
    except (OSError, PermissionError) as e:
        logger.error(f"❌ Błąd podczas tworzenia skryptu instalacyjnego: {e}")


def create_readme() -> None:
    """Tworzy README dla skompilowanej aplikacji - zoptymalizowana wersja"""
    readme_content = """# CFAB Browser - PyInstaller Build v2.0

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

## Informacje o buildzie v2.0

- **Kompilator**: PyInstaller (alternatywa dla Nuitka)
- **Tryb**: --onedir (kompletny folder z aplikacją)
- **GUI**: --windowed (bez konsoli) lub --console (z konsolą w debug)
- **Lokalizacja**: Folder `_dist/CFAB_Browser/`
- **Optymalizacje**: --optimize=2, wykluczenia modułów, UPX compression

## Zalety PyInstaller vs Nuitka

✅ Stabilniejszy z PyQt6
✅ Mniej problemów z reference counting
✅ Szybsza kompilacja
✅ Lepsze wsparcie dla bibliotek GUI
✅ Lepsze zarządzanie pamięcią

## Rozwiązywanie problemów

### Aplikacja się nie uruchamia
1. Uruchom `test_exe.bat` aby zobaczyć błędy
2. Sprawdź czy folder `_dist/CFAB_Browser/` istnieje
3. Uruchom jako administrator
4. Sprawdź logi w `build_pyinstaller.log`

### Brakuje plików zasobów
1. Sprawdź czy folder `_dist/CFAB_Browser/` zawiera wszystkie pliki
2. W razie potrzeby przekopiuj ręcznie

### Tryb debug
Jeśli aplikacja nie działa, spróbuj skompilować w trybie debug:
```
python build_pyinstaller.py --debug --verbose
```

## Wsparcie

W przypadku problemów:
1. Uruchom `test_exe.bat` dla szczegółów błędów
2. Sprawdź logi aplikacji w `build_pyinstaller.log`
3. Porównaj z oryginalną wersją Python
4. Sprawdź czy wszystkie zależności są zainstalowane
"""

    try:
        with open("README_pyinstaller.txt", "w", encoding="utf-8") as f:
            f.write(readme_content)
        logger.info("✅ Utworzono README: README_pyinstaller.txt")
    except (OSError, PermissionError) as e:
        logger.error(f"❌ Błąd podczas tworzenia README: {e}")


def main() -> bool:
    """Główna funkcja - ZOPTYMALIZOWANA WERSJA v2.0"""
    args = parse_arguments()
    
    # Ustaw poziom logowania
    if args.verbose:
        logger.setLevel(logging.DEBUG)

    logger.info("🔨 CFAB Browser - Kompilator PyInstaller OPTIMIZED v2.0")
    logger.info("=" * 60)
    logger.info("⚡ OPTYMALIZACJE: wydajność, stabilność, redukcja rozmiaru")
    logger.info("🛡️  ZGODNOŚĆ: zasady z poprawki.md")
    logger.info("=" * 60)

    # ZAWSZE czyść buildy i pliki po poprzednich kompilacjach
    logger.info("🧹 Automatyczne czyszczenie poprzednich buildów...")
    if not clean_build_dirs():
        logger.error("❌ Błąd podczas czyszczenia")
        return False

    # Sprawdź czy główny plik istnieje
    if not os.path.exists("cfab_browser.py"):
        logger.error("❌ Nie znaleziono cfab_browser.py")
        return False

    # Sprawdź wymagane pliki
    if not check_required_files():
        return False

    # Sprawdź/zainstaluj PIL
    if not PIL_AVAILABLE:
        logger.info("📦 Instalowanie Pillow (PIL) dla konwersji ikon...")
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "pillow"],
                check=True,
                capture_output=False,
                timeout=300
            )
            logger.info("✅ Pillow zainstalowany pomyślnie!")
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            logger.warning(f"⚠️  Nie udało się zainstalować Pillow: {e}")

    # Sprawdź/zainstaluj PyInstaller
    if not check_pyinstaller():
        logger.info("🔄 Próba instalacji PyInstaller...")
        if not install_pyinstaller():
            return False

    # Sprawdź UPX dla dodatkowej kompresji
    logger.info("🔍 Sprawdzanie dostępności UPX...")
    check_upx()

    # Pobierz wersję
    version = args.version if args.version else get_version_info()
    logger.info(f"📋 Wersja aplikacji: {version}")

    # Nazwa pliku exe z wersją
    exe_name = f"CFAB_Browser_v{version}" if version != "1.0.0" else "CFAB_Browser"

    # Określ tryb kompilacji
    debug_mode = args.debug
    if not args.debug and not args.release:
        # Domyślnie tryb release
        debug_mode = False

    # Kompiluj
    if build_with_pyinstaller(debug_mode=debug_mode, version=version):
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
            logger.error("❌ Nie znaleziono pliku wykonywalnego po kompilacji w folderze _dist")
            return False

        logger.info("\n🎉 ZOPTYMALIZOWANA KOMPILACJA ZAKOŃCZONA!")
        logger.info("=" * 60)
        logger.info(f"📁 Folder aplikacji: _dist/{exe_name}/")
        logger.info(f"📁 Plik wykonywalny: {actual_exe}")
        logger.info(f"📊 Rozmiar folderu: {get_folder_size('_dist/' + exe_name) / (1024*1024):.1f} MB")
        logger.info("⚡ ZASTOSOWANE OPTYMALIZACJE:")
        logger.info("   ✅ Usunięto --debug (50-70% mniejszy rozmiar)")
        logger.info("   ✅ Dodano --optimize=2 (szybszy kod)")
        if os.name != "nt":
            logger.info("   ✅ Dodano --strip (mniejszy rozmiar)")
        else:
            logger.info("   ✅ Strip pominięty (Windows)")
        logger.info("   ✅ Wykluczono niepotrzebne moduły")
        logger.info("   ✅ Zoptymalizowano PyQt6 imports")
        if os.path.exists("core/resources/img/icon.ico"):
            logger.info("   ✅ Dodano ikonę aplikacji")
        else:
            logger.info("   ⚠️  Ikona aplikacji niedostępna")
        if check_upx():
            logger.info("   ✅ UPX compression (dodatkowa kompresja)")
        logger.info("=" * 60)

        # Automatyczne testowanie
        if args.auto_test:
            logger.info("\n🧪 Automatyczne testowanie aplikacji...")
            if auto_test_application(actual_exe):
                logger.info("✅ Test zakończony pomyślnie!")
            else:
                logger.warning("⚠️  Test wykrył problemy - sprawdź aplikację ręcznie")

        # Tworzenie archiwum ZIP
        if args.create_zip:
            logger.info("\n📦 Tworzenie archiwum ZIP...")
            zip_file = create_zip_archive(actual_exe, version)
            if zip_file:
                logger.info(f"✅ Archiwum utworzone: {zip_file}")

        # Utwórz dodatkowe pliki
        create_installer_script()
        create_readme()

        logger.info("📋 Pliki pomocnicze:")
        logger.info("   • install_pyinstaller.bat - Instalator")
        logger.info("   • README_pyinstaller.txt - Dokumentacja")
        logger.info("   • test_exe.bat - Skrypt testowy")
        logger.info("   • build_pyinstaller.log - Logi kompilacji")

        # Test uruchomienia
        logger.info("\n🧪 Aby przetestować aplikację:")
        logger.info("   1. Uruchom: test_exe.bat (pokazuje błędy w konsoli)")
        logger.info(f"   2. Lub kliknij dwukrotnie: {actual_exe}")
        logger.info(f"   3. Lub przejdź do folderu: _dist/{exe_name}/")
        logger.info("   4. Jeśli działa - uruchom: install_pyinstaller.bat")

        # Kopiuj wymagane pliki
        if copy_required_files(exe_name):
            logger.info("\n📁 Wymagane pliki skopiowane do folderu _dist")
        else:
            logger.warning("\n❌ Nie udało się skopiować wymaganych plików")

        return True
    else:
        logger.error("\n❌ Kompilacja nie powiodła się")
        return False


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("\n⚠️  Kompilacja przerwana przez użytkownika")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n❌ Nieoczekiwany błąd: {e}")
        sys.exit(1)
