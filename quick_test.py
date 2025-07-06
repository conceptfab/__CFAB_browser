#!/usr/bin/env python3
"""
Quick test for Rust scanner integration
"""

import os
import tempfile
from core.scanner import AssetRepository

def main():
    print("🦀 RUST SCANNER QUICK TEST")
    print("-" * 30)
    
    # Test 1: Basic initialization
    repo = AssetRepository()
    print(f"✅ Scanner initialized, Rust enabled: {repo.use_rust}")
    
    # Test 2: Empty folder scan
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"📁 Testing empty folder: {temp_dir}")
        assets = repo.find_and_create_assets(temp_dir)
        print(f"✅ Empty folder scan: {len(assets)} assets found")
        
        # Test 3: Create test files and scan
        print("📝 Creating test files...")
        zip_file = os.path.join(temp_dir, "test.zip")
        jpg_file = os.path.join(temp_dir, "test.jpg")
        
        with open(zip_file, 'w') as f:
            f.write("fake zip")
        with open(jpg_file, 'w') as f:
            f.write("fake jpg")
        
        print(f"✅ Created 2 test files")
        
        assets = repo.find_and_create_assets(temp_dir)
        print(f"✅ Scan with files: {len(assets)} assets found")
        
        # Test 4: Load existing
        existing = repo.load_existing_assets(temp_dir)
        print(f"✅ Load existing: {len(existing)} assets found")
    
    print("🎉 ALL TESTS COMPLETED!")

if __name__ == "__main__":
    main() 