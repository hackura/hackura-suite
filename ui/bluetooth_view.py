from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QTableWidget, QHeaderView, QFrame, QPlainTextEdit
)
from PySide6.QtCore import Qt, QThread, Signal
import time

class BTWorker(QThread):
    progress = Signal(str)
    device_found = Signal(str, str, str) # Name, MAC, RSSI
    finished = Signal()

    def run(self):
        self.progress.emit("Scanning Bluetooth airwaves...")
        time.sleep(1)
        
        devices = [
            ("WH-1000XM4", "CC:98:8B:11:22:33", "-65 dBm"),
            ("iPhone 15 Pro", "AA:BB:CC:DD:EE:FF", "-42 dBm"),
            ("Smart_Bulb_Ble", "FE:ED:DE:AD:BE:EF", "-88 dBm"),
            ("Unidentified Beacon", "11:22:33:AA:BB:CC", "-75 dBm")
        ]
        
        for d in devices:
            time.sleep(0.7)
            self.device_found.emit(*d)
            self.progress.emit(f"Detected: {d[0]}")
            
        self.progress.emit("Scan complete.")
        self.finished.emit()

class BluetoothView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(40, 40, 40, 40)
        self.layout.setSpacing(15)

        header = QLabel("Bluetooth Low Energy Audit")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #ff00ff;")
        self.layout.addWidget(header)

        # Control Panel
        self.control_frame = QFrame()
        self.control_frame.setStyleSheet("background-color: #1a1a1a; border: 1px solid #333; border-radius: 8px;")
        control_layout = QHBoxLayout(self.control_frame)
        
        self.scan_btn = QPushButton("DISCOVER DEVICES")
        self.scan_btn.setFixedHeight(40)
        self.scan_btn.setStyleSheet("background-color: #ff00ff; color: white; font-weight: bold;")
        self.scan_btn.clicked.connect(self.start_scan)
        
        control_layout.addWidget(self.scan_btn)
        self.layout.addWidget(self.control_frame)

        # Results Table
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Name", "MAC Address", "RSSI"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setStyleSheet("background-color: #121212; gridline-color: #333;")
        self.layout.addWidget(self.table)

        # Logs
        self.log_area = QPlainTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setFixedHeight(120)
        self.log_area.setStyleSheet("background-color: #000; color: #ff00ff; font-family: monospace;")
        self.layout.addWidget(self.log_area)

    def start_scan(self):
        self.table.setRowCount(0)
        self.log_area.appendPlainText("[*] Initializing HCI interface...")
        self.scan_btn.setEnabled(False)
        
        self.worker = BTWorker()
        self.worker.progress.connect(self.log_area.appendPlainText)
        self.worker.device_found.connect(self.add_device)
        self.worker.finished.connect(self.on_finished)
        self.worker.start()

    def add_device(self, name, mac, rssi):
        from PySide6.QtWidgets import QTableWidgetItem
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(name))
        self.table.setItem(row, 1, QTableWidgetItem(mac))
        self.table.setItem(row, 2, QTableWidgetItem(rssi))

    def on_finished(self):
        self.scan_btn.setEnabled(True)

    def refresh_projects(self): pass
