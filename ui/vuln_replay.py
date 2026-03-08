from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QLineEdit, QPlainTextEdit, QFrame, QListWidget
)
from PySide6.QtCore import Qt
from core.db import db_manager

class VulnReplayView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(40, 40, 40, 40)
        self.layout.setSpacing(20)

        header = QLabel("Vulnerability Replay & Validation")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #00ccff;")
        self.layout.addWidget(header)

        # Session List
        main_layout = QHBoxLayout()
        
        list_frame = QFrame()
        list_frame.setFixedWidth(300)
        list_frame.setStyleSheet("background-color: #2b2b2b; border: 1px solid #3d3d3d; border-radius: 8px;")
        list_layout = QVBoxLayout(list_frame)
        list_layout.addWidget(QLabel("Stored Exploit Sessions:"))
        
        self.session_list = QListWidget()
        self.load_sessions()
        list_layout.addWidget(self.session_list)
        
        self.replay_btn = QPushButton("REPLAY SELECTED EXPLOIT")
        self.replay_btn.setStyleSheet("background-color: #00ccff; color: black; font-weight: bold;")
        self.replay_btn.clicked.connect(self.run_replay)
        list_layout.addWidget(self.replay_btn)
        
        main_layout.addWidget(list_frame)
        
        # Details & Log
        self.log_area = QPlainTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setStyleSheet("background-color: #000; color: #00ff00; font-family: monospace;")
        main_layout.addWidget(self.log_area)
        
        self.layout.addLayout(main_layout)

    def load_sessions(self):
        # Mocking stored sessions for Phase 3
        sessions = [
            "SQLi-Auth-Bypass-SRI",
            "XSS-Stored-Tonaton-Profile",
            "LFI-Config-Disclosure-Mel"
        ]
        self.session_list.addItems(sessions)

    def run_replay(self):
        curr = self.session_list.currentItem()
        if not curr: return
        
        session_name = curr.text()
        self.log_area.appendPlainText(f"[>] Initiating Replay: {session_name}")
        self.log_area.appendPlainText("[*] Serializing payload vectors...")
        self.log_area.appendPlainText("[*] Sending re-exploitation request to target endpoint...")
        
        # Simulate check
        import random
        success = random.choice([True, False])
        
        if success:
            self.log_area.appendPlainText(f"[!] REPLAY SUCCESS: Vulnerability {session_name} is STILL PRESENT.")
        else:
            self.log_area.appendPlainText(f"[+] REPLAY FAILED: Target is no longer vulnerable. REMEDIATION VERIFIED.")

    def refresh_projects(self): pass
