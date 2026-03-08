from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QPlainTextEdit, QFrame, QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit
)
from PySide6.QtCore import Qt
from core.db import db_manager

class LogAnalyzerView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(40, 40, 40, 40)
        self.layout.setSpacing(20)

        header = QLabel("Centralized Log Aggregator & Analyzer")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #00ccff;")
        self.layout.addWidget(header)

        # Search
        search_frame = QFrame()
        search_frame.setStyleSheet("background-color: #2b2b2b; border: 1px solid #3d3d3d; border-radius: 8px;")
        search_layout = QHBoxLayout(search_frame)
        
        self.query_input = QLineEdit()
        self.query_input.setPlaceholderText("Query logs (e.g. 'SSH brute force', 'XSS 200', 'Ghana SMB')...")
        self.search_btn = QPushButton("SEARCH LOGS")
        self.search_btn.setStyleSheet("background-color: #00ccff; color: black; font-weight: bold;")
        self.search_btn.clicked.connect(self.run_search)
        
        search_layout.addWidget(self.query_input)
        search_layout.addWidget(self.search_btn)
        self.layout.addWidget(search_frame)

        # Logs Table
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Timestamp", "Action", "Details"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setStyleSheet("background-color: #1a1a1a; gridline-color: #333;")
        self.layout.addWidget(self.table)
        
        self.refresh_logs()

    def refresh_logs(self):
        self.table.setRowCount(0)
        conn = db_manager.get_connection()
        logs = conn.execute("SELECT created_at, action, details FROM audit_logs ORDER BY created_at DESC LIMIT 50").fetchall()
        
        for l in logs:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(l['created_at'])))
            self.table.setItem(row, 1, QTableWidgetItem(l['action']))
            self.table.setItem(row, 2, QTableWidgetItem(l['details']))

    def run_search(self):
        query = self.query_input.text().strip()
        if not query:
            self.refresh_logs()
            return
            
        self.table.setRowCount(0)
        conn = db_manager.get_connection()
        # Simple LIKE search for the PoC
        logs = conn.execute(
            "SELECT created_at, action, details FROM audit_logs WHERE action LIKE ? OR details LIKE ? ORDER BY created_at DESC",
            (f"%{query}%", f"%{query}%")
        ).fetchall()
        
        for l in logs:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(l['created_at'])))
            self.table.setItem(row, 1, QTableWidgetItem(l['action']))
            self.table.setItem(row, 2, QTableWidgetItem(l['details']))

    def refresh_projects(self): 
        self.refresh_logs()
