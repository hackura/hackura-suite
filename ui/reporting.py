from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QComboBox, QTextEdit, QMessageBox, QFrame
)
from core.db import db_manager
from core.report_engine import HackuraReport
import os
import matplotlib.pyplot as plt
from io import BytesIO

class ReportingView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(40, 40, 40, 40)

        header = QLabel("Consultancy Report Generator")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #00ccff;")
        self.layout.addWidget(header)

        # Selection Group
        select_frame = QFrame()
        select_frame.setObjectName("ReportingFrame")
        select_layout = QVBoxLayout(select_frame)
        select_layout.setContentsMargins(20, 20, 20, 20)
        
        lbl = QLabel("Select Target Project:")
        lbl.setStyleSheet("font-weight: bold;")
        select_layout.addWidget(lbl)
        
        self.project_combo = QComboBox()
        self.project_combo.setFixedHeight(35)
        # Placeholder while loading
        self.project_combo.addItem("Loading Projects...", None)
        select_layout.addWidget(self.project_combo)
        
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
            client_prefix = f"{p['client_name']} - " if p['client_name'] else "Unknown Client - "
            self.project_combo.addItem(f"{client_prefix}{p['name']}", p['id'])

    def generate_report(self):
        project_id = self.project_combo.currentData()
        if not project_id: return
        
        try:
            conn = db_manager.get_connection()
            # Fetch Project and Client Details
            project = conn.execute("""
                SELECT p.name, c.name as client_name, c.logo_path 
                FROM projects p 
                JOIN clients c ON p.client_id = c.id 
                WHERE p.id = ?
            """, (project_id,)).fetchone()
            
            # Fetch Findings
            findings = conn.execute("""
                SELECT f.title, f.severity, f.description, s.type as scan_type
                FROM findings f
                JOIN scans s ON f.scan_id = s.id
                WHERE s.project_id = ?
            """, (project_id,)).fetchall()
            
            report_dir = os.path.join(os.path.expanduser("~"), "HackuraSuite", "reports")
            report_path = os.path.join(report_dir, f"Report_{project['name'].replace(' ', '_')}.pdf")
            os.makedirs(report_dir, exist_ok=True)
            
            pdf = HackuraReport(project['client_name'], project['logo_path'])
            pdf.create_title_page(project['name'])
            
            # 1. Executive Summary Section
            pdf.add_section("Executive Summary", pdf.page_no())
            pdf.set_font('helvetica', 'B', 16)
            pdf.set_text_color(0, 51, 102)
            pdf.cell(0, 10, "1. Executive Summary", ln=True)
            pdf.set_font('helvetica', '', 11)
            pdf.set_text_color(50, 50, 50)
            pdf.multi_cell(0, 8, f"This security assessment was authorized by {project['client_name']} and performed by the Hackura Consult Offensive Security Division. The objective was to identify and evaluate security vulnerabilities within the scoped environment for the {project['name']} engagement.")
            pdf.ln(10)
            
            # Risk Distribution Chart
            self.embed_risk_chart(pdf, findings)
            
            # 2. Detailed Security Findings Section
            pdf.add_section("Detailed Security Findings", pdf.page_no())
            pdf.set_font('helvetica', 'B', 16)
            pdf.set_text_color(0, 51, 102)
            pdf.cell(0, 10, "2. Detailed Security Findings", ln=True)
            pdf.ln(5)
            
            # Mapper for Tool-Specific Remediation & Compliance
            strategy_map = {
                "Nuclei": ("Remediate detected vulnerability by patching the underlying software or updating template-specific configurations.", "A06:2021-Vulnerable and Outdated Components"),
                "Subfinder": ("Implement strict DNS auditing. Minimize passive subdomain exposure manually by monitoring public certificate transparency logs.", "A01:2021-Broken Access Control"),
                "OSINT Hub": ("Enforce strict data privacy policies. Scrub sensitive host information from passive intelligence databases.", "A05:2021-Security Misconfiguration"),
                "Cloud Hunter": ("Enforce IAM policies and check Bucket ACLs for 'Public Read' access. Use private endpoints for cloud resources.", "A05:2021-Security Misconfiguration"),
                "Tech Fingerprint": ("Obfuscate server banners and minimize technical footprint to prevent stack-targeted exploitation.", "A05:2021-Security Misconfiguration"),
                "Defence Audit": ("Update EDR/AV policies to detect common probing techniques and improve telemetry coverage.", "A00:2021-Legacy/General")
            }

            for f in findings:
                title, severity, desc, scan_type = f
                # Use mapped data if available, else fallback
                mitigation, owasp = strategy_map.get(scan_type, (
                    "Standard security hardening and patch management should be applied. Refer to vendor-specific documentation.",
                    "A01:2021-Broken Access Control"
                ))
                pdf.add_finding_card(title, severity, desc, mitigation, owasp)
            
            pdf.add_signoff()
            
            # Finalize: Create TOC (simplified approach: we generate TOC at the end or just assume sections)
            # True TOC with fpdf requires a multi-pass approach or specific hacks. 
            # For now, we've added the sections to the internal list.
            
            pdf.output(report_path)

            db_manager.log_action("Report Generated", f"Project ID: {project_id} | Path: {report_path}")
            QMessageBox.information(self, "Success", f"Report generated:\n{report_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate report: {str(e)}")
            
    def embed_risk_chart(self, pdf, findings):
        if not findings: return
        
        # Aggregate severity counts
        counts = {'Critical': 0, 'High': 0, 'Medium': 0, 'Low': 0, 'Info': 0}
        for f in findings:
            sev = f[1].capitalize()
            if sev in counts:
                counts[sev] += 1
            else:
                counts['Info'] += 1 # Fallback
            
        # Filter out zero counts for the chart but keep for legend if desired
        labels = [l for l in counts if counts[l] > 0]
        sizes = [counts[l] for l in labels]
        
        # Professional color palette
        colors_map = {
            'Critical': '#8B0000', # Dark Red
            'High': '#FF4500',     # Orange Red
            'Medium': '#DAA520',   # Goldenrod
            'Low': '#2E8B57',      # Sea Green
            'Info': '#4682B4'      # Steel Blue
        }
        c_list = [colors_map.get(l, '#808080') for l in labels]

        plt.figure(figsize=(10, 6))
        # Donut Chart
        wedges, texts, autotexts = plt.pie(
            sizes, 
            labels=labels, 
            colors=c_list, 
            autopct='%1.1f%%', 
            startangle=140, 
            pctdistance=0.85,
            wedgeprops=dict(width=0.4, edgecolor='w'),
            textprops={'color':"w", 'weight':'bold'}
        )
        
        # Center Circle for Donut
        centre_circle = plt.Circle((0,0), 0.70, fc='white')
        fig = plt.gcf()
        fig.gca().add_artist(centre_circle)
        
        # Legend at bottom right
        plt.legend(wedges, labels, title="Risk Severities", loc="lower right", bbox_to_anchor=(1, 0, 0.5, 1))
        
        plt.setp(autotexts, size=8, weight="bold")
        plt.axis('equal')
        plt.tight_layout()
        
        chart_path = os.path.join(os.path.expanduser("~"), "HackuraSuite", "reports", "temp_chart_pro.png")
        os.makedirs(os.path.dirname(chart_path), exist_ok=True)
        plt.savefig(chart_path, dpi=120, transparent=True)
        plt.close()
        
        pdf.add_chart("Executive Risk Distribution Analysis", chart_path)
        if os.path.exists(chart_path): os.remove(chart_path)

        # 1.3 Risk Mitigation Summary Table
        pdf.set_font('helvetica', 'B', 14)
        pdf.cell(0, 10, "1.3 Mitigation Coverage Summary", ln=True)
        pdf.set_font('helvetica', '', 10)
        
        # Summary description
        pdf.multi_cell(0, 7, "The following table summarizes the identified risks and the corresponding mitigation status. Our security team recommends immediate remediation for all Critical and High findings.")
        pdf.ln(5)
        
        # Table Header
        pdf.set_fill_color(0, 51, 102)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(60, 8, "Risk Category", 1, 0, 'C', True)
        pdf.cell(50, 8, "Total Findings", 1, 0, 'C', True)
        pdf.cell(80, 8, "Recommended Strategy", 1, 1, 'C', True)
        
        # Table Rows
        pdf.set_text_color(0, 0, 0)
        for sev, count in counts.items():
            if count > 0:
                pdf.cell(60, 8, sev, 1)
                pdf.cell(50, 8, str(count), 1, 0, 'C')
                strategy = "Immediate Fix" if sev in ['Critical', 'High'] else "Scheduled Patch"
                pdf.cell(80, 8, strategy, 1, 1, 'C')
        pdf.ln(10)

