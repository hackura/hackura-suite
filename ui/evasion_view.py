from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QLineEdit, QComboBox, QPlainTextEdit, QFrame
)
from PySide6.QtCore import Qt
from core.evasion import EvasionEngine

class EvasionView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(40, 40, 40, 40)
        self.layout.setSpacing(20)

        header = QLabel("Endpoint/EDR Evasion Suite")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #ffaa00;")
        self.layout.addWidget(header)

        # Shellcode Gen
        gen_frame = QFrame()
        gen_frame.setStyleSheet("background-color: #2b2b2b; border: 1px solid #3d3d3d; border-radius: 8px;")
        gen_layout = QVBoxLayout(gen_frame)
        
        gen_layout.addWidget(QLabel("C2 CONFIGURATION"))
        self.lhost_input = QLineEdit("10.0.0.5")
        self.lport_input = QLineEdit("4444")
        gen_layout.addWidget(QLabel("LHOST:"))
        gen_layout.addWidget(self.lhost_input)
        gen_layout.addWidget(QLabel("LPORT:"))
        gen_layout.addWidget(self.lport_input)

        self.gen_btn = QPushButton("GENERATE EVASIVE SHELLCODE")
        self.gen_btn.setStyleSheet("background-color: #ffaa00; color: black; font-weight: bold;")
        self.gen_btn.clicked.connect(self.run_gen)
        gen_layout.addWidget(self.gen_btn)

        self.clear_btn = QPushButton("CLEAR OUTPUT")
        self.clear_btn.clicked.connect(lambda: self.output_area.clear())
        gen_layout.addWidget(self.clear_btn)
        self.layout.addWidget(gen_frame)

        # Bypass Templates
        self.tech_combo = QComboBox()
        self.tech_combo.addItems(["AMSI Patch", "ETW Bypass", "Indirect Syscalls"])
        self.layout.addWidget(QLabel("Defensive Bypass Technique:"))
        self.layout.addWidget(self.tech_combo)

        self.get_template_btn = QPushButton("FETCH BYPASS TEMPLATE")
        self.get_template_btn.clicked.connect(self.run_template)
        self.layout.addWidget(self.get_template_btn)

        self.output_area = QPlainTextEdit()
        self.output_area.setReadOnly(True)
        self.output_area.setStyleSheet("background-color: #000; color: #ffaa00; font-family: monospace;")
        self.layout.addWidget(self.output_area)

        self.engine = EvasionEngine()

    def run_gen(self):
        lhost = self.lhost_input.text()
        lport = self.lport_input.text()
        code = self.engine.generate_shellcode(lhost, lport)
        self.output_area.setPlainText(f"// Generated Evasive Shellcode for C2\n{code}")

    def run_template(self):
        tech = self.tech_combo.currentText()
        template = self.engine.get_patch_template(tech)
        self.output_area.setPlainText(f"// {tech} Template\n{template}")

    def refresh_projects(self): pass
