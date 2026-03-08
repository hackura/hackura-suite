from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView, QFrame, QDateEdit
)
from PySide6.QtCore import Qt, QDate
from core.db import db_manager

class EngagementTrackerView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(40, 40, 40, 40)
        self.layout.setSpacing(20)

        header = QLabel("Engagement & CRM Tracker")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #ff00ff;")
        self.layout.addWidget(header)

        # New Engagement Frame
        form_frame = QFrame()
        form_frame.setStyleSheet("background-color: #2b2b2b; border: 1px solid #3d3d3d; border-radius: 8px;")
        form_layout = QVBoxLayout(form_frame)
        
        self.client_input = QLineEdit()
        self.client_input.setPlaceholderText("Client Name")
        self.scope_input = QLineEdit()
        self.scope_input.setPlaceholderText("Engagement Scope (e.g. External Infrastructure)")
        
        self.deadline_input = QDateEdit()
        self.deadline_input.setDate(QDate.currentDate().addDays(14))
        self.deadline_input.setCalendarPopup(True)
        
        self.budget_input = QLineEdit()
        self.budget_input.setPlaceholderText("Budget / Rate (GH₵)")

        form_layout.addWidget(QLabel("Client:"))
        form_layout.addWidget(self.client_input)
        form_layout.addWidget(QLabel("Scope:"))
        form_layout.addWidget(self.scope_input)
        form_layout.addWidget(QLabel("Deadline:"))
        form_layout.addWidget(self.deadline_input)
        form_layout.addWidget(QLabel("Budget (GH₵):"))
        form_layout.addWidget(self.budget_input)
        
        self.add_btn = QPushButton("CREATE NEW ENGAGEMENT")
        self.add_btn.setStyleSheet("background-color: #ff00ff; color: white; font-weight: bold;")
        self.add_btn.clicked.connect(self.add_engagement)
        form_layout.addWidget(self.add_btn)

        self.layout.addWidget(form_frame)

        # Active Engagements Table
        self.layout.addWidget(QLabel("Active Engagements:"))
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Client", "Scope", "Deadline", "Budget", "Status"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setStyleSheet("background-color: #1a1a1a;")
        self.layout.addWidget(self.table)
        
        # Load initial data
        self.refresh_table()

    def add_engagement(self):
        client = self.client_input.text()
        scope = self.scope_input.text()
        deadline = self.deadline_input.date().toString(Qt.ISODate)
        budget = self.budget_input.text()
        
        if not client or not scope: return
        
        # In a real app, this would be a dedicated table. Here we reuse projects if needed or just simulate.
        # For now, let's just add to UI to show functionality
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(client))
        self.table.setItem(row, 1, QTableWidgetItem(scope))
        self.table.setItem(row, 2, QTableWidgetItem(deadline))
        self.table.setItem(row, 3, QTableWidgetItem(f"GH₵ {budget}"))
        self.table.setItem(row, 4, QTableWidgetItem("Active"))

        db_manager.log_action("Engagement Created", f"Client: {client} | Scope: {scope}")
        self.client_input.clear()
        self.scope_input.clear()

    def refresh_table(self):
        # Mock load
        data = [
            ("SRI Holdings", "Full Cloud Audit", "2026-03-20", "15,000", "In Progress"),
            ("Tonaton Clone", "API Pentest", "2026-03-15", "8,000", "Critical Findings")
        ]
        self.table.setRowCount(0)
        for c, s, d, b, st in data:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(c))
            self.table.setItem(row, 1, QTableWidgetItem(s))
            self.table.setItem(row, 2, QTableWidgetItem(d))
            self.table.setItem(row, 3, QTableWidgetItem(f"GH₵ {b}"))
            self.table.setItem(row, 4, QTableWidgetItem(st))

    def refresh_projects(self): pass
