from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QPlainTextEdit, QFrame, QComboBox, QLineEdit
)
from PySide6.QtCore import Qt
from core.obfuscator import obfuscator

class ObfuscationView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(40, 40, 40, 40)
        self.layout.setSpacing(20)

        header = QLabel("Advanced Obfuscation Pipeline")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #ffaa00;")
        self.layout.addWidget(header)

        # Config
        config_frame = QFrame()
        config_frame.setStyleSheet("background-color: #2b2b2b; border: 1px solid #3d3d3d; border-radius: 8px;")
        config_layout = QVBoxLayout(config_frame)
        
        config_layout.addWidget(QLabel("Input Payload / Shellcode:"))
        self.input_area = QPlainTextEdit()
        self.input_area.setPlaceholderText("Paste your raw script or shellcode here...")
        config_layout.addWidget(self.input_area)

        self.method_combo = QComboBox()
        self.method_combo.addItems(["XOR Encryption", "Base64 Layering", "Python Exec Stub"])
        config_layout.addWidget(QLabel("Obfuscation Method:"))
        config_layout.addWidget(self.method_combo)
        
        self.gen_btn = QPushButton("PROTECT PAYLOAD")
        self.gen_btn.setStyleSheet("background-color: #ffaa00; color: black; font-weight: bold; height: 40px;")
        self.gen_btn.clicked.connect(self.run_obfuscation)
        config_layout.addWidget(self.gen_btn)
        
        self.layout.addWidget(config_frame)

        # Output
        self.output_area = QPlainTextEdit()
        self.output_area.setReadOnly(True)
        self.output_area.setStyleSheet("background-color: #000; color: #00ff00; font-family: monospace;")
        self.layout.addWidget(self.output_area)

    def run_obfuscation(self):
        data = self.input_area.toPlainText().strip()
        if not data: return
        
        method = self.method_combo.currentText()
        self.output_area.clear()
        
        if method == "XOR Encryption":
            encrypted, key = obfuscator.xor_encrypt(data)
            self.output_area.appendPlainText(f"# XOR Key: {key}\n")
            self.output_area.appendPlainText(encrypted)
        elif method == "Base64 Layering":
            self.output_area.appendPlainText(obfuscator.b64_obfuscate(data))
        elif method == "Python Exec Stub":
            encrypted, key = obfuscator.xor_encrypt(data)
            stub = obfuscator.generate_python_stub(encrypted, key)
            self.output_area.appendPlainText(stub)

    def refresh_projects(self): pass
