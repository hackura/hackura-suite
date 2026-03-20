from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QHeaderView, QLineEdit, QTableWidgetItem
from PySide6.QtCore import Qt

class IntelligenceBaseView(QWidget):
    def __init__(self, title):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(40, 40, 40, 40)
        
        header = QLabel(title)
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #00ccff;")
        self.layout.addWidget(header)
        
        # Search Input
        search_layout = QHBoxLayout()
        self.target_input = QLineEdit()
        self.target_input.setPlaceholderText("Enter target (email, domain, or IP)...")
        self.target_input.setFixedHeight(40)
        self.target_input.setStyleSheet("background-color: #2b2b2b; border: 1px solid #3d3d3d; border-radius: 4px; padding-left: 15px;")
        
        self.search_btn = QPushButton("RUN INTELLIGENCE SCAN")
        self.search_btn.setFixedHeight(40)
        self.search_btn.setStyleSheet("background-color: #00ccff; color: black; font-weight: bold; padding: 0 20px;")
        self.search_btn.clicked.connect(self.run_intelligence_scan)
        
        search_layout.addWidget(self.target_input)
        search_layout.addWidget(self.search_btn)
        self.layout.addLayout(search_layout)
        
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Target", "Intelligence Data", "Severity/Source"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setStyleSheet("background-color: #1a1a1a; gridline-color: #333;")
        self.layout.addWidget(self.table)
        
        self.clear_btn = QPushButton("CLEAR SESSION")
        self.clear_btn.setFixedHeight(35)
        self.clear_btn.setStyleSheet("background-color: #333; color: #aaa; font-weight: bold;")
        self.clear_btn.clicked.connect(lambda: self.table.setRowCount(0))
        self.layout.addWidget(self.clear_btn)

    def run_intelligence_scan(self):
        target = self.target_input.text().strip()
        if not target: return
        
        # Simulate results
        import random
        sources = ["HaveIBeenPwned", "LeakCheck", "Scylla.sh", "DeHashed", "IntelX"]
        data_types = ["Password Leak", "Personal Data", "Financial Info", "PII Exposure"]
        
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(target))
        self.table.setItem(row, 1, QTableWidgetItem(random.choice(data_types)))
        self.table.setItem(row, 2, QTableWidgetItem(random.choice(sources)))

    def refresh_projects(self): pass

class BreachSearchView(IntelligenceBaseView):
    def __init__(self):
        super().__init__("Breach Search & Data Leak Audit")

class DarkWebScanView(IntelligenceBaseView):
    def __init__(self):
        super().__init__("Dark Web Surface Monitoring")
