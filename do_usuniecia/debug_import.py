try:
    from core.scanner import AssetRepository
    print("SUCCESS: Imported AssetRepository from core.scanner")
    repo = AssetRepository()
    print("SUCCESS: Initialized AssetRepository")
    print(f"AssetRepository implementation: {repo._rust_repo.__class__.__name__}")
except Exception as e:
    print(f"ALARM: Error during verification: {e}")
    import traceback
    traceback.print_exc()
