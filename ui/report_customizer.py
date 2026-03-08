from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QLineEdit, QComboBox, QPlainTextEdit, QFileDialog, QFrame
)
from PySide6.QtCore import Qt
from core.report_engine import report_engine
from core.db import db_manager
import os

class ReportCustomizerView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(40, 40, 40, 40)
        self.layout.setSpacing(20)

        header = QLabel("Report Customizer")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #00ccff;")
        self.layout.addWidget(header)

        # Config Frame
        config_frame = QFrame()
        config_frame.setStyleSheet("background-color: #2b2b2b; border: 1px solid #3d3d3d; border-radius: 8px;")
        config_layout = QVBoxLayout(config_frame)
        
        self.project_combo = QComboBox()
        self.project_combo.setFixedHeight(35)
        self.refresh_projects()
        config_layout.addWidget(QLabel("Select Project:"))
        config_layout.addWidget(self.project_combo)

        self.template_combo = QComboBox()
        self.template_combo.addItems(["ghana-smb", "professional-fintech", "compliance-lite"])
        self.template_combo.setFixedHeight(35)
        config_layout.addWidget(QLabel("Select Template:"))
        config_layout.addWidget(self.template_combo)

        self.layout.addWidget(config_frame)

        # Branding
        branding_frame = QFrame()
        branding_frame.setStyleSheet("background-color: #1a1a1a; border: 1px solid #333; border-radius: 8px;")
        branding_layout = QVBoxLayout(branding_frame)
        
        self.logo_path_input = QLineEdit()
        self.logo_path_input.setPlaceholderText("Path to custom logo...")
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self.browse_logo)
        
        logo_layout = QHBoxLayout()
        logo_layout.addWidget(self.logo_path_input)
        logo_layout.addWidget(browse_btn)
        
        branding_layout.addWidget(QLabel("Custom Branding (Logo):"))
        branding_layout.addLayout(logo_layout)
        self.layout.addWidget(branding_frame)

        # Actions
        self.gen_btn = QPushButton("GENERATE PDF REPORT")
        self.gen_btn.setFixedHeight(50)
        self.gen_btn.setStyleSheet("background-color: #00ff00; color: black; font-weight: bold; font-size: 14px;")
        self.gen_btn.clicked.connect(self.run_generation)
        self.layout.addWidget(self.gen_btn)

        self.status_lbl = QLabel("Ready")
        self.status_lbl.setStyleSheet("color: #888;")
        self.layout.addWidget(self.status_lbl)
        
        self.layout.addStretch()

    def refresh_projects(self):
        self.project_combo.clear()
        conn = db_manager.get_connection()
        projs = conn.execute("SELECT id, name FROM projects").fetchall()
        for p in projs:
            self.project_combo.addItem(p['name'], p['id'])

    def browse_logo(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Logo", "", "Images (*.png *.jpg)")
        if path:
            self.logo_path_input.setText(path)

    def run_generation(self):
        project_id = self.project_combo.currentData()
        if not project_id: return
        
        save_path, _ = QFileDialog.getSaveFileName(self, "Save Report", f"report_{project_id}.pdf", "PDF Files (*.pdf)")
        if not save_path: return
        
        self.gen_btn.setEnabled(False)
        self.status_lbl.setText("Generating professional PDF...")
        
        template = self.template_combo.currentText()
        result = report_engine.generate_pdf(project_id, save_path, template)
        
        self.gen_btn.setEnabled(True)
        if result["success"]:
            self.status_lbl.setText(f"Success! Report saved to: {save_path}")
            db_manager.log_action("Report Generated", f"Project: {project_id} | Template: {template}")
        else:
            self.status_lbl.setText(f"Error: {result['error']}")
