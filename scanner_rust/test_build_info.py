#!/usr/bin/env python3
"""
Test funkcji informacji o kompilacji modułów Rust
"""

import sys
import os

# Dodaj ścieżkę do modułów Rust
rust_path = os.path.join(os.path.dirname(__file__), '..', 'core', '__rust')
if os.path.exists(rust_path):
    sys.path.insert(0, rust_path)
    print(f"✅ Dodano ścieżkę do modułów Rust: {rust_path}")
else:
    print(f"❌ Nie znaleziono ścieżki do modułów Rust: {rust_path}")

def test_scanner_module():
    """Test modułu scanner (numer 1)"""
    try:
        import scanner_rust
        
        print("=== MODUŁ SCANNER (1) ===")
        print(f"Informacje: {scanner_rust.get_module_info()}")
        print(f"Numer modułu: {scanner_rust.get_module_number()}")
        print(f"Numer kompilacji: {scanner_rust.get_build_number()}")
        print(f"Data/godzina kompilacji: {scanner_rust.get_build_datetime()}")
        print(f"Hash Git: {scanner_rust.get_git_commit()}")
        print(f"Prefiks logowania: {scanner_rust.get_log_prefix()}")
        print(f"Przykład komunikatu: {scanner_rust.format_log_message('Test message')}")
        
        info = scanner_rust.get_build_info()
        print(f"Wszystkie informacje: {dict(info)}")
        print()
        
    except ImportError as e:
        print(f"Błąd importu scanner_rust: {e}")

def test_hash_utils_module():
    """Test modułu hash_utils (numer 2)"""
    try:
        import hash_utils
        
        print("=== MODUŁ HASH_UTILS (2) ===")
        print(f"Informacje: {hash_utils.get_module_info()}")
        print(f"Numer modułu: {hash_utils.get_module_number()}")
        print(f"Numer kompilacji: {hash_utils.get_build_number()}")
        print(f"Data/godzina kompilacji: {hash_utils.get_build_datetime()}")
        print(f"Hash Git: {hash_utils.get_git_commit()}")
        print(f"Prefiks logowania: {hash_utils.get_log_prefix()}")
        print(f"Przykład komunikatu: {hash_utils.format_log_message('Test message')}")
        
        info = hash_utils.get_build_info()
        print(f"Wszystkie informacje: {dict(info)}")
        print()
        
    except ImportError as e:
        print(f"Błąd importu hash_utils: {e}")

def test_image_tools_module():
    """Test modułu image_tools (numer 3)"""
    try:
        import image_tools
        
        print("=== MODUŁ IMAGE_TOOLS (3) ===")
        print(f"Informacje: {image_tools.get_module_info()}")
        print(f"Numer modułu: {image_tools.get_module_number()}")
        print(f"Numer kompilacji: {image_tools.get_build_number()}")
        print(f"Data/godzina kompilacji: {image_tools.get_build_datetime()}")
        print(f"Hash Git: {image_tools.get_git_commit()}")
        print(f"Prefiks logowania: {image_tools.get_log_prefix()}")
        print(f"Przykład komunikatu: {image_tools.format_log_message('Test message')}")
        
        info = image_tools.get_build_info()
        print(f"Wszystkie informacje: {dict(info)}")
        print()
        
    except ImportError as e:
        print(f"Błąd importu image_tools: {e}")

def test_all_modules():
    """Test wszystkich modułów"""
    print("🧪 TEST INFORMACJI O KOMPILACJI MODUŁÓW RUST")
    print("=" * 60)
    
    test_scanner_module()
    test_hash_utils_module()
    test_image_tools_module()
    
    print("✅ Test zakończony")

if __name__ == "__main__":
    test_all_modules() 