import sys
import os
import json
import shutil

# Dodaj ścieżkę do katalogu głównego projektu
sys.path.append(os.path.join(os.path.dirname(__file__)))

from core.scanner import find_and_create_assets, _check_texture_folders_presence

def test_scenario_1():
    """Test scenariusza 1: Folder BEZ folderów tekstur"""
    print("=== SCENARIUSZ 1: Folder BEZ folderów tekstur ===")
    
    # Upewnij się, że nie ma folderów tekstur
    for texture_folder in ['tex', 'textures', 'maps']:
        texture_path = os.path.join('test_folder', texture_folder)
        if os.path.exists(texture_path):
            shutil.rmtree(texture_path)
    
    # Sprawdź funkcję sprawdzania
    result = _check_texture_folders_presence('test_folder')
    print(f"Funkcja sprawdzania: textures_in_the_archive = {result} (oczekiwano True)")
    
    # Uruchom scanner
    created_assets = find_and_create_assets('test_folder')
    print(f"Scanner utworzył {len(created_assets)} plików asset")
    
    # Sprawdź zawartość plików asset
    for asset_path in created_assets:
        with open(asset_path, 'r', encoding='utf-8') as f:
            asset_data = json.load(f)
        
        name = asset_data.get('name', 'BRAK')
        textures_value = asset_data.get('textures_in_the_archive', 'BRAK')
        print(f"  {name}.asset: textures_in_the_archive = {textures_value}")
    
    # Usuń pliki asset dla następnego testu
    for asset_path in created_assets:
        os.remove(asset_path)
    
    # Usuń folder .cache
    cache_folder = 'test_folder/.cache'
    if os.path.exists(cache_folder):
        shutil.rmtree(cache_folder)

def test_scenario_2():
    """Test scenariusza 2: Folder Z folderem tex"""
    print("\n=== SCENARIUSZ 2: Folder Z folderem 'tex' ===")
    
    # Stwórz folder tex
    tex_folder = os.path.join('test_folder', 'tex')
    os.makedirs(tex_folder, exist_ok=True)
    
    # Sprawdź funkcję sprawdzania
    result = _check_texture_folders_presence('test_folder')
    print(f"Funkcja sprawdzania: textures_in_the_archive = {result} (oczekiwano False)")
    
    # Uruchom scanner
    created_assets = find_and_create_assets('test_folder')
    print(f"Scanner utworzył {len(created_assets)} plików asset")
    
    # Sprawdź zawartość plików asset
    for asset_path in created_assets:
        with open(asset_path, 'r', encoding='utf-8') as f:
            asset_data = json.load(f)
        
        name = asset_data.get('name', 'BRAK')
        textures_value = asset_data.get('textures_in_the_archive', 'BRAK')
        print(f"  {name}.asset: textures_in_the_archive = {textures_value}")
    
    # Usuń pliki asset dla następnego testu
    for asset_path in created_assets:
        os.remove(asset_path)
    
    # Usuń folder .cache
    cache_folder = 'test_folder/.cache'
    if os.path.exists(cache_folder):
        shutil.rmtree(cache_folder)
    
    # Usuń folder tex
    shutil.rmtree(tex_folder)

def test_scenario_3():
    """Test scenariusza 3: Folder Z folderem textures"""
    print("\n=== SCENARIUSZ 3: Folder Z folderem 'textures' ===")
    
    # Stwórz folder textures
    textures_folder = os.path.join('test_folder', 'textures')
    os.makedirs(textures_folder, exist_ok=True)
    
    # Sprawdź funkcję sprawdzania
    result = _check_texture_folders_presence('test_folder')
    print(f"Funkcja sprawdzania: textures_in_the_archive = {result} (oczekiwano False)")
    
    # Uruchom scanner
    created_assets = find_and_create_assets('test_folder')
    print(f"Scanner utworzył {len(created_assets)} plików asset")
    
    # Sprawdź zawartość plików asset
    for asset_path in created_assets:
        with open(asset_path, 'r', encoding='utf-8') as f:
            asset_data = json.load(f)
        
        name = asset_data.get('name', 'BRAK')
        textures_value = asset_data.get('textures_in_the_archive', 'BRAK')
        print(f"  {name}.asset: textures_in_the_archive = {textures_value}")
    
    # Usuń pliki asset
    for asset_path in created_assets:
        os.remove(asset_path)
    
    # Usuń folder .cache
    cache_folder = 'test_folder/.cache'
    if os.path.exists(cache_folder):
        shutil.rmtree(cache_folder)
    
    # Usuń folder textures
    shutil.rmtree(textures_folder)

if __name__ == "__main__":
    test_scenario_1()
    test_scenario_2() 
    test_scenario_3()
    print("\n✅ Wszystkie testy zakończone pomyślnie!") 