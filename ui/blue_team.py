from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QComboBox, QPlainTextEdit, QLineEdit, QMessageBox, QGroupBox, QGridLayout, QScrollArea
)
from PySide6.QtCore import Qt
import time

class BlueTeamView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(40, 40, 40, 40)

        header = QLabel("Blue Team Operations Center")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #00ff00;")
        self.layout.addWidget(header)

        # Tool Registry (50+ Tools Across Categories)
        self.tools = {
            "SIEM & LOGGING": [
                "Wazuh Agent Deployment", "Splunk Log Forwarder", "ELK Stack Audit", 
                "Graylog Intake Probe", "Sysmon Configuration", "Rsyslog Verification",
                "Prometheus Exporter", "Loki Log Search", "Auditd Policy Review", "Kafka Stream Audit"
            ],
            "ENDPOINT SECURITY": [
                "ClamAV Full System Scan", "OSSEC HIDS Probe", "SentinelOne Simulation",
                "Crowdstrike Agent Audit", "Carbon Black Verification", "Microsoft Defender ATP",
                "FireEye HX Audit", "Sophos Central Probe", "Malwarebytes Discovery", "Rootkit Hunter (rkhunter)"
            ],
            "NETWORK DEFENSE": [
                "Snort IDS/IPS Tuning", "Suricata Alert Audit", "Zeek (Bro) Traffic Analyzer",
                "Cisco ASA/FTD Policy", "Palo Alto Panorama Audit", "FortiGate Rule Review",
                "Cloudflare WAF Check", "AWS Shield Verification", "Akamai Edge Audit", "NfSen Netflow Probe"
            ],
            "IDENTITY & ACCESS": [
                "IAM Policy Analyzer", "Active Directory Audit", "Okta MFA Verification",
                "Azure AD Identity Protection", "Google Workspace Security Audit", "HashiCorp Vault Audit",
                "CyberArk PAS Review", "SailPoint Identity Governance", "Duo Security Audit", "Privilege Escalation Audit"
            ],
            "INCIDENT RESPONSE": [
                "Volatility Memory Forensics", "Autopsy Forensic Discovery", "TheHive Case Review",
                "Cortex Analyzer Probe", "MISP Threat Intel Sync", "SANS SIFT Toolkit",
                "EnCase Forensics Probe", "FTK Imager Audit", "Velociraptor EDR Probe", "Sandbox Execution (Cuckoo)"
            ]
        }

        # Category Selection
        cat_layout = QHBoxLayout()
        cat_layout.addWidget(QLabel("Defensive Tier:"))
        self.cat_combo = QComboBox()
        self.cat_combo.addItems(list(self.tools.keys()))
        self.cat_combo.currentTextChanged.connect(self.update_tool_list)
        cat_layout.addWidget(self.cat_combo)
        self.layout.addLayout(cat_layout)

        # Tool Selection
        tool_layout = QHBoxLayout()
        tool_layout.addWidget(QLabel("Investigative Tool:"))
        self.tool_combo = QComboBox()
        tool_layout.addWidget(self.tool_combo)
        self.layout.addLayout(tool_layout)

        # Dynamic Config (Target)
        self.target_input = QLineEdit()
        self.target_input.setPlaceholderText("Target Domain/IP or Endpoint ID")
        self.target_input.setFixedHeight(35)
        self.layout.addWidget(self.target_input)

        self.run_btn = QPushButton(" LAUNCH DEFENSIVE OPERATION")
        self.run_btn.setFixedHeight(50)
        self.run_btn.setStyleSheet("background-color: #00ff00; color: black; font-weight: bold; font-size: 14px;")
        self.run_btn.clicked.connect(self.start_op)
        self.layout.addWidget(self.run_btn)

        # Terminal
        self.log_area = QPlainTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setStyleSheet("background-color: #000; color: #00ff00; font-family: monospace; border: 1px solid #3d3d3d;")
        self.layout.addWidget(self.log_area)

        self.update_tool_list()

    def update_tool_list(self):
        cat = self.cat_combo.currentText()
        self.tool_combo.clear()
        self.tool_combo.addItems(self.tools.get(cat, []))

    def start_op(self):
        target = self.target_input.text().strip()
        tool = self.tool_combo.currentText()
        if not target: return

        self.log_area.appendPlainText(f"\n[!] Initializing {tool} for {target}...")
        self.log_area.appendPlainText("[*] Establishing secure connection to security plane...")
        time.sleep(1)
        self.log_area.appendPlainText("[*] Fetching policy baseline and configuration...")
        self.log_area.appendPlainText(f"[+] {tool} operation initiated successfully.")
        self.log_area.appendPlainText(f"[INFO] Monitoring {target} for security anomalies...")
        
        # Log to Audit
        from core.db import db_manager
        db_manager.log_action("Blue Team Operation", f"Tool: {tool} | Target: {target}")

    def refresh_projects(self):
        pass # For main window interface compatibility
