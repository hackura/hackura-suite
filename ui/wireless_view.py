from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QLineEdit, QComboBox, QPlainTextEdit, QFrame, QTabWidget
)
from PySide6.QtCore import Qt
from core.wireless import WirelessAuditor

class WirelessView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(40, 40, 40, 40)
        self.layout.setSpacing(20)

        header = QLabel("Wireless & Bluetooth Auditor")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #ff00ff;")
        self.layout.addWidget(header)

        self.tabs = QTabWidget()
        self.setup_wifi_tab()
        self.setup_ble_tab()
        self.layout.addWidget(self.tabs)

        self.auditor = WirelessAuditor()

    def setup_wifi_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        self.bssid_input = QLineEdit()
        self.bssid_input.setPlaceholderText("Target BSSID (e.g., 00:11:22:33:44:55)")
        layout.addWidget(QLabel("Target BSSID:"))
        layout.addWidget(self.bssid_input)

        self.deauth_btn = QPushButton("LAUNCH DEAUTH CAMPAIGN")
        self.deauth_btn.setStyleSheet("background-color: #ff00ff; color: white; font-weight: bold;")
        self.deauth_btn.clicked.connect(self.run_deauth)
        layout.addWidget(self.deauth_btn)

        self.clear_wifi_btn = QPushButton("CLEAR LOGS")
        self.clear_wifi_btn.clicked.connect(lambda: self.wifi_logs.clear())
        layout.addWidget(self.clear_wifi_btn)
        
        self.wifi_logs = QPlainTextEdit()
        self.wifi_logs.setReadOnly(True)
        self.wifi_logs.setStyleSheet("background-color: #000; color: #00ff00; font-family: monospace;")
        layout.addWidget(self.wifi_logs)
        layout.addStretch()
        self.tabs.addTab(tab, "WiFi Auditor")

    def setup_ble_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        self.scan_ble_btn = QPushButton("DISCOVER BLE DEVICES")
        self.scan_ble_btn.setStyleSheet("background-color: #00ccff; color: black; font-weight: bold;")
        self.scan_ble_btn.clicked.connect(self.run_ble_scan)
        layout.addWidget(self.scan_ble_btn)

        self.clear_ble_btn = QPushButton("CLEAR LOGS")
        self.clear_ble_btn.clicked.connect(lambda: self.ble_logs.clear())
        layout.addWidget(self.clear_ble_btn)

        self.ble_logs = QPlainTextEdit()
        self.ble_logs.setReadOnly(True)
        self.ble_logs.setStyleSheet("background-color: #000; color: #00ccff; font-family: monospace;")
        layout.addWidget(self.ble_logs)
        layout.addStretch()
        self.tabs.addTab(tab, "BT/BLE Auditor")

    def run_deauth(self):
        bssid = self.bssid_input.text()
        if not bssid: return
        self.wifi_logs.appendPlainText(f"[*] Switching wlan0 to monitor mode...")
        self.wifi_logs.appendPlainText(f"[*] Injecting deauth frames to {bssid}...")
        self.auditor.start_deauth(bssid)
        self.wifi_logs.appendPlainText("[!] Operation persistent. Monitoring for handshakes...")

    def run_ble_scan(self):
        self.ble_logs.appendPlainText("[*] Initializing HCI interface for scanning...")
        devices = self.auditor.scan_ble()
        for d in devices:
            self.ble_logs.appendPlainText(f"[+] Found: {d['name']} ({d['mac']})")
            if d['vuln'] != "None":
                self.ble_logs.appendPlainText(f"    VULN: {d['vuln']}")

    def refresh_projects(self): pass
