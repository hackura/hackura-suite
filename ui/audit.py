from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, 
    QHeaderView, QLabel, QPushButton
)
from core.db import db_manager

class SecurityAuditView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(40, 40, 40, 40)

        header = QLabel("Security Operations Audit Log")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #ff3333;")
        
        header_layout = QHBoxLayout()
        header_layout.addWidget(header)
        header_layout.addStretch()
        
        self.clear_btn = QPushButton("🗑 CLEAR AUDIT LOGS")
        self.clear_btn.setFixedSize(180, 35)
        self.clear_btn.setStyleSheet("background-color: #2b2b2b; color: #888; border: 1px solid #3d3d3d; font-weight: bold;")
        self.clear_btn.clicked.connect(self.clear_logs)
        header_layout.addWidget(self.clear_btn)
        
        self.layout.addLayout(header_layout)

        self.table = QTableWidget(0, 3)
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Timestamp", "Action", "Details"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setVisible(True)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #2b2b2b;
                gridline-color: #3d3d3d;
                color: #f0f0f0;
            }
            QHeaderView::section {
                background-color: #1e1e1e;
                color: #ff3333;
                padding: 10px;
                font-weight: bold;
                border: 1px solid #3d3d3d;
            }
        """)
        self.layout.addWidget(self.table)
        
        self.refresh_logs()

    def clear_logs(self):
        from PySide6.QtWidgets import QMessageBox
        reply = QMessageBox.question(self, 'Confirm Clear', 
                                    "Are you sure you want to permanently delete all audit logs?",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            conn = db_manager.get_connection()
            conn.execute("DELETE FROM audit_logs")
            conn.commit()
            db_manager.log_action("Audit Logs Cleared", "User wiped investigation history.")
            self.refresh_logs()

    def refresh_logs(self):
        self.table.setRowCount(0)
        conn = db_manager.get_connection()
        logs = conn.execute("SELECT created_at, action, details FROM audit_logs ORDER BY created_at DESC LIMIT 100").fetchall()
        for l in logs:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(l['created_at'])))
            self.table.setItem(row, 1, QTableWidgetItem(l['action']))
            self.table.setItem(row, 2, QTableWidgetItem(l['details']))
