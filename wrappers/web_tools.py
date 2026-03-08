import subprocess
import os

class GenericWebWrapper:
    def __init__(self, tool_name):
        self.tool_name = tool_name

    def is_available(self):
        try:
            subprocess.run([self.tool_name, "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except FileNotFoundError:
            return False

    def scan(self, url, wordlist=None):
        if not self.is_available():
            return {"success": False, "error": f"{self.tool_name} not installed"}
            
        cmd = [self.tool_name, "-u", url]
        if wordlist:
            if self.tool_name == "gobuster":
                cmd = ["gobuster", "dir", "-u", url, "-w", wordlist]
            elif self.tool_name == "dirsearch":
                cmd = ["dirsearch", "-u", url, "-w", wordlist]
                
        try:
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            stdout, stderr = process.communicate()
            return {"success": True, "raw": stdout, "error": stderr}
        except Exception as e:
            return {"success": False, "error": str(e)}

class GobusterWrapper(GenericWebWrapper):
    def __init__(self):
        super().__init__("gobuster")

class DirsearchWrapper(GenericWebWrapper):
    def __init__(self):
        super().__init__("dirsearch")
