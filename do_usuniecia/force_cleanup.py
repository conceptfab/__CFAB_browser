import shutil
import os
import time
import sys

# Flush output immediately
sys.stdout.reconfigure(encoding='utf-8')

files_to_move = [
    "__bandit_report.py",
    "__radon_report.py",
    "__vulture_report.py",
    "debug_import.py",
    "quick_test.py",
    "list.md",
    "raport.md",
    "poprawki.md",
    "cleanup_temp.py",
    "cleanup_v2.py"
]

dirs_to_move = [
    "build",
    "_dist",
    "__raports"
]

dest_dir = "do_usuniecia"

base_dir = os.getcwd()
dest_path = os.path.join(base_dir, dest_dir)

print(f"--- STARTING CLEANUP ---")
print(f"Base dir: {base_dir}")
print(f"Target: {dest_path}")

if not os.path.exists(dest_path):
    try:
        os.makedirs(dest_path)
        print(f"Created directory: {dest_path}")
    except Exception as e:
        print(f"CRITICAL: Failed to create target directory: {e}")
        sys.exit(1)

success_count = 0
fail_count = 0

for f in files_to_move:
    src = os.path.join(base_dir, f)
    dst = os.path.join(dest_path, f)
    
    if os.path.exists(src):
        try:
            # Try move
            shutil.move(src, dst)
            print(f"SUCCESS: Moved {f}")
            success_count += 1
        except PermissionError:
            print(f"FAIL: {f} is likely OPEN in another program (PermissionError).")
            # Try copy as backup? No, user wants move.
            fail_count += 1
        except Exception as e:
            print(f"FAIL: Could not move {f}: {e}")
            fail_count += 1
    else:
        # Check if it's already in destination
        if os.path.exists(dst):
            print(f"INFO: {f} is already in destination.")
        else:
            print(f"INFO: Source file {f} not found (maybe already moved).")

for d in dirs_to_move:
    src = os.path.join(base_dir, d)
    dst = os.path.join(dest_path, d)
    
    if os.path.exists(src):
        try:
            if os.path.exists(dst):
                print(f"Removing existing directory at destination: {dst}")
                shutil.rmtree(dst)
            shutil.move(src, dst)
            print(f"SUCCESS: Moved dir {d}")
            success_count += 1
        except Exception as e:
            print(f"FAIL: Could not move dir {d}: {e}")
            fail_count += 1
    else:
        if os.path.exists(dst):
            print(f"INFO: Directory {d} seems to be already in destination.")

print(f"--- FINISHED: {success_count} moved, {fail_count} failed ---")
