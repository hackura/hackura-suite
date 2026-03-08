from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QLineEdit, QComboBox, QPlainTextEdit, QProgressBar, QFrame
)
from PySide6.QtCore import Qt, QThread, Signal
from core.api_scanner import APIScanner
import os

class ScanThread(QThread):
    log_signal = Signal(str)
    finished_signal = Signal()

    def __init__(self, scanner, endpoint, wordlist):
        super().__init__()
        self.scanner = scanner
        self.endpoint = endpoint
        self.wordlist = wordlist

    def run(self):
        self.log_signal.emit(f"[*] Starting discovery on {self.endpoint}...")
        process = self.scanner.start_fuzzing(self.endpoint, self.wordlist)
        
        if process:
            for line in iter(process.stdout.readline, ''):
                if line:
                    self.log_signal.emit(line.strip())
            process.stdout.close()
            process.wait()
        
        self.log_signal.emit("[+] Fuzzing operation completed.")
        self.finished_signal.emit()

class APIFuzzerView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(40, 40, 40, 40)
        self.layout.setSpacing(20)

        header = QLabel("API Fuzzer & Discovery")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #00ccff;")
        self.layout.addWidget(header)

        # Target Config
        config_frame = QFrame()
        config_frame.setStyleSheet("background-color: #2b2b2b; border: 1px solid #3d3d3d; border-radius: 8px;")
        config_layout = QVBoxLayout(config_frame)
        
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Base URL (e.g., https://api.example.com)")
        self.url_input.setFixedHeight(35)
        config_layout.addWidget(QLabel("Target Base URL:"))
        config_layout.addWidget(self.url_input)

        self.endpoint_combo = QComboBox()
        self.endpoint_combo.setEditable(True)
        config_layout.addWidget(QLabel("Endpoint to Fuzz:"))
        config_layout.addWidget(self.endpoint_combo)

        self.wordlist_input = QLineEdit("/usr/share/wordlists/dirb/common.txt")
        config_layout.addWidget(QLabel("Wordlist Path:"))
        config_layout.addWidget(self.wordlist_input)

        self.layout.addWidget(config_frame)

        # Buttons
        btn_layout = QHBoxLayout()
        self.discover_btn = QPushButton("DISCOVER ENDPOINTS")
        self.discover_btn.clicked.connect(self.discover)
        self.fuzz_btn = QPushButton("START FUZZING")
        self.fuzz_btn.clicked.connect(self.start_fuzz)
        self.fuzz_btn.setStyleSheet("background-color: #00ccff; color: black; font-weight: bold;")
        
        self.clear_btn = QPushButton("CLEAR LOGS")
        self.clear_btn.clicked.connect(lambda: self.terminal.clear())
        
        btn_layout.addWidget(self.discover_btn)
        btn_layout.addWidget(self.fuzz_btn)
        btn_layout.addWidget(self.clear_btn)
        self.layout.addLayout(btn_layout)

        # Progress & Logs
        self.progress = QProgressBar()
        self.layout.addWidget(self.progress)

        self.terminal = QPlainTextEdit()
        self.terminal.setReadOnly(True)
        self.terminal.setStyleSheet("background-color: #000; color: #00ccff; font-family: monospace; border: 1px solid #333;")
        self.layout.addWidget(self.terminal)

    def discover(self):
        url = self.url_input.text().strip()
        if not url: return
        
        self.terminal.appendPlainText(f"[*] Discovering endpoints for {url}...")
        scanner = APIScanner(url)
        endpoints = scanner.discover_endpoints()
        
        self.endpoint_combo.clear()
        if endpoints:
            self.endpoint_combo.addItems(endpoints)
            self.terminal.appendPlainText(f"[+] Found {len(endpoints)} potential endpoints.")
        else:
            self.terminal.appendPlainText("[-] No common endpoints discovered automatically.")

    def start_fuzz(self):
        url = self.url_input.text().strip()
        endpoint = self.endpoint_combo.currentText().strip()
        wordlist = self.wordlist_input.text().strip()
        
        if not url or not endpoint or not wordlist: return
        
        self.fuzz_btn.setEnabled(False)
        self.progress.setRange(0, 0) # Indeterminate
        
        self.scanner = APIScanner(url)
        self.thread = ScanThread(self.scanner, endpoint, wordlist)
        self.thread.log_signal.connect(self.terminal.appendPlainText)
        self.thread.finished_signal.connect(self.scan_finished)
        self.thread.start()

    def scan_finished(self):
        self.fuzz_btn.setEnabled(True)
        self.progress.setRange(0, 100)
        self.progress.setValue(100)

    def refresh_projects(self):
        pass
