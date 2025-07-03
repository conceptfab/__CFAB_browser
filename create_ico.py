#!/usr/bin/env python3
"""
Skrypt do utworzenia poprawnego pliku ICO
"""

import os
import subprocess
import sys

from PIL import Image


def create_ico_with_pil_manual():
    """Tworzy plik ICO ręcznie używając PIL"""
    png_path = "core/resources/img/icon.png"
    ico_path = "core/resources/img/icon_manual.ico"

    print("🔧 TWORZENIE ICO RĘCZNIE (PIL)")
    print("=" * 40)

    try:
        # Otwórz obraz PNG
        img = Image.open(png_path)
        if img.mode != "RGBA":
            img = img.convert("RGBA")

        # Usuń stary plik
        if os.path.exists(ico_path):
            os.remove(ico_path)

        # Rozmiary dla Windows
        sizes = [16, 32, 48]

        # Skaluj do najmniejszego rozmiaru i zapisz
        small_img = img.resize((16, 16), Image.Resampling.LANCZOS)
        small_img.save(ico_path, format="ICO")

        print(f"✅ Utworzono ICO: {ico_path}")
        print(f"📊 Rozmiar pliku: {os.path.getsize(ico_path)} bajtów")

        return ico_path

    except Exception as e:
        print(f"❌ Błąd: {e}")
        return None


def create_ico_with_icoextract():
    """Tworzy plik ICO używając icoextract"""
    png_path = "core/resources/img/icon.png"
    ico_path = "core/resources/img/icon_extract.ico"

    print("🔧 TWORZENIE ICO (ICOEXTRACT)")
    print("=" * 40)

    try:
        import icoextract

        # Usuń stary plik
        if os.path.exists(ico_path):
            os.remove(ico_path)

        # Utwórz plik ICO z PNG
        # icoextract może nie obsługiwać bezpośredniej konwersji PNG->ICO
        # Spróbujmy innego podejścia

        print("⚠️  icoextract nie obsługuje bezpośredniej konwersji PNG->ICO")
        return None

    except ImportError:
        print("❌ icoextract nie jest zainstalowany")
        return None
    except Exception as e:
        print(f"❌ Błąd: {e}")
        return None


def create_ico_with_powershell():
    """Tworzy plik ICO używając PowerShell"""
    png_path = "core/resources/img/icon.png"
    ico_path = "core/resources/img/icon_ps.ico"

    print("🔧 TWORZENIE ICO (POWERSHELL)")
    print("=" * 40)

    try:
        # PowerShell script do konwersji
        ps_script = f"""
Add-Type -AssemblyName System.Drawing
$pngPath = "{png_path.replace('/', '\\')}"
$icoPath = "{ico_path.replace('/', '\\')}"

if (Test-Path $pngPath) {{
    $png = [System.Drawing.Image]::FromFile($pngPath)
    $ico = [System.Drawing.Icon]::FromHandle($png.GetHicon())
    
    $stream = [System.IO.File]::OpenWrite($icoPath)
    $ico.Save($stream)
    $stream.Close()
    
    $png.Dispose()
    $ico.Dispose()
    
    Write-Host "ICO created successfully"
}} else {{
    Write-Host "PNG file not found"
}}
"""

        # Zapisz skrypt PowerShell
        ps_file = "convert_icon.ps1"
        with open(ps_file, "w") as f:
            f.write(ps_script)

        # Uruchom PowerShell
        result = subprocess.run(
            ["powershell", "-ExecutionPolicy", "Bypass", "-File", ps_file],
            capture_output=True,
            text=True,
        )

        # Usuń plik skryptu
        os.remove(ps_file)

        if result.returncode == 0 and os.path.exists(ico_path):
            print(f"✅ Utworzono ICO: {ico_path}")
            print(f"📊 Rozmiar pliku: {os.path.getsize(ico_path)} bajtów")
            return ico_path
        else:
            print(f"❌ Błąd PowerShell: {result.stderr}")
            return None

    except Exception as e:
        print(f"❌ Błąd: {e}")
        return None


def test_ico_file(ico_path):
    """Testuje plik ICO"""
    print(f"\n🧪 TEST PLIKU: {ico_path}")
    print("=" * 30)

    if not os.path.exists(ico_path):
        print("❌ Plik nie istnieje")
        return False

    try:
        with Image.open(ico_path) as img:
            print(f"🎨 Format: {img.format}")
            print(f"📐 Rozmiar: {img.size}")
            print(f"📊 Rozmiar pliku: {os.path.getsize(ico_path)} bajtów")

            # Sprawdź czy to ICO
            if img.format == "ICO":
                print("✅ To jest poprawny plik ICO")
                return True
            else:
                print("❌ To nie jest plik ICO")
                return False

    except Exception as e:
        print(f"❌ Błąd testu: {e}")
        return False


if __name__ == "__main__":
    print("🔧 TWORZENIE POPRAWNYCH PLIKÓW ICO")
    print("=" * 60)

    # Metoda 1: PIL ręcznie
    ico1 = create_ico_with_pil_manual()
    if ico1:
        test_ico_file(ico1)

    # Metoda 2: PowerShell
    ico2 = create_ico_with_powershell()
    if ico2:
        test_ico_file(ico2)

    print("\n💡 NAJLEPSZY PLIK ICO:")
    if ico1 and ico2:
        # Porównaj rozmiary
        size1 = os.path.getsize(ico1)
        size2 = os.path.getsize(ico2)

        if size1 < size2:
            print(f"✅ Użyj: {ico1} (mniejszy rozmiar)")
            # Skopiuj jako główny
            import shutil

            shutil.copy2(ico1, "core/resources/img/icon.ico")
            print("📋 Skopiowano jako główny plik ikony")
        else:
            print(f"✅ Użyj: {ico2} (mniejszy rozmiar)")
            # Skopiuj jako główny
            import shutil

            shutil.copy2(ico2, "core/resources/img/icon.ico")
            print("📋 Skopiowano jako główny plik ikony")
    elif ico1:
        print(f"✅ Użyj: {ico1}")
        import shutil

        shutil.copy2(ico1, "core/resources/img/icon.ico")
        print("📋 Skopiowano jako główny plik ikony")
    elif ico2:
        print(f"✅ Użyj: {ico2}")
        import shutil

        shutil.copy2(ico2, "core/resources/img/icon.ico")
        print("📋 Skopiowano jako główny plik ikony")
    else:
        print("❌ Nie udało się utworzyć żadnego pliku ICO")
