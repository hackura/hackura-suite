import re
from core.db import db_manager

class GitScanner:
    def __init__(self):
        # Sample Gitleaks-style regexes
        self.patterns = {
            "AWS Key": r"AKIA[0-9A-Z]{16}",
            "MoMo API Key": r"momo_[0-9a-f]{32}",
            "Slack Token": r"xox[baprs]-[0-9a-zA-Z]{10,48}"
        }

    def scan_code(self, code_text):
        """Simulates scanning a block of code for secrets."""
        db_manager.log_action("Secrets Scan", "Scanned code block for sensitive keys")
        found = []
        for name, pattern in self.patterns.items():
            matches = re.findall(pattern, code_text)
            if matches:
                found.append({"type": name, "matches": matches})
        return found
