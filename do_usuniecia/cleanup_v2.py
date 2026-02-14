import shutil
import os
import sys

log_file = "cleanup_log.txt"

def log(msg):
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(msg + "\n")
    print(msg)

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

# Ensure absolute paths
base_dir = os.getcwd()
dest_path = os.path.join(base_dir, dest_dir)

log(f"Starting cleanup in {base_dir}")
log(f"Destination: {dest_path}")

if not os.path.exists(dest_path):
    try:
        os.makedirs(dest_path)
        log(f"Created {dest_path}")
    except Exception as e:
        log(f"Error creating dir {dest_path}: {e}")

for f in files_to_move:
    src = os.path.join(base_dir, f)
    dst = os.path.join(dest_path, f)
    
    if os.path.exists(src):
        try:
            shutil.move(src, dst)
            log(f"Moved {f}")
        except Exception as e:
            log(f"Error moving {f}: {e}")
    else:
        log(f"File not found: {f}")

for d in dirs_to_move:
    src = os.path.join(base_dir, d)
    dst = os.path.join(dest_path, d)
    
    if os.path.exists(src):
        try:
            if os.path.exists(dst):
                log(f"Removing existing {dst} before move")
                shutil.rmtree(dst)
            shutil.move(src, dst)
            log(f"Moved dir {d}")
        except Exception as e:
            log(f"Error moving dir {d}: {e}")
    else:
        log(f"Dir not found: {d}")

log("Cleanup done.")
