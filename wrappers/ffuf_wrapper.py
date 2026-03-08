import subprocess
import shutil
import os

class FfufWrapper:
    def __init__(self, binary_path=None):
        self.binary = binary_path or shutil.which("ffuf")
        
    def is_available(self):
        return self.binary is not None

    def fuzz(self, url, wordlist, extra_args=None):
        """
        Executes ffuf against a target.
        url: The target URL with 'FUZZ' keyword.
        wordlist: Path to the wordlist file.
        """
        if not self.is_available():
            raise FileNotFoundError("ffuf binary not found in PATH")

        cmd = [self.binary, "-u", url, "-w", wordlist]
        if extra_args:
            cmd.extend(extra_args)

        # Ensure the output directory exists if -o is used
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            return process
        except Exception as e:
            print(f"Error launching ffuf: {e}")
            return None

    def get_version(self):
        if not self.is_available():
            return None
        try:
            res = subprocess.run([self.binary, "-V"], capture_output=True, text=True)
            return res.stdout.strip()
        except:
            return "Unknown"
