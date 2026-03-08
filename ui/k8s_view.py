from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QLineEdit, QPlainTextEdit, QFrame
)
from PySide6.QtCore import Qt
from core.k8s_audit import K8sAuditor

class K8sView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(40, 40, 40, 40)
        self.layout.setSpacing(20)

        header = QLabel("Container & K8s Pentester")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #00ff00;")
        self.layout.addWidget(header)

        # Audit Config
        config_frame = QFrame()
        config_frame.setStyleSheet("background-color: #2b2b2b; border: 1px solid #3d3d3d; border-radius: 8px;")
        config_layout = QVBoxLayout(config_frame)
        
        self.cluster_ip = QLineEdit()
        self.cluster_ip.setPlaceholderText("Cluster Control Plane IP (e.g., 10.96.0.1)")
        config_layout.addWidget(QLabel("Target Cluster:"))
        config_layout.addWidget(self.cluster_ip)

        self.run_audit_btn = QPushButton("LAUNCH K8S CLUSTER AUDIT")
        self.run_audit_btn.setStyleSheet("background-color: #00ff00; color: black; font-weight: bold;")
        self.run_audit_btn.clicked.connect(self.run_audit)
        config_layout.addWidget(self.run_audit_btn)

        self.escape_btn = QPushButton("TEST DOCKER SOCKET ESCAPE")
        self.escape_btn.clicked.connect(self.run_escape_test)
        config_layout.addWidget(self.escape_btn)

        self.clear_btn = QPushButton("CLEAR TERMINAL")
        self.clear_btn.clicked.connect(lambda: self.terminal.clear())
        config_layout.addWidget(self.clear_btn)

        self.layout.addWidget(config_frame)

        self.terminal = QPlainTextEdit()
        self.terminal.setReadOnly(True)
        self.terminal.setStyleSheet("background-color: #000; color: #00ff00; font-family: monospace;")
        self.layout.addWidget(self.terminal)

        self.auditor = K8sAuditor()

    def run_audit(self):
        ip = self.cluster_ip.text()
        if not ip: return
        self.terminal.appendPlainText(f"[*] Connecting to {ip} API server...")
        findings = self.auditor.audit_kubelet(ip)
        for f in findings:
            self.terminal.appendPlainText(f"[!] FINDING: {f}")
        self.terminal.appendPlainText("[+] Audit complete.")

    def run_escape_test(self):
        self.terminal.appendPlainText("[*] Investigating mounted volumes...")
        res = self.auditor.run_docker_audit()
        self.terminal.appendPlainText(f"[!] STATUS: {res['status']} - {res['finding']}")

    def refresh_projects(self): pass
