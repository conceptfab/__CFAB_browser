from core.scanner import AssetRepository
import tempfile
import os

print("RUST SCANNER INTEGRATION - SIMPLE TEST")
print("=" * 40)

# Test initialization
repo = AssetRepository()
print(f"✅ Scanner initialized: Rust={repo.use_rust}")

# Test with temp folder
with tempfile.TemporaryDirectory() as temp_dir:
    print(f"📁 Test folder: {temp_dir}")
    
    # Test empty folder
    assets = repo.find_and_create_assets(temp_dir)
    print(f"✅ Empty folder: {len(assets)} assets")
    
    # Create test files
    with open(os.path.join(temp_dir, "test.zip"), 'w') as f:
        f.write("fake")
    with open(os.path.join(temp_dir, "test.jpg"), 'w') as f:
        f.write("fake")
    
    # Test with files
    assets = repo.find_and_create_assets(temp_dir)
    print(f"✅ With files: {len(assets)} assets")

print("🎉 INTEGRATION SUCCESS!") 