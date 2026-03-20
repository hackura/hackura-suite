from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView, QProgressBar, QComboBox,
    QPlainTextEdit, QMessageBox
)

from PySide6.QtCore import Qt, QThread, Signal
from core.web_fuzzer import WebFuzzer
from wrappers.web_tools import GobusterWrapper, DirsearchWrapper
from wrappers.nuclei import NucleiWrapper
from core.db import db_manager
import json

class FuzzWorker(QThread):
    progress = Signal(str)
    result_found = Signal(str, int)
    finished = Signal()

    def __init__(self, url, tool_type="Built-in"):
        super().__init__()
        self.url = url
        self.tool_type = tool_type

    def run(self):
        self.progress.emit(f"Starting {self.tool_type} assessment...")
        if self.tool_type == "Built-in":
            words = ["admin", "login", "config", "api", "v1", "backup", "wp-admin", "sh", "env", ".git"]
            self.fuzzer = WebFuzzer(self.url, words)
            self.fuzzer.progress.connect(self.progress.emit)
            self.fuzzer.result_found.connect(self.result_found.emit)
            self.fuzzer.finished.connect(self.finished.emit)
            self.fuzzer.run()
        else:
            if self.tool_type == "Gobuster":
                tool = GobusterWrapper()
            elif self.tool_type == "Nuclei":
                tool = NucleiWrapper()
            else:
                tool = DirsearchWrapper()
            
            res = tool.scan(self.url)
            self.progress.emit(res.get("raw", "No output"))
            self.finished.emit()

class WebView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(40, 40, 40, 40)

        header = QLabel("Web Application Assessment")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #00ccff;")
        self.layout.addWidget(header)

        # Input
        input_layout = QHBoxLayout()
        
        self.project_combo = QComboBox()
        self.project_combo.setPlaceholderText("Select Project")
        self.project_combo.setFixedHeight(35)
        self.project_combo.setStyleSheet("background-color: #2b2b2b; border: 1px solid #3d3d3d;")
        self.refresh_projects()

        self.tool_combo = QComboBox()
        self.tool_combo.addItems(["Built-in", "Gobuster", "Dirsearch", "Nuclei"])
        self.tool_combo.setFixedHeight(35)
        self.tool_combo.setStyleSheet("background-color: #2b2b2b; border: 1px solid #3d3d3d;")

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Target URL (e.g. https://example.com)")
        self.url_input.setFixedHeight(35)
        self.url_input.setStyleSheet("background-color: #2b2b2b; border: 1px solid #3d3d3d; padding-left: 10px;")
        
        self.fuzz_btn = QPushButton("START FUZZING")
        self.fuzz_btn.setFixedHeight(35)
        self.fuzz_btn.setStyleSheet("background-color: #00ccff; color: black; font-weight: bold; padding: 0 20px;")
        self.fuzz_btn.clicked.connect(self.start_fuzz)

        self.clear_btn = QPushButton("CLEAR")
        self.clear_btn.setFixedHeight(35)
        self.clear_btn.clicked.connect(self.clear_all)
        
        input_layout.addWidget(self.project_combo)
        input_layout.addWidget(self.tool_combo)
        input_layout.addWidget(self.url_input)
        input_layout.addWidget(self.fuzz_btn)
        input_layout.addWidget(self.clear_btn)
        self.layout.addLayout(input_layout)

        # Progress
        self.progress_label = QLabel("Ready")
        self.layout.addWidget(self.progress_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.layout.addWidget(self.progress_bar)

        # Results Table
        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["URL", "Status Code"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setStyleSheet("background-color: #1e1e1e; color: #f0f0f0;")
        self.layout.addWidget(self.table)

        # Real-time Logs
        self.layout.addWidget(QLabel("Real-time Assessment Log:"))
        self.log_area = QPlainTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setFixedHeight(150)
        self.log_area.setStyleSheet("background-color: #000; color: #00ccff; font-family: monospace;")
        self.layout.addWidget(self.log_area)

    def refresh_projects(self):
        self.project_combo.clear()
        conn = db_manager.get_connection()
        projs = conn.execute("SELECT id, name FROM projects").fetchall()
        for p in projs:
            self.project_combo.addItem(p['name'], p['id'])
        if not projs:
            self.project_combo.addItem("NO ACTIVE PROJECTS", None)

    def start_fuzz(self):
        url = self.url_input.text().strip()
        if not url: return

        # Project Guard
        self.current_project_id = self.project_combo.currentData()
        if not self.current_project_id:
            QMessageBox.warning(self, "Selection Required", "Please select a target project before starting the assessment.")
            return

        # URL Normalization
        if not url.startswith(("http://", "https://")):
            url = "http://" + url
            self.url_input.setText(url)
            self.log_area.appendPlainText(f"[!] Normalized target URL to: {url}")

        words = ["admin", "login", "config", "api", "v1", "backup", "wp-admin", "sh", "env", ".git"]
        
        self.fuzz_btn.setEnabled(False)
        self.table.setRowCount(0)
        self.log_area.clear()
        self.log_area.appendPlainText(f">>> Starting fuzzing session for {url}")
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, len(words))
        self.progress_bar.setValue(0)

        self.worker = FuzzWorker(url, self.tool_combo.currentText())
        self.worker.progress.connect(self.update_log)
        self.worker.result_found.connect(self.add_result)
        self.worker.finished.connect(self.on_finished)
        self.worker.start()

    def update_log(self, msg):
        """Append to log area and update progress status."""
        self.log_area.appendPlainText(f"[*] {msg}")
        self.progress_label.setText(msg)
        self.progress_bar.setValue(self.progress_bar.value() + 1)


    def add_result(self, url, code):
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(url))
        self.table.setItem(row, 1, QTableWidgetItem(str(code)))
        
        self.log_area.appendPlainText(f"[HIT] Found resource: {url} (Status: {code})")

        
        # Record finding for specific status codes
        if code in [200, 301, 403]:
            conn = db_manager.get_connection()
            conn.execute(
                "INSERT INTO findings (scan_id, severity, title, description) VALUES (?, ?, ?, ?)",
                (self.current_scan_id, "Info", f"Discovered: {url}", f"Found web resource with status {code}")
            )
            conn.commit()

    def clear_all(self):
        self.table.setRowCount(0)
        self.log_area.clear()
        self.progress_label.setText("Ready")
        self.progress_bar.setVisible(False)
