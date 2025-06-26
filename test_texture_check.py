import sys
import os
import json

# Dodaj ścieżkę do katalogu głównego projektu
sys.path.append(os.path.join(os.path.dirname(__file__)))

from core.scanner import find_and_create_assets, _check_texture_folders_presence

def test_texture_check():
    """Test funkcji sprawdzania folderów tekstur"""
    print("=== Test sprawdzania folderów tekstur ===")
    
    # Test 1: Folder bez folderów tekstur (tekstury w archiwum)
    print("\nTest 1: Folder bez folderów tekstur")
    result1 = _check_texture_folders_presence('test_folder')
    print(f"Wynik: textures_in_the_archive = {result1} (oczekiwano True)")
    
    # Test 2: Stwórz folder z folderem tex
    os.makedirs('test_folder/tex', exist_ok=True)
    print("\nTest 2: Folder z folderem 'tex'")
    result2 = _check_texture_folders_presence('test_folder')
    print(f"Wynik: textures_in_the_archive = {result2} (oczekiwano False)")
    
    # Test 3: Usuń folder tex, stwórz folder textures
    os.rmdir('test_folder/tex')
    os.makedirs('test_folder/textures', exist_ok=True)
    print("\nTest 3: Folder z folderem 'textures'")
    result3 = _check_texture_folders_presence('test_folder')
    print(f"Wynik: textures_in_the_archive = {result3} (oczekiwano False)")
    
    # Test 4: Usuń folder textures, stwórz folder maps
    os.rmdir('test_folder/textures')
    os.makedirs('test_folder/maps', exist_ok=True)
    print("\nTest 4: Folder z folderem 'maps'")
    result4 = _check_texture_folders_presence('test_folder')
    print(f"Wynik: textures_in_the_archive = {result4} (oczekiwano False)")
    
    # Usuń folder maps dla następnych testów
    os.rmdir('test_folder/maps')

def test_scanner_with_assets():
    """Test scannera z tworzeniem plików asset"""
    print("\n=== Test scannera z plikami asset ===")
    
    # Uruchom scanner na folderze testowym
    created_assets = find_and_create_assets('test_folder')
    print(f"Utworzono {len(created_assets)} plików asset")
    
    # Sprawdź zawartość utworzonych plików asset
    for asset_path in created_assets:
        print(f"\nSprawdzam plik: {asset_path}")
        try:
            with open(asset_path, 'r', encoding='utf-8') as f:
                asset_data = json.load(f)
            
            textures_value = asset_data.get('textures_in_the_archive', 'BRAK')
            print(f"  textures_in_the_archive: {textures_value}")
            print(f"  name: {asset_data.get('name', 'BRAK')}")
            print(f"  archive: {asset_data.get('archive', 'BRAK')}")
            print(f"  preview: {asset_data.get('preview', 'BRAK')}")
            
        except Exception as e:
            print(f"  Błąd przy czytaniu pliku: {e}")

def cleanup():
    """Czyści pliki testowe"""
    print("\n=== Sprzątanie ===")
    import glob
    import shutil
    
    # Usuń pliki asset
    for asset_file in glob.glob('test_folder/*.asset'):
        os.remove(asset_file)
        print(f"Usunięto: {asset_file}")
    
    # Usuń folder .cache jeśli istnieje
    cache_folder = 'test_folder/.cache'
    if os.path.exists(cache_folder):
        shutil.rmtree(cache_folder)
        print(f"Usunięto folder: {cache_folder}")

if __name__ == "__main__":
    test_texture_check()
    test_scanner_with_assets()
    cleanup()
    print("\nTest zakończony!") 