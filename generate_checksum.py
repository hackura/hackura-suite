import hashlib
import os
import sys

def generate_checksum(file_path):
    """Generates SHA256 checksum for a file."""
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found.")
        return None
    
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        # Read and update hash string value in blocks of 4K
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    
    return sha256_hash.hexdigest()

def save_checksum(file_path):
    """Generates and saves the checksum to a .sha256 file."""
    checksum = generate_checksum(file_path)
    if checksum:
        checksum_file = f"{file_path}.sha256"
        with open(checksum_file, "w") as f:
            f.write(f"{checksum}  {os.path.basename(file_path)}")
        print(f"[+] SHA256 Checksum generated: {checksum}")
        print(f"[+] Saved to: {checksum_file}")
        return checksum
    return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate_checksum.py <file_path>")
        sys.exit(1)
    
    save_checksum(sys.argv[1])
