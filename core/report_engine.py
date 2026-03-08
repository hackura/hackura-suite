import os
from jinja2 import Template
from fpdf import FPDF
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib import colors
from reportlab.lib.units import inch
from core.db import db_manager

class ReportEngine:
    def __init__(self, template_dir="data/templates"):
        self.template_dir = template_dir
        if not os.path.exists(self.template_dir):
            os.makedirs(self.template_dir)
        self.styles = getSampleStyleSheet()
        self._add_custom_styles()

    def _add_custom_styles(self):
        self.styles.add(ParagraphStyle(
            name='PremiumTitle',
            parent=self.styles['Title'],
            fontName='Helvetica-Bold',
            fontSize=28,
            textColor=colors.HexColor("#003366"),
            spaceAfter=30
        ))
        self.styles.add(ParagraphStyle(
            name='FindingTitle',
            parent=self.styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=14,
            textColor=colors.HexColor("#CC0000"),
            spaceBefore=12,
            spaceAfter=6
        ))
        self.styles.add(ParagraphStyle(
            name='FindingDesc',
            parent=self.styles['Normal'],
            fontName='Helvetica',
            fontSize=11,
            leading=14,
            alignment=0 # Left aligned
        ))

    def generate_pdf(self, project_id, output_path):
        """Generates a high-quality professional PDF using ReportLab."""
        conn = db_manager.get_connection()
        project = conn.execute("""
            SELECT p.name, c.name as client_name, c.logo_path, p.created_at 
            FROM projects p 
            JOIN clients c ON p.client_id = c.id 
            WHERE p.id = ?
        """, (project_id,)).fetchone()
        
        if not project:
            return {"success": False, "error": "Project not found"}

        findings = conn.execute("""
            SELECT f.title, f.severity, f.description, s.type as scan_type
            FROM findings f
            JOIN scans s ON f.scan_id = s.id
            WHERE s.project_id = ?
        """, (project_id,)).fetchall()
        
        doc = SimpleDocTemplate(output_path, pagesize=letter, 
                               rightMargin=72, leftMargin=72, 
                               topMargin=72, bottomMargin=18)
        elements = []

        # 1. Cover Page
        elements.append(Spacer(1, 2*inch))
        if project['logo_path'] and os.path.exists(project['logo_path']):
            try:
                img = Image(project['logo_path'], 2*inch, 2*inch)
                elements.append(img)
            except: pass
        
        elements.append(Spacer(1, 1*inch))
        elements.append(Paragraph(f"Security Assessment Report", self.styles['PremiumTitle']))
        elements.append(Paragraph(f"Engagement: {project['name']}", self.styles['Heading2']))
        elements.append(Paragraph(f"Client: {project['client_name']}", self.styles['Heading3']))
        elements.append(Paragraph(f"Date: {project['created_at']}", self.styles['Normal']))
        elements.append(PageBreak())

        # 2. Executive Summary
        elements.append(Paragraph("1. Executive Summary", self.styles['Heading1']))
        summary_text = (
            f"This comprehensive security assessment was conducted for {project['client_name']} "
            f"targeting the '{project['name']}' environment. Our assessment identified {len(findings)} "
            "vulnerability identifiers ranging across various severity levels."
        )
        elements.append(Paragraph(summary_text, self.styles['Normal']))
        elements.append(Spacer(1, 12))
        
        # Risk Table
        severity_counts = {'Critical': 0, 'High': 0, 'Medium': 0, 'Low': 0, 'Info': 0}
        for f in findings:
            s_key = f['severity'].capitalize()
            severity_counts[s_key] = severity_counts.get(s_key, 0) + 1
        
        data = [["Severity Level", "Count", "Recommended Action"]]
        for sev, count in severity_counts.items():
            action = "Immediate Remediation" if sev in ['Critical', 'High'] else "Scheduled Fix"
            data.append([sev, str(count), action])
            
        t = Table(data, colWidths=[1.5*inch, 1*inch, 2.5*inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#003366")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
        ]))
        elements.append(t)
        elements.append(Spacer(1, 24))

        # 3. Technical Findings (Word Wrap Active)
        elements.append(Paragraph("2. Technical Findings", self.styles['Heading1']))
        elements.append(Spacer(1, 12))

        for f in findings:
            elements.append(Paragraph(f"[{f['severity'].upper()}] {f['title']}", self.styles['FindingTitle']))
            # Word Wrap is handled naturally by Paragraph
            elements.append(Paragraph(f"<b>Description:</b> {f['description']}", self.styles['FindingDesc']))
            elements.append(Spacer(1, 12))

        doc.build(elements)
        return {"success": True, "path": output_path}

report_engine = ReportEngine()

# --- Legacy Wrapper for backwards compat ---
class HackuraReport(FPDF):
    def __init__(self, client_name="Unknown Client", logo_path=None):
        super().__init__()
        self.client_name = client_name
        self.logo_path = logo_path

    def create_title_page(self, project_name):
        self.add_page()
        self.set_font('helvetica', 'B', 24)
        self.ln(60)
        self.cell(0, 20, "Security Assessment Report", ln=True, align='C')
        self.set_font('helvetica', '', 18)
        self.cell(0, 15, f"Project: {project_name}", ln=True, align='C')

    def add_section(self, title, page_no): self.add_page()
    def add_chart(self, title, chart_path): pass
    def add_finding_card(self, title, severity, desc, mitigation, owasp):
        self.set_font('helvetica', 'B', 12)
        self.cell(0, 10, f"[{severity.upper()}] {title}", ln=True)
        self.set_font('helvetica', '', 10)
        self.multi_cell(0, 6, f"Description: {desc}")
        self.ln(10)

    def add_signoff(self): pass
