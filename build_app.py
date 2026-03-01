import os
import sys
import subprocess
import shutil
from generate_checksum import save_checksum

APP_NAME = "HackuraSuite"
SPEC_FILE = "windows_build.spec"
DIST_DIR = "dist"

def build():
    print(f"[*] Starting Professional Build for {APP_NAME}...")
    
    # 1. Check for PyInstaller
    if not shutil.which("pyinstaller"):
        print("[!] Error: PyInstaller not found. Please install it with 'pip install pyinstaller'.")
        sys.exit(1)

    # 2. Run PyInstaller with Spec File
    print(f"[*] Executing PyInstaller with {SPEC_FILE}...")
    try:
        subprocess.run(["pyinstaller", "--noconfirm", SPEC_FILE], check=True)
    except subprocess.CalledProcessError as e:
        print(f"[!] PyInstaller failed: {e}")
        sys.exit(1)

    # 3. Identify the result (Look for EXE in dist/HackuraSuite/)
    # Note: On Linux, this creates a Linux ELF, but on Windows it creates an EXE.
    # We'll search for both for cross-platform utility script.
    exe_target = None
    search_path = os.path.join(DIST_DIR, APP_NAME)
    
    if os.path.exists(search_path):
        for root, dirs, files in os.walk(search_path):
            for file in files:
                if file == APP_NAME or file == f"{APP_NAME}.exe":
                    exe_target = os.path.join(root, file)
                    break
            if exe_target: break

    # 4. Generate Checksum
    if exe_target:
        print(f"[+] Build successful: {exe_target}")
        print("[*] Generating security checksum...")
        save_checksum(exe_target)
    else:
        print("[!] Error: Could not find built executable in dist/ directory.")
        sys.exit(1)

    print("\n[COMPLETE] Production bundle and checksums ready in 'dist/'.")

if __name__ == "__main__":
    build()
