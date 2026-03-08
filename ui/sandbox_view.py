from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QPlainTextEdit, QFrame, QListWidget, QProgressBar
)
from PySide6.QtCore import Qt
import subprocess

class SandboxView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(40, 40, 40, 40)
        self.layout.setSpacing(20)

        header = QLabel("Sandbox Exploit Tester (Local Labs)")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #ff3333;")
        self.layout.addWidget(header)

        # Laboratory Control
        main_layout = QHBoxLayout()
        
        lab_frame = QFrame()
        lab_frame.setFixedWidth(350)
        lab_frame.setStyleSheet("background-color: #2b2b2b; border: 1px solid #3d3d3d; border-radius: 8px;")
        lab_layout = QVBoxLayout(lab_frame)
        
        lab_layout.addWidget(QLabel("Vulnerable Target Machines:"))
        self.target_list = QListWidget()
        self.target_list.addItems(["Metasploitable 2 (Linux)", "DVWA (Web App)", "Juice Shop (Modern Web)", "Windows 7 (Legacy SMB)"])
        lab_layout.addWidget(self.target_list)
        
        self.deploy_btn = QPushButton("DEPLOY DOCKER TARGET")
        self.deploy_btn.setStyleSheet("background-color: #ff3333; color: white; font-weight: bold;")
        self.deploy_btn.clicked.connect(self.deploy_target)
        lab_layout.addWidget(self.deploy_btn)
        
        self.stop_btn = QPushButton("STOP ALL LABS")
        self.stop_btn.clicked.connect(self.stop_labs)
        lab_layout.addWidget(self.stop_btn)
        
        main_layout.addWidget(lab_frame)
        
        # Terminal/Status
        self.terminal = QPlainTextEdit()
        self.terminal.setReadOnly(True)
        self.terminal.setStyleSheet("background-color: #000; color: #ff3333; font-family: monospace;")
        main_layout.addWidget(self.terminal)
        
        self.layout.addLayout(main_layout)
        
        self.progress = QProgressBar()
        self.layout.addWidget(self.progress)

    def deploy_target(self):
        target = self.target_list.currentItem()
        if not target: return
        
        target_name = target.text()
        self.terminal.appendPlainText(f"[*] Pulled image for {target_name}...")
        self.terminal.appendPlainText(f"[*] Starting container: {target_name.split(' (')[0].lower()}...")
        
        # Simulation of docker compose/run
        self.progress.setRange(0, 0)
        self.terminal.appendPlainText("[+] Target deployed at localhost:8888")
        self.progress.setRange(0, 100)
        self.progress.setValue(100)

    def stop_labs(self):
        self.terminal.appendPlainText("[!] Stopping all laboratory containers...")
        self.progress.setValue(0)

    def refresh_projects(self): pass
