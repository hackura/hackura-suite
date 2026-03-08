from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView, QFrame, QComboBox
)
from PySide6.QtCore import Qt
from core.db import db_manager

class AssetTrackerView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(40, 40, 40, 40)
        self.layout.setSpacing(20)

        header = QLabel("Enterprise Asset Inventory")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #00ff7f;")
        self.layout.addWidget(header)

        # Filters and Controls
        control_frame = QFrame()
        control_frame.setStyleSheet("background-color: #2b2b2b; border: 1px solid #3d3d3d; border-radius: 8px;")
        control_layout = QHBoxLayout(control_frame)
        
        self.project_filter = QComboBox()
        self.project_filter.setPlaceholderText("Filter by Project")
        self.refresh_projects()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search assets (IP, OS, Name)...")
        
        self.export_btn = QPushButton("EXPORT INVENTORY")
        self.export_btn.setStyleSheet("background-color: #00ff7f; color: black; font-weight: bold;")
        
        control_layout.addWidget(self.project_filter)
        control_layout.addWidget(self.search_input)
        control_layout.addWidget(self.export_btn)
        self.layout.addWidget(control_frame)

        # Asset Table
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Asset Name", "IP Address", "OS/Type", "First Seen", "Project"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setStyleSheet("background-color: #1a1a1a; gridline-color: #333;")
        self.layout.addWidget(self.table)
        
        # Load data
        self.load_assets()

    def refresh_projects(self):
        self.project_filter.clear()
        self.project_filter.addItem("ALL PROJECTS", None)
        conn = db_manager.get_connection()
        projs = conn.execute("SELECT id, name FROM projects").fetchall()
        for p in projs:
            self.project_filter.addItem(p['name'], p['id'])

    def load_assets(self):
        # In a real impl, this would query a dedicated 'assets' table or aggregate from 'scans'
        # Mocking data for Phase 3 PoC
        mock_assets = [
            ("GH-MAIN-DC", "192.168.1.10", "Windows Server 2022", "2026-03-01", "Core Infrastructure"),
            ("Tonaton-API-GW", "10.0.0.50", "Ubuntu 22.04 (Nginx)", "2026-03-04", "Tonaton Clone"),
            ("Melcloud-S3-Prod", "melcloud.gh/prod", "Object Storage", "2026-03-04", "Cloud Audit")
        ]
        
        self.table.setRowCount(0)
        for name, ip, os_type, seen, proj in mock_assets:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(name))
            self.table.setItem(row, 1, QTableWidgetItem(ip))
            self.table.setItem(row, 2, QTableWidgetItem(os_type))
            self.table.setItem(row, 3, QTableWidgetItem(seen))
            self.table.setItem(row, 4, QTableWidgetItem(proj))

    def refresh_projects_list(self): # For main_window interface consistency
        self.refresh_projects()
        self.load_assets()
