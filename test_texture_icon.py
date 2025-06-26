#!/usr/bin/env python3
"""
Test weryfikacyjny dla ikony texture w ThumbnailTile

Ten test sprawdza czy:
1. Ikona texture jest ukryta domyślnie
2. Ikona texture pojawia się gdy textures_in_the_archive = True  
3. Ikona texture jest ukryta gdy textures_in_the_archive = False
"""

import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

# Dodaj ścieżkę do katalogu głównego projektu
sys.path.append(os.path.join(os.path.dirname(__file__)))

from core.thumbnail_tile import ThumbnailTile

def test_texture_icon_functionality():
    """Test funkcjonalności ikony texture"""
    print("=== Test ikony texture w ThumbnailTile ===")
    
    # Utwórz aplikację Qt (wymagane do testów UI)
    app = QApplication(sys.argv) if not QApplication.instance() else QApplication.instance()
    
    # Utwórz kafelek
    tile = ThumbnailTile(128, "test_asset.jpg", 1, 1)
    
    # Test 1: Ikona ukryta domyślnie
    print("Test 1: Ikona ukryta domyślnie")
    print(f"  Ikona widoczna: {tile.texture_icon.isVisible()} (oczekiwano False)")
    
    # Test 1a: Sprawdź czy ikona ma zawartość
    print("\nTest 1a: Sprawdzenie zawartości ikony przed użyciem")
    pixmap = tile.texture_icon.pixmap()
    text = tile.texture_icon.text()
    if pixmap and not pixmap.isNull():
        print(f"  Ikona ma pixmap o rozmiarze: {pixmap.width()}x{pixmap.height()}")
    elif text:
        print(f"  Ikona ma tekst fallback: '{text}'")
    else:
        print("  Ikona jest pusta")
    
    # Test 1b: Test bezpośredniego wywołania show_texture_icon
    print("\nTest 1b: Bezpośrednie wywołanie show_texture_icon()")
    tile.show_texture_icon()
    print(f"  Ikona widoczna po show_texture_icon(): {tile.texture_icon.isVisible()} (oczekiwano True)")
    
    # Ukryj ponownie do dalszych testów
    tile.hide_texture_icon()
    
    # Test 2: Asset z textures_in_the_archive = True
    print("\nTest 2: Asset z textures_in_the_archive = True")
    asset_with_textures = {
        "name": "material_with_textures",
        "archive": "material.zip", 
        "preview": "material.jpg",
        "size_mb": 5.2,
        "textures_in_the_archive": True
    }
    print(f"  Ustawianie asset_data z textures_in_the_archive = {asset_with_textures['textures_in_the_archive']}")
    tile.set_asset_data(asset_with_textures)
    print(f"  Ikona widoczna: {tile.texture_icon.isVisible()} (oczekiwano True)")
    
    # Test 3: Asset z textures_in_the_archive = False
    print("\nTest 3: Asset z textures_in_the_archive = False")
    asset_without_textures = {
        "name": "material_without_textures",
        "archive": "material.zip",
        "preview": "material.jpg", 
        "size_mb": 3.1,
        "textures_in_the_archive": False
    }
    tile.set_asset_data(asset_without_textures)
    print(f"  Ikona widoczna: {tile.texture_icon.isVisible()} (oczekiwano False)")
    
    # Test 4: Asset bez pola textures_in_the_archive (domyślnie False)
    print("\nTest 4: Asset bez pola textures_in_the_archive")
    asset_legacy = {
        "name": "legacy_asset",
        "archive": "legacy.zip",
        "preview": "legacy.jpg",
        "size_mb": 2.8
        # brak pola textures_in_the_archive
    }
    tile.set_asset_data(asset_legacy)
    print(f"  Ikona widoczna: {tile.texture_icon.isVisible()} (oczekiwano False)")
    
    # Test 5: Sprawdzenie czy ikona ma pixmap lub tekst
    print("\nTest 5: Sprawdzenie zawartości ikony po testach")
    pixmap = tile.texture_icon.pixmap()
    text = tile.texture_icon.text()
    if pixmap and not pixmap.isNull():
        print(f"  Ikona ma pixmap o rozmiarze: {pixmap.width()}x{pixmap.height()}")
    elif text:
        print(f"  Ikona ma tekst fallback: '{text}'")
    else:
        print("  Ikona jest pusta")
    
    # Test 6: Sprawdzenie ścieżki do pliku ikony
    print("\nTest 6: Sprawdzenie ścieżki do pliku texture.png")
    icon_path = os.path.join(os.path.dirname(__file__), "core", "resources", "img", "texture.png")
    print(f"  Ścieżka: {icon_path}")
    print(f"  Plik istnieje: {os.path.exists(icon_path)}")
    
    # Test 7: Sprawdzenie layoutu i parent widget
    print("\nTest 7: Sprawdzenie struktury widget")
    print(f"  Ikona ma parent: {tile.texture_icon.parent() is not None}")
    print(f"  Parent to tile: {tile.texture_icon.parent() is tile}")
    print(f"  Ikona width: {tile.texture_icon.width()}")
    print(f"  Ikona height: {tile.texture_icon.height()}")
    print(f"  Ikona isEnabled: {tile.texture_icon.isEnabled()}")
    print(f"  Ikona isHidden: {tile.texture_icon.isHidden()}")
    
    # Test 8: Pokaż kafelek żeby zobaczyć czy to pomaga
    print("\nTest 8: Pokazanie kafelka")
    tile.show()
    tile.texture_icon.setVisible(True)
    print(f"  Ikona widoczna po show() kafelka: {tile.texture_icon.isVisible()}")
    
    print("\n✅ Testy ikony texture zakończone!")
    
    return tile

if __name__ == "__main__":
    tile = test_texture_icon_functionality()
    
    # Test wizualny - pokaż kafelek z ikoną texture
    print("\n🔍 TEST WIZUALNY")
    print("Pokazuję kafelek z asset-em który ma textures_in_the_archive = True")
    
    # Ustaw asset z textures_in_the_archive = True
    asset_with_textures = {
        "name": "test_material_with_textures",
        "archive": "material.zip", 
        "preview": "material.jpg",
        "size_mb": 5.2,
        "textures_in_the_archive": True
    }
    tile.set_asset_data(asset_with_textures)
    
    print(f"Ikona widoczna przed show(): {tile.texture_icon.isVisible()}")
    tile.show()
    print(f"Ikona widoczna po show(): {tile.texture_icon.isVisible()}")
    
    print("Naciśnij Ctrl+C aby zakończyć test wizualny")
    
    # Pokaż kafelek wizualnie - uruchom tylko jeśli user chce
    try:
        app = QApplication.instance()
        if app:
            app.exec()
    except KeyboardInterrupt:
        print("\nTest wizualny zakończony przez użytkownika") 