from fpdf import FPDF
import os
import datetime
from core.db import db_manager

class HackuraReport(FPDF):
    def __init__(self, client_name, client_logo=None):
        super().__init__()
        self.client_name = client_name
        self.client_logo = client_logo
        self.consult_logo = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "hackura_consult_logo.png")
        self.sections = [] # For Table of Contents
        self.set_auto_page_break(auto=True, margin=15)
        self.add_page()
        
    def header(self):
        if self.page_no() == 1: return # No header on title page
        
        # Hackura Consult Logo - Positioned higher
        if os.path.exists(self.consult_logo):
            self.image(self.consult_logo, x=10, y=5, w=20)
        
        # Consultancy Details
        self.set_font('helvetica', 'B', 10)
        self.set_text_color(0, 51, 102)
        self.set_xy(35, 8)
        self.cell(0, 5, 'HACKURA CONSULT - OFFENSIVE SECURITY DIVISION', ln=1)
        
        self.set_font('helvetica', '', 8)
        self.set_text_color(100, 100, 100)
        self.set_x(35)
        self.cell(0, 4, '12 Cyber Security Plaza, Suite 404, Pentest District, SD 90211', ln=1)
        self.set_x(35)
        self.cell(0, 4, 'ops@hackuraconsult.io | +1 (555) HACKURA | www.hackuraconsult.io', ln=1)
        
        # Client Logo - Positioned higher to avoid crossing the line at y=30
        if self.client_logo and os.path.exists(self.client_logo):
            self.image(self.client_logo, x=175, y=5, w=20)
        
        self.set_draw_color(0, 51, 102)
        self.line(10, 30, 200, 30)
        
        # VERY IMPORTANT: Set state for subsequent content
        self.set_y(35)
        self.set_x(self.l_margin)

    def footer(self):
        if self.page_no() == 1: return
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Page {self.page_no()} | CONFIDENTIAL - {self.client_name}', align='C')

    def create_title_page(self, project_name):
        self.set_font('helvetica', 'B', 28)
        self.set_text_color(0, 51, 102)
        self.ln(60)
        self.cell(0, 15, 'Security Assessment Report', ln=True, align='C')
        
        self.set_draw_color(0, 51, 102)
        self.line(50, self.get_y(), 160, self.get_y())
        
        self.set_font('helvetica', 'B', 18)
        self.set_text_color(50, 50, 50)
        self.ln(10)
        self.cell(0, 10, project_name, ln=True, align='C')
        
        self.ln(40)
        self.set_font('helvetica', 'B', 12)
        self.cell(0, 10, f'Client: {self.client_name}', ln=True, align='C')
        self.set_font('helvetica', '', 11)
        self.cell(0, 8, f'Date of Issue: {datetime.date.today()}', ln=True, align='C')
        self.cell(0, 8, 'Classification: CONFIDENTIAL', ln=True, align='C')
        
        # Assessment Badge
        self.set_xy(85, 220)
        self.set_font('helvetica', 'B', 10)
        self.set_draw_color(0, 128, 0)
        self.set_text_color(0, 128, 0)
        self.cell(40, 10, 'CERTIFIED ASSESSMENT', border=1, ln=True, align='C')
        
        self.add_page()
        self.add_disclaimer_page()

    def add_disclaimer_page(self):
        self.add_section("Legal & Confidentiality", self.page_no())
        self.set_x(10)
        self.set_font('helvetica', 'B', 16)
        self.set_text_color(0, 51, 102)
        self.cell(0, 10, "Legal Disclaimer & Confidentiality Notice", ln=1)
        self.ln(5)
        self.set_x(10)
        self.set_font('helvetica', '', 11)
        self.set_text_color(50, 50, 50)
        text = (
            "This document is the property of Hackura Consult and the Client specified on the title page. "
            "The information contained herein is highly sensitive and confidential. Unauthorized distribution, "
            "copying, or disclosure is strictly prohibited.\n\n"
            "The findings presented in this report represent a snapshot in time of the security posture of the "
            "scoped systems. While every effort has been made to identify vulnerabilities, this assessment does "
            "not guarantee that all security flaws have been discovered. Hackura Consult accepts no liability "
            "for any damages resulting from the use or misuse of the information provided."
        )
        self.multi_cell(190, 7, text)
        self.ln(10)
        
        # Severity Glossary
        self.set_x(10)
        self.set_font('helvetica', 'B', 14)
        self.cell(0, 10, "Risk Severity Definitions", ln=1)
        self.set_font('helvetica', '', 10)
        glossary = [
            ("CRITICAL", "Immediate threat to core business logic or sensitive data. Requires instant remediation."),
            ("HIGH", "Significant risk of compromise. Should be addressed within 24-48 hours."),
            ("MEDIUM", "Vulnerability that could be exploited with moderate effort or specific conditions."),
            ("LOW", "Minor security concern or information disclosure with limited impact."),
            ("INFO", "Best practice recommendation or general observation with no immediate risk.")
        ]
        for title, desc in glossary:
            self.set_x(10)
            self.set_font('helvetica', 'B', 10)
            self.cell(35, 7, title, 0)
            self.set_font('helvetica', '', 10)
            self.multi_cell(155, 7, desc)
            self.ln(2)
        self.add_page()

    def add_section(self, title, page):
        self.sections.append((title, page))

    def create_toc_page(self):
        self.add_page()
        self.set_x(10)
        self.set_font('helvetica', 'B', 16)
        self.set_text_color(0, 51, 102)
        self.cell(0, 10, "Table of Contents", ln=1)
        self.ln(5)
        self.set_font('helvetica', '', 12)
        self.set_text_color(0, 0, 0)
        for i, (title, page) in enumerate(self.sections):
            self.set_x(10)
            self.cell(170, 8, f"{i+1}. {title}", 0)
            self.cell(20, 8, str(page), 0, 1, 'R')
            self.line(10, self.get_y(), 200, self.get_y())
        self.add_page()

    def add_finding_card(self, title, severity, description, remediation, owasp_mapping="N/A"):
        # Preemptive page break check
        if self.get_y() > 220:
            self.add_page()
            
        y_start = self.get_y()
        # Header Background
        self.set_fill_color(245, 245, 245)
        self.rect(10, y_start, 190, 45, 'F')
        
        self.set_font('helvetica', 'B', 14)
        if severity.lower() == 'critical': self.set_text_color(200, 0, 0)
        elif severity.lower() == 'high': self.set_text_color(255, 69, 0)
        elif severity.lower() == 'medium': self.set_text_color(218, 165, 32)
        else: self.set_text_color(0, 100, 0)
        
        self.set_x(10)
        self.cell(0, 10, f"[{severity.upper()}] {title}", ln=1)
        self.set_text_color(0, 0, 0)
        
        self.set_x(10)
        self.set_font('helvetica', 'B', 10)
        self.cell(0, 8, f"OWASP Alignment: {owasp_mapping}", ln=1)
        
        self.set_x(10)
        self.set_font('helvetica', '', 10)
        self.set_text_color(60, 60, 60)
        self.multi_cell(190, 6, f"Context: {description}")
        self.ln(4)
        
        self.set_x(10)
        self.set_font('helvetica', 'B', 10)
        self.set_text_color(0, 51, 102)
        self.cell(0, 8, "Remediation Strategy:", ln=1)
        self.set_x(10)
        self.set_font('helvetica', '', 10)
        self.set_text_color(0, 0, 0)
        self.multi_cell(190, 6, remediation)
        self.ln(10)

    def add_chart(self, title, chart_path):
        if not os.path.exists(chart_path): return
        self.set_font('helvetica', 'B', 14)
        self.set_text_color(0, 51, 102)
        self.cell(0, 10, title, ln=True)
        self.ln(5)
        self.image(chart_path, x=20, w=170)
        self.ln(10)

    def add_signoff(self):
        self.ln(20)
        self.set_font('helvetica', 'B', 12)
        self.cell(0, 10, "Executive Sign-off", ln=True)
        self.ln(10)
        self.line(10, self.get_y(), 90, self.get_y())
        self.line(110, self.get_y(), 190, self.get_y())
        self.set_font('helvetica', '', 10)
        self.cell(90, 8, "Hackura Consult Lead", 0)
        self.cell(90, 8, f"{self.client_name} Representative", 0, 1, 'R')
