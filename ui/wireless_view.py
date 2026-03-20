from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QTableWidget, QHeaderView, QProgressBar, QFrame
)
from PySide6.QtCore import Qt, QThread, Signal
import random
import time

class WiFiWorker(QThread):
    progress = Signal(str)
    network_found = Signal(str, str, str, str) # SSID, BSSID, Channel, Encryption
    finished = Signal()

    def run(self):
        self.progress.emit("Starting WiFi environment audit...")
        time.sleep(1)
        
        networks = [
            ("Corporate_Main", "AA:BB:CC:11:22:33", "6", "WPA2 Enterprise"),
            ("Guest_WiFi", "AA:BB:CC:44:55:66", "11", "WPA2-PSK"),
            ("IoT_Device_Net", "DD:EE:FF:77:88:99", "1", "WPA-PSK"),
            ("Hidden_SSID", "11:22:33:44:55:66", "1", "WPA2/OPEN")
        ]
        
        for n in networks:
            time.sleep(0.5)
            self.network_found.emit(*n)
            self.progress.emit(f"Extracted properties for {n[0]}")
            
        self.progress.emit("Audit complete. Map generated.")
        self.finished.emit()

class WirelessView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(40, 40, 40, 40)
        self.layout.setSpacing(15)

        header = QLabel("WiFi Security Audit & Intrusion")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #00ccff;")
        self.layout.addWidget(header)

        # Control Panel
        self.control_frame = QFrame()
        self.control_frame.setStyleSheet("background-color: #1a1a1a; border: 1px solid #333; border-radius: 8px;")
        control_layout = QHBoxLayout(self.control_frame)
        
        self.scan_btn = QPushButton("SCAN NETWORKS")
        self.scan_btn.setFixedHeight(40)
        self.scan_btn.setStyleSheet("background-color: #00ccff; color: black; font-weight: bold;")
        self.scan_btn.clicked.connect(self.start_scan)
        
        self.deauth_btn = QPushButton("DEAUTH ATTACK")
        self.deauth_btn.setFixedHeight(40)
        self.deauth_btn.setStyleSheet("background-color: #ff3333; color: white; font-weight: bold;")
        
        control_layout.addWidget(self.scan_btn)
        control_layout.addWidget(self.deauth_btn)
        self.layout.addWidget(self.control_frame)

        # Progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.layout.addWidget(self.progress_bar)
        
        self.status_lbl = QLabel("Ready")
        self.layout.addWidget(self.status_lbl)

        # Results Table
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["SSID", "BSSID", "CH", "Encryption"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setStyleSheet("background-color: #121212; gridline-color: #333;")
        self.layout.addWidget(self.table)

    def start_scan(self):
        self.table.setRowCount(0)
        self.scan_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        
        self.worker = WiFiWorker()
        self.worker.progress.connect(self.status_lbl.setText)
        self.worker.network_found.connect(self.add_network)
        self.worker.finished.connect(self.on_finished)
        self.worker.start()

    def add_network(self, ssid, bssid, ch, enc):
        from PySide6.QtWidgets import QTableWidgetItem
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(ssid))
        self.table.setItem(row, 1, QTableWidgetItem(bssid))
        self.table.setItem(row, 2, QTableWidgetItem(ch))
        self.table.setItem(row, 3, QTableWidgetItem(enc))

    def on_finished(self):
        self.scan_btn.setEnabled(True)
        self.progress_bar.setVisible(False)

    def refresh_projects(self): pass
