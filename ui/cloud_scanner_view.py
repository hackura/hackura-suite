from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QLineEdit, QComboBox, QPlainTextEdit, QFrame, QProgressBar
)
from PySide6.QtCore import Qt
from core.cloud_scan import CloudScanner

class CloudScannerView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(40, 40, 40, 40)
        self.layout.setSpacing(20)

        header = QLabel("Cloud Misconfig Scanner")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #00ccff;")
        self.layout.addWidget(header)

        # Config Area
        config_frame = QFrame()
        config_frame.setStyleSheet("background-color: #2b2b2b; border: 1px solid #3d3d3d; border-radius: 8px;")
        config_layout = QVBoxLayout(config_frame)
        
        self.provider_combo = QComboBox()
        self.provider_combo.addItems(["AWS (Africa-Central)", "GCP", "Azure", "Melcloud (Ghana)"])
        config_layout.addWidget(QLabel("Cloud Provider:"))
        config_layout.addWidget(self.provider_combo)

        self.target_input = QLineEdit()
        self.target_input.setPlaceholderText("Account ID, Domain or Bucket Pattern")
        config_layout.addWidget(QLabel("Scan Target:"))
        config_layout.addWidget(self.target_input)

        self.run_btn = QPushButton("EXECUTE CLOUD AUDIT")
        self.run_btn.setStyleSheet("background-color: #00ccff; color: black; font-weight: bold; height: 40px;")
        self.run_btn.clicked.connect(self.run_scan)
        config_layout.addWidget(self.run_btn)

        self.clear_btn = QPushButton("CLEAR LOGS")
        self.clear_btn.clicked.connect(lambda: self.terminal.clear())
        config_layout.addWidget(self.clear_btn)

        self.layout.addWidget(config_frame)
        
        self.progress = QProgressBar()
        self.layout.addWidget(self.progress)

        self.terminal = QPlainTextEdit()
        self.terminal.setReadOnly(True)
        self.terminal.setStyleSheet("background-color: #000; color: #00ccff; font-family: monospace;")
        self.layout.addWidget(self.terminal)

        self.scanner = CloudScanner()

    def run_scan(self):
        provider = self.provider_combo.currentText()
        target = self.target_input.text()
        if not target: return

        self.progress.setRange(0, 0)
        self.terminal.appendPlainText(f"[*] Authenticating to {provider} mgmt plane...")
        self.terminal.appendPlainText(f"[*] Enumerating resources for {target}...")
        
        findings = self.scanner.scan_buckets(provider, target)
        for f in findings:
            self.terminal.appendPlainText(f"[!] {f['severity'].upper()}: {f['title']}")
            self.terminal.appendPlainText(f"    Details: {f['desc']}")
        
        self.progress.setRange(0, 100)
        self.progress.setValue(100)
        self.terminal.appendPlainText("[+] Cloud audit finished.")

    def refresh_projects(self): pass
