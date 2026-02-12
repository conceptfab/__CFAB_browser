import os
import sys
import subprocess

def check_command(cmd):
    try:
        subprocess.run([cmd, "--version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def main():
    print("🦀 --- CFAB Browser: Rust Engine Rebuilder ---")
    
    # 1. Check requirements
    missing = []
    if not check_command("rustc"): missing.append("Rust (rustc/cargo)")
    if not check_command("maturin"): missing.append("Maturin (pip install maturin)")
    
    if missing:
        print("\n❌ Error: Missing required tools:")
        for tool in missing:
            print(f"  - {tool}")
        print("\nPlease install these tools and try again.")
        print("Installation tips:")
        print("  - Rust: https://rustup.rs/")
        print("  - Maturin: pip install maturin")
        return 1

    # 2. Run the build script
    build_script = os.path.join("scanner_rust", "build.py")
    if not os.path.exists(build_script):
        print(f"❌ Error: Could not find build script at {build_script}")
        return 1

    print("\n🚀 Starting build process...")
    try:
        subprocess.run([sys.executable, build_script], check=True)
        print("\n✅ Build completed successfully!")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Build failed with exit code {e.returncode}")
        return e.returncode

if __name__ == "__main__":
    sys.exit(main())
