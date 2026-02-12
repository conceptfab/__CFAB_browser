import shutil
import os
import sys

# Define log file
log_file = "cleanup_result.txt"

def log(msg):
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(msg + "\n")
    print(msg)

# Clear log file
with open(log_file, "w", encoding="utf-8") as f:
    f.write("Starting cleanup...\n")

base_dir = os.getcwd()
dest_dir_name = "do_usuniecia" # ASCII name
dest_path = os.path.join(base_dir, dest_dir_name)

log(f"Base Directory: {base_dir}")
log(f"Destination: {dest_path}")

if not os.path.exists(dest_path):
    try:
        os.makedirs(dest_path)
        log(f"Created directory: {dest_path}")
    except Exception as e:
        log(f"CRITICAL: Failed to create target directory: {e}")
        sys.exit(1)

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
    "cleanup_v2.py",
    "force_cleanup.py"
]

dirs_to_move = [
    "build",
    "_dist",
    "__raports"
]

success_count = 0
fail_count = 0

for f in files_to_move:
    src = os.path.join(base_dir, f)
    dst = os.path.join(dest_path, f)
    
    log(f"Processing file: {f}")
    if os.path.exists(src):
        try:
            if os.path.exists(dst):
                log(f"  Warning: {f} already exists in destination. Overwriting/Skipping?")
                # shutil.move might fail if dest exists. Let's remove dest first if it's a file
                try:
                    os.remove(dst)
                    log(f"  Removed existing destination file: {dst}")
                except Exception as e:
                    log(f"  Failed to remove existing file {dst}: {e}")

            shutil.move(src, dst)
            if os.path.exists(dst) and not os.path.exists(src):
                log(f"  SUCCESS: Moved {f}")
                success_count += 1
            else:
                log(f"  Verify Failed: src still exists or dst missing for {f}")
                fail_count += 1
        except Exception as e:
            log(f"  FAIL: Error moving {f}: {e}")
            fail_count += 1
    else:
        if os.path.exists(dst):
            log(f"  Info: {f} already in destination.")
        else:
            log(f"  Info: Source file {f} not found.")

for d in dirs_to_move:
    src = os.path.join(base_dir, d)
    dst = os.path.join(dest_path, d)
    
    log(f"Processing dir: {d}")
    if os.path.exists(src):
        try:
            if os.path.exists(dst):
                log(f"  Removing existing dir at destination: {dst}")
                shutil.rmtree(dst)
            
            shutil.move(src, dst)
            if os.path.exists(dst) and not os.path.exists(src):
                 log(f"  SUCCESS: Moved dir {d}")
                 success_count += 1
            else:
                 log(f"  Verify Failed for dir {d}")
                 fail_count += 1
        except Exception as e:
            log(f"  FAIL: Error moving dir {d}: {e}")
            fail_count += 1
    else:
         if os.path.exists(dst):
            log(f"  Info: Dir {d} already in destination.")
         else:
            log(f"  Info: Source dir {d} not found.")

log(f"Cleanup finished. Moved: {success_count}, Failed: {fail_count}")
