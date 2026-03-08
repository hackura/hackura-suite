from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView, QFrame
)
from PySide6.QtCore import Qt
from core.compliance_engine import ComplianceEngine
import os

class ComplianceView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(40, 40, 40, 40)
        self.layout.setSpacing(20)

        header = QLabel("Regulatory Compliance Auditor")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #ffaa00;")
        self.layout.addWidget(header)

        # Audit Config
        config_frame = QFrame()
        config_frame.setStyleSheet("background-color: #2b2b2b; border: 1px solid #3d3d3d; border-radius: 8px;")
        config_layout = QVBoxLayout(config_frame)
        
        self.target_url = QLineEdit()
        self.target_url.setPlaceholderText("Target Domain or URL (e.g., https://example.com.gh)")
        self.target_url.setFixedHeight(35)
        config_layout.addWidget(QLabel("Audit Target:"))
        config_layout.addWidget(self.target_url)

        self.run_btn = QPushButton("RUN COMPLIANCE AUDIT (GHANA DPA)")
        self.run_btn.setFixedHeight(45)
        self.run_btn.setStyleSheet("background-color: #ffaa00; color: black; font-weight: bold;")
        self.run_btn.clicked.connect(self.run_audit)
        config_layout.addWidget(self.run_btn)

        self.clear_btn = QPushButton("CLEAR RESULTS")
        self.clear_btn.clicked.connect(self.clear_results)
        config_layout.addWidget(self.clear_btn)

        self.layout.addWidget(config_frame)

        # Results Summary
        self.score_lbl = QLabel("Audit Score: - / -")
        self.score_lbl.setStyleSheet("font-size: 18px; font-weight: bold; color: #f0f0f0;")
        self.layout.addWidget(self.score_lbl)

        # Results Table
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["ID", "Requirement", "Status", "Detail"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setStyleSheet("background-color: #1a1a1a; gridline-color: #333;")
        self.layout.addWidget(self.table)

    def run_audit(self):
        url = self.target_url.text().strip()
        if not url: return

        rule_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "compliance", "ghana_dpa.yaml")
        engine = ComplianceEngine(rule_path)
        
        results = engine.audit_target(url)
        
        if "error" in results:
            self.score_lbl.setText(f"Audit Error: {results['error']}")
            return

        self.score_lbl.setText(f"Audit Score: {results['score']} / {results['max_score']}")
        
        self.table.setRowCount(0)
        for f in results['findings']:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            self.table.setItem(row, 0, QTableWidgetItem(f['id']))
            self.table.setItem(row, 1, QTableWidgetItem(f['section']))
            
            status = "PASSED" if f['passed'] else "FAILED"
            status_item = QTableWidgetItem(status)
            if f['passed']:
                status_item.setForeground(Qt.green)
            else:
                status_item.setForeground(Qt.red)
            
            self.table.setItem(row, 2, status_item)
            self.table.setItem(row, 3, QTableWidgetItem(f['detail']))

    def clear_results(self):
        self.table.setRowCount(0)
        self.score_lbl.setText("Audit Score: - / -")

    def refresh_projects(self): pass
