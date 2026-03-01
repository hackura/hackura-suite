import requests
import time
from PySide6.QtCore import QObject, Signal

class WebFuzzer(QObject):
    """Native Python web fuzzer for basic directory/file discovery."""
    progress = Signal(str)
    result_found = Signal(str, int) # url, status_code
    finished = Signal()

    def __init__(self, base_url, wordlist):
        super().__init__()
        self.base_url = base_url.rstrip('/')
        self.wordlist = wordlist
        self._is_running = True

    def stop(self):
        self._is_running = False

    def run(self):
        try:
            total = len(self.wordlist)
            for i, word in enumerate(self.wordlist):
                if not self._is_running: break
                
                word_clean = word.strip()
                url = f"{self.base_url}/{word_clean}"
                try:
                    # Basic check with SSL verification disabled for flexibility
                    resp = requests.get(url, timeout=3, allow_redirects=False, verify=False)
                    
                    # Verbose attempt logging
                    self.progress.emit(f"Checking: /{word_clean} -> Status: {resp.status_code}")
                    
                    if resp.status_code in [200, 301, 302, 403]:
                        self.result_found.emit(url, resp.status_code)
                    
                    # Small delay to avoid overwhelming target
                    time.sleep(0.05)
                except requests.exceptions.RequestException as re:
                    self.progress.emit(f"[!] Request Error (/{word_clean}): {str(re)}")
                except Exception as e:
                    self.progress.emit(f"[!] System Error (/{word_clean}): {str(e)}")
        finally:
            self.finished.emit()


