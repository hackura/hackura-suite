import os
import shutil
import subprocess

def build_deb():
    pkg_name = "hackura-suite_5.7.0_all"
    build_dir = os.path.join("build", "debian", pkg_name)
    
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
        
    os.makedirs(os.path.join(build_dir, "DEBIAN"))
    os.makedirs(os.path.join(build_dir, "opt", "hackura-suite"))
    os.makedirs(os.path.join(build_dir, "usr", "bin"))
    os.makedirs(os.path.join(build_dir, "usr", "share", "applications"))
    os.makedirs(os.path.join(build_dir, "usr", "share", "pixmaps"))
    
    # Copy source files
    items_to_copy = ["core", "ui", "assets", "wrappers", "data", "main.py", "requirements.txt"]
    for item in items_to_copy:
        src = item
        dst = os.path.join(build_dir, "opt", "hackura-suite", item)
        if os.path.isdir(src):
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst)
            
    # Copy control and postinst
    shutil.copy2("packaging/debian/control", os.path.join(build_dir, "DEBIAN", "control"))
    shutil.copy2("packaging/debian/postinst", os.path.join(build_dir, "DEBIAN", "postinst"))
    os.chmod(os.path.join(build_dir, "DEBIAN", "postinst"), 0o755)
    
    # Copy desktop and icon
    shutil.copy2("packaging/debian/hackura-suite.desktop", os.path.join(build_dir, "usr", "share", "applications", "hackura-suite.desktop"))
    shutil.copy2("assets/logo.png", os.path.join(build_dir, "usr", "share", "pixmaps", "hackura-suite.png"))

    # Create symlink for bin
    bin_path = os.path.join(build_dir, "usr", "bin", "hackura-suite")
    with open(bin_path, 'w') as f:
        f.write("#!/bin/bash\n/usr/bin/python3 /opt/hackura-suite/main.py \"$@\"\n")
    os.chmod(bin_path, 0o755)
    
    print("Building package...")
    try:
        subprocess.run(["dpkg-deb", "--build", build_dir], check=True)
        print(f"Package built: build/debian/{pkg_name}.deb")
    except Exception as e:
        print(f"Error building package: {e}")

if __name__ == "__main__":
    build_deb()
