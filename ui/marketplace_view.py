from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QFrame, QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit
)
from PySide6.QtCore import Qt

class PluginMarketplaceView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(40, 40, 40, 40)
        self.layout.setSpacing(20)

        header = QLabel("Internal Plugin Marketplace")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #ff00ff;")
        self.layout.addWidget(header)

        # Marketplace List
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Plugin Name", "Category", "Rating", "Status"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setStyleSheet("background-color: #1a1a1a;")
        self.layout.addWidget(self.table)
        
        # Actions
        btn_layout = QHBoxLayout()
        self.upload_btn = QPushButton("UPLOAD CUSTOM PLUGIN")
        self.refresh_btn = QPushButton("REFRESH MARKETPLACE")
        self.refresh_btn.clicked.connect(self.load_plugins)
        
        btn_layout.addWidget(self.upload_btn)
        btn_layout.addWidget(self.refresh_btn)
        self.layout.addLayout(btn_layout)
        
        self.load_plugins()

    def load_plugins(self):
        # Mocking marketplace data for Phase 3
        plugins = [
            ("MoMo-Phisher-v2", "Social Engineering", "⭐⭐⭐⭐⭐", "Installed"),
            ("Tonaton-Scanner", "Vulnerability Research", "⭐⭐⭐⭐", "Available"),
            ("Jumia-Order-Checker", "E-commerce Tools", "⭐⭐⭐⭐⭐", "Installed"),
            ("Melcloud-Auditor-Pro", "Cloud Security", "⭐⭐⭐⭐⭐", "Update Available")
        ]
        
        self.table.setRowCount(0)
        for name, cat, rate, status in plugins:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(name))
            self.table.setItem(row, 1, QTableWidgetItem(cat))
            self.table.setItem(row, 2, QTableWidgetItem(rate))
            self.table.setItem(row, 3, QTableWidgetItem(status))

    def refresh_projects(self): pass
