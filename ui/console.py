import subprocess
import os
import sys
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTextEdit, QLineEdit, QLabel
)
from PySide6.QtCore import Qt, QProcess

class ConsoleView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(40, 40, 40, 40)

        header = QLabel("Interactive Pentest Console")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #00ccff;")
        self.layout.addWidget(header)

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setStyleSheet("""
            background-color: #000;
            color: #00ff00;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 13px;
        """)
        self.layout.addWidget(self.output)

        self.input = QLineEdit()
        self.input.setPlaceholderText("Enter command (e.g. nmap -F 127.0.0.1)")
        self.input.setStyleSheet("""
            background-color: #1e1e1e;
            color: #fff;
            border: 1px solid #3d3d3d;
            padding: 8px;
            font-family: monospace;
        """)
        self.input.returnPressed.connect(self.execute_command)
        self.layout.addWidget(self.input)

        self.process = QProcess(self)
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.finished.connect(self.command_finished)

    def execute_command(self):
        cmd = self.input.text()
        if not cmd: return
        
        self.output.append(f"<span style='color: #00ccff;'># {cmd}</span>")
        self.input.clear()
        self.input.setEnabled(False)
        
        # Split command for execution
        parts = cmd.split()
        self.process.start(parts[0], parts[1:])

    def handle_stdout(self):
        data = self.process.readAllStandardOutput().data().decode()
        self.output.append(data)

    def handle_stderr(self):
        data = self.process.readAllStandardError().data().decode()
        self.output.append(f"<span style='color: #ff3333;'>{data}</span>")

    def command_finished(self):
        self.input.setEnabled(True)
        self.input.setFocus()
