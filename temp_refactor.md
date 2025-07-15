# 🐛 Code Audit Report

## 📁 Files Requiring Fixes

1. **core/amv_controllers/handlers/asset_rebuild_controller.py**
- **PROBLEM**: Duplicate AssetRebuilderWorker class
- **ISSUE**: thumbnail_cache imported in utilities.clear_thumbnail_cache_after_rebuild()
- **FIXES**:
  - Remove unused thumbnail_cache import (line 11)
  - Verify AssetRebuilderWorker class for duplicates

2. **core/amv_controllers/handlers/file_operation_controller.py**
- **PROBLEM**: _remove_moved_assets_optimized() method (150+ lines)
- **FIXES**:
  - Split _remove_moved_assets_optimized() into smaller functions
  - Remove duplicated path validation logic

3. **core/amv_models/file_operations_model.py**
- **PROBLEM**: Mixed Polish/English comments
- **ISSUE**: Inconsistent error handling in _move_single_asset_* methods
- **FIXES**:
  - Standardize comments to English
  - Unify error handling across methods

4. **core/amv_views/asset_tile_view.py**
- **PROBLEM**: Unused reset_for_pool() method
- **ISSUE**: Complex update_asset_data() logic
- **FIXES**:
  - Remove unused reset_for_pool() method
  - Simplify update_asset_data() logic

5. **core/main_window.py**
- **PROBLEM**: Duplicate asset counting logic
- **ISSUE**: Unused AssetCounts, AssetCountsDetailed structures
- **FIXES**:
  - Use SelectionCounter for asset counting
  - Remove unused data structures

6. **core/pairing_tab.py**
- **PROBLEM**: Polish strings and inconsistent naming
- **ISSUE**: Unused imports (json, subprocess, Path)
- **FIXES**:
  - Change Polish strings to English
  - Remove unused imports

7. **core/tools_tab.py**
- **PROBLEM**: Unnecessary proxy methods
- **ISSUE**: Polish UI strings
- **FIXES**:
  - Remove proxy methods (_handle_worker_*)
  - Fix Polish strings in UI

8. **core/utilities.py**
- **PROBLEM**: Duplicate logic in update_main_window_status()
- **ISSUE**: Potential module overlap
- **FIXES**:
  - Verify for duplicate functionality
  - Consider merging with other utility modules

9. **core/workers/worker_manager.py**
- **PROBLEM**: Lack of thread safety
- **ISSUE**: Inconsistent error handling
- **FIXES**:
  - Add thread safety to static methods
  - Standardize error handling

10. **core/tools/ (all worker files)**
- **PROBLEM**: Duplicate validation logic
- **ISSUE**: Duplicate Rust module loading
- **FIXES**:
  - Move common validation to BaseToolWorker
  - Remove duplicate Rust module loading

## 🎯 Priority Fixes

### High Priority (Critical Bugs):
- Points 1, 9, 17, 19

### Medium Priority (Optimization):
- Points 3, 7, 8, 13

### Low Priority (Code Cleanup):
- Points 11, 14, 15, 18, 20

## ⏳ Estimated Time
- ~4-6 hours of work for all fixes
