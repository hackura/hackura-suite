from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QPlainTextEdit, QFrame, QFileDialog
)
from PySide6.QtCore import Qt
from core.git_scanner import GitScanner

class SecretsView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(40, 40, 40, 40)
        self.layout.setSpacing(20)

        header = QLabel("Secrets & Git Scanner")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #ffaa00;")
        self.layout.addWidget(header)

        # Scanner UI
        control_frame = QFrame()
        control_frame.setStyleSheet("background-color: #2b2b2b; border: 1px solid #3d3d3d; border-radius: 8px;")
        control_layout = QVBoxLayout(control_frame)
        
        self.scan_code_btn = QPushButton("SCAN CODE BLOCK")
        self.scan_code_btn.setStyleSheet("background-color: #ffaa00; color: black; font-weight: bold;")
        self.scan_code_btn.clicked.connect(self.run_code_scan)
        control_layout.addWidget(self.scan_code_btn)

        self.clear_btn = QPushButton("CLEAR RESULTS")
        self.clear_btn.clicked.connect(lambda: self.results_area.clear())
        control_layout.addWidget(self.clear_btn)

        self.layout.addWidget(control_frame)

        self.code_input = QPlainTextEdit()
        self.code_input.setPlaceholderText("Paste source code or .env contents here to scan for leaked keys...")
        self.code_input.setStyleSheet("background-color: #1a1a1a; color: #ddd;")
        self.layout.addWidget(self.code_input)

        self.results_area = QPlainTextEdit()
        self.results_area.setReadOnly(True)
        self.results_area.setStyleSheet("background-color: #000; color: #ffaa00; font-family: monospace;")
        self.layout.addWidget(self.results_area)

        self.scanner = GitScanner()

    def run_code_scan(self):
        text = self.code_input.toPlainText()
        if not text: return
        self.results_area.appendPlainText("[*] Commencing pattern-based secret discovery...")
        findings = self.scanner.scan_code(text)
        if not findings:
            self.results_area.appendPlainText("[+] No known secrets found in provided text.")
        else:
            for f in findings:
                self.results_area.appendPlainText(f"[!] FOUND {len(f['matches'])} {f['type']}(s)!")
                for m in f['matches']:
                    self.results_area.appendPlainText(f"    Match: {m[:10]}...[REDACTED]")

    def refresh_projects(self): pass
