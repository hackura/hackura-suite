from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QLineEdit, QPlainTextEdit, QProgressBar, QComboBox, QMessageBox
)

from PySide6.QtCore import Qt, QThread, Signal
from wrappers.nmap import NmapWrapper
from wrappers.network_utils import PingWrapper, WhoisWrapper, DNSWrapper
from core.db import db_manager
import json

class ScanWorker(QThread):
    finished = Signal(dict)
    progress = Signal(str)

    def __init__(self, target, tool_type="Nmap"):
        super().__init__()
        self.target = target
        self.tool_type = tool_type

    def run(self):
        self.progress.emit(f"Initializing {self.tool_type} assessment...")
        if self.tool_type == "Nmap":
            tool = NmapWrapper()
        elif self.tool_type == "Ping":
            tool = PingWrapper()
        elif self.tool_type == "WHOIS":
            tool = WhoisWrapper()
        elif self.tool_type == "DNS":
            tool = DNSWrapper()
        else:
            self.finished.emit({"success": False, "error": "Unknown tool"})
            return

        if not tool.is_available():
            self.finished.emit({"success": False, "error": f"Tool '{tool.tool_name}' not installed."})
            return

        result = tool.scan(self.target)
        self.finished.emit(result)

class NetworkView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(40, 40, 40, 40)

        header = QLabel("Network Assessment")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #00ccff;")
        self.layout.addWidget(header)

        input_layout = QHBoxLayout()
        
        self.project_combo = QComboBox()
        self.project_combo.setPlaceholderText("Select Project")
        self.project_combo.setFixedHeight(35)
        self.project_combo.setStyleSheet("background-color: #2b2b2b; border: 1px solid #3d3d3d;")
        self.refresh_projects()

        self.tool_combo = QComboBox()
        self.tool_combo.addItems(["Nmap", "Ping", "WHOIS", "DNS"])
        self.tool_combo.setFixedHeight(35)
        self.tool_combo.setStyleSheet("background-color: #2b2b2b; border: 1px solid #3d3d3d;")
        
        self.target_input = QLineEdit()
        self.target_input.setPlaceholderText("Target (IP, Domain, Range)")
        self.target_input.setFixedHeight(35)
        self.target_input.setStyleSheet("background-color: #2b2b2b; border: 1px solid #3d3d3d; padding-left: 10px;")
        
        self.scan_btn = QPushButton("RUN ASSESSMENT")
        self.scan_btn.setFixedHeight(35)
        self.scan_btn.setStyleSheet("background-color: #00ccff; color: black; font-weight: bold; padding: 0 20px;")
        self.scan_btn.clicked.connect(self.start_scan)

        self.clear_btn = QPushButton("CLEAR")
        self.clear_btn.setFixedHeight(35)
        self.clear_btn.clicked.connect(lambda: self.log_area.clear())
        
        input_layout.addWidget(self.project_combo)
        input_layout.addWidget(self.tool_combo)
        input_layout.addWidget(self.target_input)
        input_layout.addWidget(self.scan_btn)
        input_layout.addWidget(self.clear_btn)
        self.layout.addLayout(input_layout)

        # Progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("QProgressBar { border: 1px solid #3d3d3d; text-align: center; } QProgressBar::chunk { background-color: #00ccff; }")
        self.layout.addWidget(self.progress_bar)

        # Results area
        self.log_area = QPlainTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setStyleSheet("background-color: #000; color: #00ff00; font-family: monospace; border: 1px solid #3d3d3d; margin-top: 10px;")
        self.layout.addWidget(self.log_area)

    def refresh_projects(self):
        self.project_combo.clear()
        conn = db_manager.get_connection()
        projs = conn.execute("SELECT id, name FROM projects").fetchall()
        if not projs:
            self.project_combo.addItem("NO ACTIVE PROJECTS", None)
            return
            
        for p in projs:
            self.project_combo.addItem(p['name'], p['id'])

    def start_scan(self):
        target = self.target_input.text().strip()
        tool_type = self.tool_combo.currentText()
        if not target: return

        # Project Guard
        self.current_project_id = self.project_combo.currentData()
        if not self.current_project_id:
            QMessageBox.warning(self, "Selection Required", "Please select a target project before starting the assessment.")
            return

        self.scan_btn.setEnabled(False)

        self.log_area.setPlainText(f">>> Initializing {tool_type} for {target}\n")
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        
        self.current_project_id = self.project_combo.currentData()
        self.current_target = target
        self.current_tool = tool_type
        db_manager.log_action("Network Assessment Started", f"Tool: {tool_type} | Target: {target}")

        self.worker = ScanWorker(target, tool_type)
        self.worker.progress.connect(lambda msg: self.log_area.appendPlainText(f"[+] {msg}"))
        self.worker.finished.connect(self.on_scan_finished)
        self.worker.start()

    def on_scan_finished(self, result):
        self.scan_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        if result["success"]:
            self.log_area.appendPlainText(f"\n--- {self.current_tool} Results ---")
            # Persist to DB
            conn = db_manager.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO scans (project_id, type, target, status, results) VALUES (?, ?, ?, ?, ?)",
                (self.current_project_id, self.current_tool, self.current_target, "Completed", json.dumps(result))
            )
            scan_id = cursor.lastrowid
            
            if self.current_tool == "Nmap":
                for host in result.get("hosts", []):
                    self.log_area.appendPlainText(f"Host: {host['address']} ({host['status']})")
                    for port in host['ports']:
                        self.log_area.appendPlainText(f"  Port: {port['id']}/{port['protocol']} - {port['state']}")
                        if port['state'] == 'open':
                            cursor.execute(
                                "INSERT INTO findings (scan_id, severity, title, description) VALUES (?, ?, ?, ?)",
                                (scan_id, "Medium", f"Open Port: {port['id']}", f"Port {port['id']} open on {host['address']}")
                            )
            elif self.current_tool == "Ping":
                status = "Alive" if result.get("alive") else "Unreachable"
                self.log_area.appendPlainText(f"Status: {status}")
                self.log_area.appendPlainText(result.get("raw", ""))
            else:
                self.log_area.appendPlainText(result.get("data", "No data returned."))

            conn.commit()
        else:
            self.log_area.appendPlainText(f"\n[!] Error: {result.get('error', 'Unknown error')}")
