#!/usr/bin/env python3
"""
Skrypt do szczegółowej analizy pliku ICO
"""

import os

from PIL import Image


def analyze_ico_file():
    """Analizuje plik ICO i sprawdza jego zawartość"""
    ico_path = "core/resources/img/icon.ico"

    print("🔍 SZCZEGÓŁOWA ANALIZA PLIKU ICO")
    print("=" * 50)

    if not os.path.exists(ico_path):
        print(f"❌ Plik ICO nie istnieje: {ico_path}")
        return False

    print(f"✅ Plik ICO istnieje: {ico_path}")
    print(f"📊 Rozmiar pliku: {os.path.getsize(ico_path)} bajtów")

    try:
        # Otwórz plik ICO
        with Image.open(ico_path) as img:
            print(f"🎨 Format: {img.format}")
            print(f"📐 Rozmiar: {img.size}")
            print(f"🎨 Tryb: {img.mode}")

            # Sprawdź czy to plik ICO
            if img.format != "ICO":
                print("❌ To nie jest plik ICO!")
                return False

            # Sprawdź dostępne rozmiary
            if hasattr(img, "n_frames"):
                print(f"📋 Liczba ramek/rozmiarów: {img.n_frames}")

            # Spróbuj wyświetlić wszystkie rozmiary
            try:
                # Sprawdź czy możemy iterować po obrazach
                if hasattr(img, "images"):
                    print(f"📋 Dostępne rozmiary: {img.images}")
                else:
                    print("⚠️  Nie można sprawdzić dostępnych rozmiarów")
            except Exception as e:
                print(f"⚠️  Błąd przy sprawdzaniu rozmiarów: {e}")

            # Sprawdź czy możemy otworzyć różne rozmiary
            sizes_to_check = [16, 24, 32, 40, 48, 64, 96, 128, 256]
            available_sizes = []

            for size in sizes_to_check:
                try:
                    # Spróbuj otworzyć konkretny rozmiar
                    img.seek(0)  # Reset do pierwszego obrazu
                    # Sprawdź czy możemy znaleźć obraz o tym rozmiarze
                    found = False
                    for i in range(img.n_frames if hasattr(img, "n_frames") else 1):
                        try:
                            img.seek(i)
                            if img.size == (size, size):
                                available_sizes.append(size)
                                found = True
                                break
                        except (EOFError, IndexError):
                            # Reached end of ICO frames - continue checking
                            continue
                        except Exception as e:
                            print(f"⚠️  Błąd sprawdzania ramki {i}: {e}")
                            continue
                    if not found:
                        print(f"❌ Brak rozmiaru {size}x{size}")
                except Exception as e:
                    print(f"❌ Błąd przy sprawdzaniu rozmiaru {size}: {e}")

            print(f"✅ Dostępne rozmiary: {available_sizes}")

            return True

    except Exception as e:
        print(f"❌ Błąd analizy pliku ICO: {e}")
        return False


def create_test_ico():
    """Tworzy testowy plik ICO z różnymi metodami"""
    png_path = "core/resources/img/icon.png"
    ico_path = "core/resources/img/icon_test.ico"

    print("\n🧪 TWORZENIE TESTOWEGO PLIKU ICO")
    print("=" * 40)

    if not os.path.exists(png_path):
        print(f"❌ Nie znaleziono pliku PNG: {png_path}")
        return False

    try:
        # Otwórz obraz PNG
        img = Image.open(png_path)
        print(f"📊 Oryginalny rozmiar: {img.size}")

        # Konwertuj na RGBA
        if img.mode != "RGBA":
            img = img.convert("RGBA")

        # Metoda 1: Standardowe rozmiary Windows
        sizes_1 = [(16, 16), (32, 32), (48, 48)]
        img.save(ico_path, format="ICO", sizes=sizes_1)
        print(f"✅ Utworzono ICO (metoda 1): {ico_path}")
        print(f"📊 Rozmiar pliku: {os.path.getsize(ico_path)} bajtów")

        # Metoda 2: Pełne rozmiary
        ico_path_2 = "core/resources/img/icon_test2.ico"
        sizes_2 = [
            (16, 16),
            (24, 24),
            (32, 32),
            (40, 40),
            (48, 48),
            (64, 64),
            (96, 96),
            (128, 128),
            (256, 256),
        ]
        img.save(ico_path_2, format="ICO", sizes=sizes_2)
        print(f"✅ Utworzono ICO (metoda 2): {ico_path_2}")
        print(f"📊 Rozmiar pliku: {os.path.getsize(ico_path_2)} bajtów")

        return True

    except Exception as e:
        print(f"❌ Błąd tworzenia testowych plików: {e}")
        return False


if __name__ == "__main__":
    print("🔍 ANALIZA IKONY CFAB BROWSER")
    print("=" * 60)

    # Analizuj obecny plik ICO
    analyze_ico_file()

    # Utwórz testowe pliki
    create_test_ico()

    print("\n💡 SUGESTIE:")
    print("1. Sprawdź czy plik ICO zawiera rozmiar 16x16")
    print("2. Spróbuj użyć różnych metod konwersji")
    print("3. Sprawdź czy Windows nie cache'uje starej ikony")
    print("4. Uruchom 'ie4uinit.exe -show' aby wyczyścić cache ikon")
