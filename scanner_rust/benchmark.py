"""
Benchmark Python vs Rust scanner
"""
import time
import os
import logging
from pathlib import Path
import shutil
import sys

# Dodaj ścieżkę do głównego projektu
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Test folders setup
def create_test_data(base_path: str, num_files: int = 100) -> str:
    """Tworzy testowe dane do benchmarku"""
    test_folder = Path(base_path) / "test_scan_data"
    if test_folder.exists():
        shutil.rmtree(test_folder)
    test_folder.mkdir(exist_ok=True)

    print(f"Tworzę {num_files} testowych plików...")
    
    # Utwórz testowe pliki
    for i in range(num_files):
        # Pliki archiwum
        archive_file = test_folder / f"test_asset_{i:04d}.zip"
        archive_file.write_bytes(b"fake_zip_content" * 100)  # Symuluj zawartość

        # Pliki obrazów
        image_file = test_folder / f"test_asset_{i:04d}.png"
        image_file.write_bytes(b"fake_png_content" * 50)  # Symuluj zawartość

        # Niektóre niesparowane
        if i % 20 == 0:
            unpaired_archive = test_folder / f"unpaired_{i:04d}.zip"
            unpaired_archive.write_bytes(b"unpaired_content" * 30)

    print(f"Utworzono testowe dane w: {test_folder}")
    return str(test_folder)

def benchmark_rust_scanner(test_folder: str):
    """Benchmark tylko Rust scanner"""
    print("\n=== Rust Scanner Benchmark ===")
    
    try:
        # Import Rust scanner
        from core.rust_scanner import RustAssetRepository
        
        rust_scanner = RustAssetRepository()

        # Pomiar czasu
        start_time = time.time()
        rust_results = rust_scanner.find_and_create_assets(test_folder)
        rust_time = time.time() - start_time

        print(f"Czas Rust: {rust_time:.2f}s")
        print(f"Znalezione asset-y: {len(rust_results)}")
        
        # Test ładowania
        start_time = time.time()
        loaded_assets = rust_scanner.load_existing_assets(test_folder)
        load_time = time.time() - start_time
        
        print(f"Czas ładowania: {load_time:.2f}s")
        print(f"Załadowane asset-y: {len(loaded_assets)}")
        
        # Test skanowania plików
        start_time = time.time()
        archives, images = rust_scanner.scan_folder_for_files(test_folder)
        scan_time = time.time() - start_time
        
        print(f"Czas skanowania plików: {scan_time:.2f}s")
        print(f"Znalezione archiwa: {len(archives)}")
        print(f"Znalezione obrazy: {len(images)}")
        
        return rust_time, load_time, scan_time
        
    except ImportError as e:
        print(f"Nie można załadować Rust scanner: {e}")
        print("Upewnij się, że scanner jest zbudowany (uruchom build.bat)")
        return None, None, None
    except Exception as e:
        print(f"Błąd podczas benchmarku: {e}")
        return None, None, None

def main():
    """Główna funkcja benchmarku"""
    logging.basicConfig(level=logging.INFO)
    
    print("=== Benchmark Rust Scanner ===")
    print("Tworzenie danych testowych...")
    
    # Ilość plików do testowania
    num_files = 500
    
    # Przygotuj dane testowe
    test_folder = create_test_data(".", num_files)
    
    try:
        # Benchmark
        rust_time, load_time, scan_time = benchmark_rust_scanner(test_folder)
        
        if rust_time is not None:
            print(f"\n=== Podsumowanie ===")
            print(f"Tworzenie asset-ów: {rust_time:.2f}s")
            print(f"Ładowanie asset-ów: {load_time:.2f}s")
            print(f"Skanowanie plików: {scan_time:.2f}s")
            print(f"Całkowity czas: {rust_time + load_time + scan_time:.2f}s")
            
            # Oblicz statystyki
            files_per_second = num_files / rust_time if rust_time > 0 else 0
            print(f"Wydajność: {files_per_second:.1f} plików/s")
            
    finally:
        # Cleanup
        if os.path.exists(test_folder):
            print(f"\nUsuwam dane testowe: {test_folder}")
            shutil.rmtree(test_folder)

if __name__ == "__main__":
    main() 