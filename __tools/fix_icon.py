#!/usr/bin/env python3
"""
Skrypt do naprawy ikony - alternatywna metoda
"""

import os

from PIL import Image


def create_proper_ico():
    """Tworzy poprawny plik ICO z wieloma rozmiarami"""
    png_path = "core/resources/img/icon.png"
    ico_path = "core/resources/img/icon.ico"

    print("🔧 TWORZENIE POPRAWNEGO PLIKU ICO")
    print("=" * 40)

    if not os.path.exists(png_path):
        print(f"❌ Nie znaleziono pliku PNG: {png_path}")
        return False

    try:
        # Otwórz obraz PNG
        original_img = Image.open(png_path)
        print(f"📊 Oryginalny rozmiar: {original_img.size}")

        # Konwertuj na RGBA
        if original_img.mode != "RGBA":
            original_img = original_img.convert("RGBA")

        # Usuń stary plik ICO
        if os.path.exists(ico_path):
            os.remove(ico_path)
            print("🗑️  Usunięto stary plik ICO")

        # Rozmiary wymagane przez Windows
        sizes = [16, 24, 32, 40, 48, 64, 96, 128, 256]

        # Przygotuj obrazy o różnych rozmiarach
        images = []
        for size in sizes:
            # Skaluj obraz do wymaganego rozmiaru
            resized_img = original_img.resize((size, size), Image.Resampling.LANCZOS)
            images.append(resized_img)
            print(f"✅ Przygotowano rozmiar {size}x{size}")

        # Zapisz jako ICO używając pierwszego obrazu jako głównego
        # i dodając pozostałe jako dodatkowe rozmiary
        main_img = images[0]  # 16x16 jako główny

        # Metoda 1: Zapisz z głównym obrazem 16x16
        main_img.save(ico_path, format="ICO", append_images=images[1:])

        print(f"✅ Zapisano ICO: {ico_path}")
        print(f"📊 Rozmiar pliku: {os.path.getsize(ico_path)} bajtów")

        # Sprawdź czy plik zawiera wszystkie rozmiary
        with Image.open(ico_path) as ico_img:
            print(f"🎨 Format: {ico_img.format}")
            print(f"📐 Główny rozmiar: {ico_img.size}")

            # Sprawdź dostępne rozmiary
            available_sizes = []
            for i, size in enumerate(sizes):
                try:
                    ico_img.seek(i)
                    if ico_img.size == (size, size):
                        available_sizes.append(size)
                except (EOFError, IndexError):
                    # Reached end of ICO frames - this is expected
                    break
                except Exception as e:
                    print(f"⚠️  Błąd sprawdzania rozmiaru {size}: {e}")
                    break

            print(f"📋 Dostępne rozmiary: {available_sizes}")

            if len(available_sizes) >= 3:
                print("✅ ICO zawiera wystarczającą liczbę rozmiarów!")
                return True
            else:
                print("❌ ICO nie zawiera wystarczającej liczby rozmiarów")
                return False

    except Exception as e:
        print(f"❌ Błąd tworzenia ICO: {e}")
        return False


def create_simple_ico():
    """Tworzy prosty plik ICO z podstawowymi rozmiarami"""
    png_path = "core/resources/img/icon.png"
    ico_path = "core/resources/img/icon_simple.ico"

    print("\n🔧 TWORZENIE PROSTEGO PLIKU ICO")
    print("=" * 40)

    try:
        # Otwórz obraz PNG
        img = Image.open(png_path)

        # Konwertuj na RGBA
        if img.mode != "RGBA":
            img = img.convert("RGBA")

        # Podstawowe rozmiary Windows
        sizes = [(16, 16), (32, 32), (48, 48)]

        # Skaluj do najmniejszego rozmiaru i zapisz
        small_img = img.resize((16, 16), Image.Resampling.LANCZOS)
        small_img.save(ico_path, format="ICO")

        print(f"✅ Utworzono prosty ICO: {ico_path}")
        print(f"📊 Rozmiar pliku: {os.path.getsize(ico_path)} bajtów")

        return ico_path

    except Exception as e:
        print(f"❌ Błąd tworzenia prostego ICO: {e}")
        return None


if __name__ == "__main__":
    print("🔧 NAPRAWA IKONY CFAB BROWSER")
    print("=" * 60)

    # Spróbuj utworzyć poprawny plik ICO
    if create_proper_ico():
        print("\n🎉 Poprawny plik ICO został utworzony!")
        print("Teraz uruchom build_pyinstaller.py")
    else:
        print("\n⚠️  Nie udało się utworzyć poprawnego ICO")
        print("Tworzę prosty plik ICO...")

        simple_ico = create_simple_ico()
        if simple_ico:
            print(f"✅ Utworzono prosty plik ICO: {simple_ico}")
            print("Możesz go użyć jako alternatywy")
