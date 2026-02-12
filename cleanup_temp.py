import shutil
import os
import time

files_to_move = [
    "__bandit_report.py",
    "__radon_report.py",
    "__vulture_report.py",
    "debug_import.py",
    "quick_test.py",
    "list.md",
    "raport.md",
    "poprawki.md",
]

dirs_to_move = [
    "build",
    "_dist",
    "__raports"
]

dest_dir = "do_usuniecia"

if not os.path.exists(dest_dir):
    os.makedirs(dest_dir)
    print(f"Created {dest_dir}")

for f in files_to_move:
    if os.path.exists(f):
        try:
            shutil.move(f, os.path.join(dest_dir, f))
            print(f"Moved {f}")
        except Exception as e:
            print(f"Error moving {f}: {e}")
    else:
        print(f"File not found: {f}")

for d in dirs_to_move:
    if os.path.exists(d):
        try:
            # Handle directory move (if dest exists, shutil.move might move inside it, which is fine, or fail)
            dest_path = os.path.join(dest_dir, d)
            if os.path.exists(dest_path):
                print(f"Removing existing {dest_path} before move")
                shutil.rmtree(dest_path)
            shutil.move(d, dest_path)
            print(f"Moved dir {d}")
        except Exception as e:
            print(f"Error moving dir {d}: {e}")
    else:
        print(f"Dir not found: {d}")

print("Cleanup done.")
