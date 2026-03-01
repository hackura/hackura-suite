import subprocess
import shutil
import sys
import os

class ToolWrapper:
    """Base class for wrapping CLI tools across Linux and Windows."""
    
    def __init__(self, tool_name, windows_path=None):
        self.tool_name = tool_name
        self.windows_path = windows_path
        self.exec_path = self._find_executable()

    def _find_executable(self):
        """Locates the tool in the system PATH or specified Windows path."""
        # 1. Try system PATH (works for Linux native and some Windows installs)
        path = shutil.which(self.tool_name)
        if path:
            return path
            
        # 2. Try Windows specific path if provided
        if sys.platform == "win32" and self.windows_path:
            if os.path.exists(self.windows_path):
                return self.windows_path
                
        return None

    def is_available(self):
        return self.exec_path is not None

    def run(self, args, timeout=300):
        """Runs the tool with the provided arguments."""
        if not self.is_available():
            raise FileNotFoundError(f"Tool '{self.tool_name}' not found on this system.")
            
        cmd = [self.exec_path] + args
        try:
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=timeout,
                check=False
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Timeout expired"}
        except Exception as e:
            return {"success": False, "error": str(e)}
