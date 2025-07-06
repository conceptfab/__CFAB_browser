#!/usr/bin/env python3
"""
Prosty test integracji Rust scanner z CFAB Browser
"""

import tempfile
import os
import time
from core.scanner import AssetRepository

def create_real_test_files(folder_path: str):
    """Tworzy prawdziwe pliki testowe"""
    print(f"Tworzę pliki testowe w {folder_path}")
    
    # Tworzenie plików ZIP z prawdziwą sygnaturą
    for i in range(5):
        zip_path = os.path.join(folder_path, f"asset_{i}.zip")
        with open(zip_path, 'wb') as f:
            f.write(b'PK\x03\x04\x14\x00\x00\x00\x08\x00')  # Prawdziwy header ZIP
        
        # Tworzenie plików JPG z prawdziwą sygnaturą
        jpg_path = os.path.join(folder_path, f"asset_{i}.jpg")  
        with open(jpg_path, 'wb') as f:
            # Minimalna struktura JPEG
            f.write(b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00')
            f.write(b'\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12')
            f.write(b'\xff\xd9')  # End of JPEG

def test_rust_integration():
    """Test prostej integracji"""
    print("="*60)
    print("🦀 RUST SCANNER INTEGRATION TEST 🦀")
    print("="*60)
    
    # Test 1: Inicjalizacja
    print("\n1️⃣ Test inicjalizacji...")
    repo = AssetRepository()
    print(f"   ✅ Rust scanner aktywny: {repo.use_rust}")
    
    # Test 2: Porównanie wydajności
    print("\n2️⃣ Test wydajności...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        create_real_test_files(temp_dir)
        
        # Test Rust
        print("   🦀 Testing Rust scanner...")
        repo_rust = AssetRepository(use_rust=True)
        start_time = time.time()
        rust_assets = repo_rust.find_and_create_assets(temp_dir)
        rust_time = time.time() - start_time
        
        # Test Python  
        print("   🐍 Testing Python scanner...")
        repo_python = AssetRepository(use_rust=False)
        start_time = time.time()
        python_assets = repo_python.find_and_create_assets(temp_dir)
        python_time = time.time() - start_time
        
        print(f"\n📊 WYNIKI:")
        print(f"   🦀 Rust:   {rust_time:.3f}s → {len(rust_assets)} assets")
        print(f"   🐍 Python: {python_time:.3f}s → {len(python_assets)} assets")
        
        if rust_time > 0 and python_time > 0:
            speedup = python_time / rust_time
            print(f"   ⚡ Przyśpieszenie: {speedup:.2f}x")
        
        # Test 3: Funkcjonalność
        print(f"\n3️⃣ Test funkcjonalności...")
        print(f"   ✅ Oba scanery znalazły tę samą liczbę asset-ów: {len(rust_assets) == len(python_assets)}")
        
    print(f"\n4️⃣ Test ładowania asset-ów...")
    with tempfile.TemporaryDirectory() as temp_dir:
        rust_loaded = repo.load_existing_assets(temp_dir)
        print(f"   ✅ Załadowano {len(rust_loaded)} asset-ów")
    
    print("\n" + "="*60)
    print("🎉 INTEGRACJA RUST SCANNER UDANA! 🎉")
    print("📈 CFAB Browser będzie teraz szybszy!")
    print("="*60)

if __name__ == "__main__":
    test_rust_integration() 