import os
import shutil
import subprocess

def build_deb():
    pkg_name = "hackura-suite_2.0.0_all"
    build_dir = os.path.join("build", "debian", pkg_name)
    
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
        
    os.makedirs(os.path.join(build_dir, "DEBIAN"))
    os.makedirs(os.path.join(build_dir, "opt", "hackura-suite"))
    
    # Copy source files
    items_to_copy = ["core", "ui", "assets", "main.py", "requirements.txt"]
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
    
    print("Building package...")
    try:
        subprocess.run(["dpkg-deb", "--build", build_dir], check=True)
        print(f"Package built: build/debian/{pkg_name}.deb")
    except Exception as e:
        print(f"Error building package: {e}")

if __name__ == "__main__":
    build_deb()
