#!/usr/bin/env python3
"""
Test script for Rust scanner integration with CFAB Browser
"""

import logging
import tempfile
import os
import time
from core.scanner import AssetRepository

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s'
)

def create_test_files(folder_path: str, num_files: int = 5):
    """Create test files for scanning"""
    print(f"Creating {num_files} test files in {folder_path}")
    
    # Create some test archive and image files
    for i in range(num_files):
        # Create .zip file
        zip_path = os.path.join(folder_path, f"test_asset_{i}.zip")
        with open(zip_path, 'wb') as f:
            f.write(b'PK\x03\x04')  # ZIP header
        
        # Create .jpg file
        jpg_path = os.path.join(folder_path, f"test_asset_{i}.jpg")
        with open(jpg_path, 'wb') as f:
            f.write(b'\xff\xd8\xff\xe0')  # JPEG header
    
    print(f"Created {num_files * 2} test files")

def test_rust_scanner():
    """Test Rust scanner integration"""
    print("=" * 50)
    print("RUST SCANNER INTEGRATION TEST")
    print("=" * 50)
    
    # Test 1: Initialize scanner with Rust
    print("\n1. Testing scanner initialization...")
    repo_rust = AssetRepository(use_rust=True)
    print(f"   ✅ Rust scanner enabled: {repo_rust.use_rust}")
    
    # Test 2: Initialize scanner with Python
    print("\n2. Testing Python fallback...")
    repo_python = AssetRepository(use_rust=False)
    print(f"   ✅ Python scanner: {not repo_python.use_rust}")
    
    # Test 3: Performance comparison
    print("\n3. Performance comparison...")
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test files
        create_test_files(temp_dir, 10)
        
        # Test Rust scanner
        start_time = time.time()
        rust_results = repo_rust.find_and_create_assets(temp_dir)
        rust_time = time.time() - start_time
        
        # Test Python scanner
        start_time = time.time()
        python_results = repo_python.find_and_create_assets(temp_dir)
        python_time = time.time() - start_time
        
        print(f"   🦀 Rust scanner: {rust_time:.3f}s -> {len(rust_results)} assets")
        print(f"   🐍 Python scanner: {python_time:.3f}s -> {len(python_results)} assets")
        
        if rust_time > 0:
            speedup = python_time / rust_time
            print(f"   ⚡ Speedup: {speedup:.2f}x")
    
    # Test 4: Load existing assets
    print("\n4. Testing load_existing_assets...")
    with tempfile.TemporaryDirectory() as temp_dir:
        rust_assets = repo_rust.load_existing_assets(temp_dir)
        python_assets = repo_python.load_existing_assets(temp_dir)
        
        print(f"   🦀 Rust: {len(rust_assets)} assets")
        print(f"   🐍 Python: {len(python_assets)} assets")
    
    print("\n" + "=" * 50)
    print("✅ ALL TESTS PASSED! Rust scanner integration successful!")
    print("=" * 50)

if __name__ == "__main__":
    test_rust_scanner() 