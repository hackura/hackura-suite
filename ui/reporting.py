from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QComboBox, QTextEdit, QMessageBox, QFrame, QFileDialog
)
from core.db import db_manager
from core.report_engine import report_engine
import os

class ReportingView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(40, 40, 40, 40)

        header = QLabel("Professional Report Generator")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #00ccff;")
        self.layout.addWidget(header)

        # Selection Group
        select_frame = QFrame()
        select_frame.setObjectName("ReportingFrame")
        select_layout = QVBoxLayout(select_frame)
        select_layout.setContentsMargins(20, 20, 20, 20)
        
        lbl = QLabel("Select Engagement for Report:")
        lbl.setStyleSheet("font-weight: bold; color: #aaa;")
        select_layout.addWidget(lbl)
        
        self.project_combo = QComboBox()
        self.project_combo.setFixedHeight(35)
        self.project_combo.addItem("Loading Projects...", None)
        select_layout.addWidget(self.project_combo)
        
        self.info_lbl = QLabel("Note: Reports use the new ReportLab engine with automatic word wrapping and professional layout.")
        self.info_lbl.setWordWrap(True)
        self.info_lbl.setStyleSheet("color: #666; font-size: 11px; font-style: italic;")
        select_layout.addWidget(self.info_lbl)

        self.gen_btn = QPushButton("🚀 GENERATE PROFESSIONAL PDF REPORT")
        self.gen_btn.setFixedHeight(50)
        self.gen_btn.setStyleSheet("background-color: #00ccff; color: black; font-weight: bold; font-size: 14px;")
        self.gen_btn.clicked.connect(self.generate_report)
        select_layout.addWidget(self.gen_btn)
        
        self.layout.addWidget(select_frame)
        
        # Initial refresh
        self.refresh_projects()
        self.layout.addStretch()

    def refresh_projects(self):
        self.project_combo.clear()
        conn = db_manager.get_connection()
        projs = conn.execute("""
            SELECT p.id, p.name, c.name as client_name 
            FROM projects p 
            LEFT JOIN clients c ON p.client_id = c.id
        """).fetchall()
        
        if not projs:
            self.project_combo.addItem("NO PROJECTS AVAILABLE", None)
            return

        for p in projs:
            client_prefix = f"{p['client_name']} - " if p['client_name'] else ""
            self.project_combo.addItem(f"{client_prefix}{p['name']}", p['id'])

    def generate_report(self):
        project_id = self.project_combo.currentData()
        if not project_id: return
        
        # Open save dialog
        default_name = f"Report_{self.project_combo.currentText().replace(' ', '_')}.pdf"
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Report", default_name, "PDF Files (*.pdf)")
        
        if not file_path:
            return

        try:
            result = report_engine.generate_pdf(project_id, file_path)
            
            if result.get("success"):
                db_manager.log_action("Report Generated", f"Project ID: {project_id} | Path: {file_path}")
                QMessageBox.information(self, "Success", f"Professional report generated successfully at:\n{file_path}")
            else:
                QMessageBox.critical(self, "Error", f"Failed to generate report: {result.get('error')}")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {str(e)}")
