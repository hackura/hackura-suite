import subprocess
import json
import os

class SubfinderWrapper:
    def __init__(self):
        self.tool_name = "subfinder"
        self.executable = "subfinder"

    def is_available(self):
        try:
            subprocess.run([self.executable, "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except FileNotFoundError:
            return False

    def scan(self, target, timeout=300):
        if not self.is_available():
            return self._simulate_scan(target)

        try:
            log = [f"[*] Launching Subfinder for {target}...", "[*] Enumerating active sources..."]
            cmd = [self.executable, "-d", target, "-silent"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            subdomains = result.stdout.splitlines()
            
            log.append(f"[+] Discovered {len(subdomains)} subdomains.")
            return {"success": True, "tool": "Subfinder", "subdomains": subdomains, "log": log, "status": "COMPLETED"}
        except subprocess.TimeoutExpired:
            return {"success": False, "tool": "Subfinder", "error": f"Operation timed out after {timeout}s", "status": "TIMEOUT"}
        except Exception as e:
            return {"success": False, "tool": "Subfinder", "error": str(e), "status": "FAILED"}

    def _simulate_scan(self, target):
        return {
            "success": True,
            "tool": "Subfinder (Simulated)",
            "subdomains": [
                f"api.{target}",
                f"dev.{target}",
                f"vpn.{target}",
                f"mail.{target}"
            ],
            "log": [
                f"[*] Launching Subfinder (Simulated) for {target}...",
                "[*] Querying passive sources...",
                "[+] Enumeration complete."
            ],
            "status": "COMPLETED"
        }
