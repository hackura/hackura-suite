from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QLineEdit, QComboBox, QPlainTextEdit, QFrame, QTabWidget
)
from PySide6.QtCore import Qt
from core.creds import CredentialManager

class CredentialView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(40, 40, 40, 40)
        self.layout.setSpacing(20)

        header = QLabel("Credential Operations")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #ff3333;")
        self.layout.addWidget(header)

        self.tabs = QTabWidget()
        self.setup_harvester_tab()
        self.setup_stuffer_tab()
        self.layout.addWidget(self.tabs)

        self.manager = CredentialManager()

    def setup_harvester_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        info = QLabel("CREDENTIAL HARVESTER (PHISHING SIM)")
        info.setStyleSheet("font-weight: bold; color: #888;")
        layout.addWidget(info)

        self.template_combo = QComboBox()
        self.template_combo.addItems(["MoMo Ghana", "Vodafone Cash", "Generic Webmail"])
        layout.addWidget(QLabel("Select Template:"))
        layout.addWidget(self.template_combo)

        self.port_input = QLineEdit("8080")
        layout.addWidget(QLabel("Listener Port:"))
        layout.addWidget(self.port_input)

        self.start_harvest_btn = QPushButton("LAUNCH HARVESTER")
        self.start_harvest_btn.setStyleSheet("background-color: #ff3333; color: white; font-weight: bold;")
        self.start_harvest_btn.clicked.connect(self.run_harvest)
        layout.addWidget(self.start_harvest_btn)

        self.clear_harvest_btn = QPushButton("CLEAR LOGS")
        self.clear_harvest_btn.clicked.connect(lambda: self.harvest_logs.clear())
        layout.addWidget(self.clear_harvest_btn)
        
        self.harvest_logs = QPlainTextEdit()
        self.harvest_logs.setReadOnly(True)
        self.harvest_logs.setStyleSheet("background-color: #000; color: #00ff00; font-family: monospace;")
        layout.addWidget(self.harvest_logs)
        
        layout.addStretch()
        self.tabs.addTab(tab, "Harvester")

    def setup_stuffer_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        info = QLabel("CREDENTIAL STUFFER (BRUTE-FORCE)")
        info.setStyleSheet("font-weight: bold; color: #888;")
        layout.addWidget(info)

        self.target_url = QLineEdit()
        self.target_url.setPlaceholderText("Target Login URL (e.g., https://portal.gh/login)")
        layout.addWidget(QLabel("Target URL:"))
        layout.addWidget(self.target_url)

        self.wordlist_path = QLineEdit("/home/karl/.gemini/antigravity/scratch/hackura-suite/data/wordlists/common-pass.txt")
        layout.addWidget(QLabel("Wordlist Path:"))
        layout.addWidget(self.wordlist_path)

        self.start_stuff_btn = QPushButton("START STUFFING ATTACK")
        self.start_stuff_btn.setStyleSheet("background-color: #ffaa00; color: black; font-weight: bold;")
        self.start_stuff_btn.clicked.connect(self.run_stuffing)
        layout.addWidget(self.start_stuff_btn)

        self.clear_stuff_btn = QPushButton("CLEAR LOGS")
        self.clear_stuff_btn.clicked.connect(lambda: self.stuff_logs.clear())
        layout.addWidget(self.clear_stuff_btn)

        self.stuff_logs = QPlainTextEdit()
        self.stuff_logs.setReadOnly(True)
        self.stuff_logs.setStyleSheet("background-color: #000; color: #ffaa00; font-family: monospace;")
        layout.addWidget(self.stuff_logs)
        
        layout.addStretch()
        self.tabs.addTab(tab, "Stuffer")

    def run_harvest(self):
        tmpl = self.template_combo.currentText()
        port = self.port_input.text()
        self.harvest_logs.appendPlainText(f"[*] Initializing {tmpl} template...")
        self.harvest_logs.appendPlainText(f"[*] Starting HTTP listener on 0.0.0.0:{port}...")
        self.manager.start_harvester(tmpl, port)
        self.harvest_logs.appendPlainText("[+] Listener project deployed. Waiting for connections...")

    def run_stuffing(self):
        url = self.target_url.text()
        wlist = self.wordlist_path.text()
        if not url: return
        self.stuff_logs.appendPlainText(f"[*] Loading wordlist from {wlist}...")
        self.manager.stuff_credentials(url, wlist)
        self.stuff_logs.appendPlainText(f"[*] Commencing stuffing attack on {url}...")
        self.stuff_logs.appendPlainText("[!] Analyzing login responses for successful sessions...")

    def refresh_projects(self): pass
