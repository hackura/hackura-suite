from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QComboBox, QTableWidget, QTableWidgetItem, QHeaderView, QProgressBar, QMessageBox
)

from PySide6.QtCore import Qt, QThread
from core.cloud_audit import CloudAuditor
from core.db import db_manager

class AuditWorker(QThread):
    def __init__(self, provider, creds):
        super().__init__()
        self.auditor = CloudAuditor(provider, creds)

    def run(self):
        self.auditor.run()

class CloudView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(40, 40, 40, 40)

        header = QLabel("Cloud Infrastructure Audit")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #00ccff;")
        self.layout.addWidget(header)

        # Provider selection
        provider_layout = QHBoxLayout()
        
        self.project_combo = QComboBox()
        self.project_combo.setPlaceholderText("Select Project")
        self.project_combo.setFixedHeight(35)
        self.project_combo.setStyleSheet("background-color: #2b2b2b; border: 1px solid #3d3d3d;")
        self.refresh_projects()
        provider_layout.addWidget(self.project_combo)

        provider_layout.addWidget(QLabel("Select Provider:"))
        self.provider_combo = QComboBox()
        self.provider_combo.addItems(["AWS", "Azure", "GCP"])
        self.provider_combo.setFixedHeight(35)
        self.provider_combo.setStyleSheet("background-color: #2b2b2b; border: 1px solid #3d3d3d;")
        provider_layout.addWidget(self.provider_combo)
        
        self.audit_btn = QPushButton("RUN AUDIT")
        self.audit_btn.setFixedHeight(35)
        self.audit_btn.setStyleSheet("background-color: #00ccff; color: black; font-weight: bold; padding: 0 20px;")
        self.audit_btn.clicked.connect(self.start_audit)
        provider_layout.addWidget(self.audit_btn)
        provider_layout.addStretch()
        self.layout.addLayout(provider_layout)

        # Progress
        self.progress_label = QLabel("Ready")
        self.layout.addWidget(self.progress_label)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.layout.addWidget(self.progress_bar)

        # Findings Table
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Service", "Severity", "Finding"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setStyleSheet("background-color: #1e1e1e; color: #f0f0f0;")
        self.layout.addWidget(self.table)

    def refresh_projects(self):
        self.project_combo.clear()
        conn = db_manager.get_connection()
        projs = conn.execute("SELECT id, name FROM projects").fetchall()
        for p in projs:
            self.project_combo.addItem(p['name'], p['id'])
        if not projs:
            self.project_combo.addItem("NO ACTIVE PROJECTS", None)

    def start_audit(self):
        provider = self.provider_combo.currentText()
        
        # Project Guard
        self.current_project_id = self.project_combo.currentData()
        if not self.current_project_id:
            QMessageBox.warning(self, "Selection Required", "Please select a target project before starting the assessment.")
            return

        self.audit_btn.setEnabled(False)

        self.table.setRowCount(0)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0) # Indeterminate
        
        self.current_project_id = self.project_combo.currentData()
        
        # Log Scan
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO scans (project_id, type, target, status) VALUES (?, ?, ?, ?)",
            (self.current_project_id, "Cloud Audit", provider, "Running")
        )
        self.scan_id = cursor.lastrowid
        conn.commit()
        
        db_manager.log_action("Cloud Audit Started", f"Provider: {provider} | Scan ID: {self.scan_id}")

        self.worker = AuditWorker(provider, {}) # Empty creds for demo
        self.worker.auditor.progress.connect(lambda msg: self.progress_label.setText(msg))
        self.worker.auditor.finding_discovered.connect(self.add_finding)
        self.worker.auditor.finished.connect(self.on_finished)
        self.worker.start()

    def add_finding(self, finding):
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(finding["service"]))
        self.table.setItem(row, 1, QTableWidgetItem(finding["severity"]))
        self.table.setItem(row, 2, QTableWidgetItem(finding["description"]))
        
        # Save Finding
        conn = db_manager.get_connection()
        conn.execute(
            "INSERT INTO findings (scan_id, severity, title, description) VALUES (?, ?, ?, ?)",
            (self.scan_id, finding["severity"], finding["service"], finding["description"])
        )
        conn.commit()

    def on_finished(self):
        self.audit_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.progress_label.setText("Audit complete.")
        
        # Update Scan Status
        conn = db_manager.get_connection()
        conn.execute("UPDATE scans SET status = ? WHERE id = ?", ("Completed", self.scan_id))
        conn.commit()
