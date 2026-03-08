import os
from jinja2 import Template
from fpdf import FPDF
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from core.db import db_manager

# --- Phase 3: New Report Engine (ReportLab & Jinja2) ---

class ReportEngine:
    def __init__(self, template_dir="data/templates"):
        self.template_dir = template_dir
        if not os.path.exists(self.template_dir):
            os.makedirs(self.template_dir)

    def generate_pdf(self, project_id, output_path, template_name="ghana-smb"):
        """Generates a professional PDF report for a given project using ReportLab."""
        conn = db_manager.get_connection()
        project = conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
        if not project:
            return {"success": False, "error": "Project not found"}

        findings = conn.execute("SELECT * FROM findings f JOIN scans s ON f.scan_id = s.id WHERE s.project_id = ?", (project_id,)).fetchall()
        
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []

        # Title Page
        elements.append(Paragraph(f"Security Assessment Report: {project['name']}", styles['Title']))
        elements.append(Spacer(1, 12))
        elements.append(Paragraph(f"Client: {project['client_id']}", styles['Normal']))
        elements.append(Paragraph(f"Date: {project['created_at']}", styles['Normal']))
        elements.append(Spacer(1, 48))

        # Executive Summary
        exec_summary_tpl = "The recent assessment of {{ project_name }} revealed {{ finding_count }} vulnerabilities. Overall risk posture is {{ risk_level }}."
        template = Template(exec_summary_tpl)
        risk_level = "High" if len(findings) > 5 else "Medium"
        summary_text = template.render(project_name=project['name'], finding_count=len(findings), risk_level=risk_level)
        
        elements.append(Paragraph("Executive Summary", styles['Heading1']))
        elements.append(Paragraph(summary_text, styles['Normal']))
        elements.append(Spacer(1, 24))

        # Ghana DPA Compliance
        elements.append(Paragraph("Ghana DPA Compliance Statement", styles['Heading2']))
        elements.append(Paragraph("This assessment was conducted with reference to the Data Protection Act, 2012 (Act 843).", styles['Italic']))
        elements.append(Spacer(1, 24))

        # Findings Table
        elements.append(Paragraph("Technical Findings", styles['Heading1']))
        data = [["ID", "Severity", "Finding", "Status"]]
        for i, f in enumerate(findings):
            data.append([str(i+1), f['severity'], f['title'], "Open"])

        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(table)

        doc.build(elements)
        return {"success": True, "path": output_path}

report_engine = ReportEngine()

# --- Retro-compatibility: Original HackuraReport (FPDF) ---

class HackuraReport(FPDF):
    def __init__(self, client_name="Unknown Client", logo_path=None):
        super().__init__()
        self.client_name = client_name
        self.logo_path = logo_path
        self.sections = []

    def create_title_page(self, project_name):
        self.add_page()
        self.set_font('helvetica', 'B', 24)
        self.ln(60)
        self.cell(0, 20, "Security Assessment Report", ln=True, align='C')
        self.set_font('helvetica', '', 18)
        self.cell(0, 15, f"Project: {project_name}", ln=True, align='C')
        self.ln(10)
        self.cell(0, 10, f"Client: {self.client_name}", ln=True, align='C')
        self.ln(40)
        if self.logo_path and os.path.exists(self.logo_path):
            self.image(self.logo_path, x=80, w=50)

    def add_section(self, title, page_no):
        self.sections.append((title, page_no))
        self.add_page()

    def add_chart(self, title, chart_path):
        self.set_font('helvetica', 'B', 14)
        self.cell(0, 10, title, ln=True)
        if os.path.exists(chart_path):
            self.image(chart_path, w=170)
        self.ln(10)

    def add_finding_card(self, title, severity, desc, mitigation, owasp):
        self.set_font('helvetica', 'B', 12)
        # Severity-based coloring
        colors = {'Critical': (139, 0, 0), 'High': (255, 69, 0), 'Medium': (218, 165, 32), 'Low': (46, 139, 87)}
        color = colors.get(severity.capitalize(), (70, 130, 180))
        
        self.set_text_color(*color)
        self.cell(0, 10, f"[{severity.upper()}] {title}", ln=True)
        self.set_text_color(0, 0, 0)
        
        self.set_font('helvetica', 'B', 10)
        self.cell(0, 7, f"OWASP Category: {owasp}", ln=True)
        self.set_font('helvetica', '', 10)
        self.multi_cell(0, 6, f"Description: {desc}")
        self.ln(2)
        self.set_font('helvetica', 'I', 10)
        self.multi_cell(0, 6, f"Mitigation Strategy: {mitigation}")
        self.ln(10)

    def add_signoff(self):
        self.add_page()
        self.set_font('helvetica', 'B', 16)
        self.cell(0, 10, "3. Final Sign-off", ln=True)
        self.set_font('helvetica', '', 11)
        self.ln(20)
        self.cell(80, 10, "Approved By: ____________________", ln=False)
        self.cell(0, 10, "Date: ____________________", ln=True)
        self.ln(10)
        self.cell(0, 10, "Hackura Consult Offensive Security Division", ln=True)
