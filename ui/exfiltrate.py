from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QComboBox, QPlainTextEdit, QProgressBar, QLineEdit, QMessageBox,
    QFrame, QGridLayout
)

from PySide6.QtCore import Qt, Signal, QObject, QRunnable, QThreadPool, QThread
from core.exfiltrator import Exfiltrator
from wrappers.nuclei import NucleiWrapper
from wrappers.subfinder import SubfinderWrapper
from wrappers.osint import OSINTWrapper
from wrappers.cloud_hunter import CloudHunterWrapper
from wrappers.fingerprinter import FingerprintWrapper
from wrappers.defence import DefenceWrapper


class ToolSignals(QObject):
    finished = Signal(dict)
    progress = Signal(str)
    status_changed = Signal(str, str) # tool_name, status

class ToolRunner(QRunnable):
    def __init__(self, tool_type, target, project_id=None, data=None, timeout=300):
        super().__init__()
        self.tool_type = tool_type
        self.target = target
        self.project_id = project_id
        self.data = data
        self.timeout = timeout
        self.signals = ToolSignals()

    def run(self):
        self.signals.status_changed.emit(self.tool_type, "RUNNING")
        self.signals.progress.emit(f"Initializing {self.tool_type} parallel module...")
        
        try:
            # Mapping to Toolkit
            if self.tool_type in ["HTTPS POST", "DNS (Simulated)", "ICMP (Simulated)"]:
                exfil = Exfiltrator(self.tool_type, self.target, self.data)
                exfil.progress.connect(self.signals.progress.emit)
                exfil.run()
                result = {"success": True, "tool": self.tool_type, "status": "COMPLETED", "log": exfil.logs}

            elif self.tool_type == "Nuclei":
                tool = NucleiWrapper()
                result = tool.scan(self.target, timeout=self.timeout)
            elif self.tool_type == "Subfinder":
                tool = SubfinderWrapper()
                result = tool.scan(self.target, timeout=self.timeout)
            elif self.tool_type == "OSINT Hub":
                tool = OSINTWrapper()
                result = tool.scan(self.target, timeout=self.timeout)
            elif self.tool_type == "Cloud Hunter":
                tool = CloudHunterWrapper()
                result = tool.scan(self.target, timeout=self.timeout)
            elif self.tool_type == "Tech Fingerprint":
                tool = FingerprintWrapper()
                result = tool.scan(self.target, timeout=self.timeout)
            elif self.tool_type == "Defence Audit":
                tool = DefenceWrapper()
                result = tool.scan(self.target, timeout=self.timeout)
            else:
                result = {"success": False, "error": "Invalid Tool Type", "status": "FAILED", "tool": self.tool_type}
            
            self.signals.status_changed.emit(self.tool_type, result.get("status", "COMPLETED"))
            
            if self.project_id and result.get("success"):
                self._persist_results(result)
                
            self.signals.finished.emit(result)
        except Exception as e:
            self.signals.status_changed.emit(self.tool_type, "FAILED")
            self.signals.finished.emit({"success": False, "error": str(e), "tool": self.tool_type})

    def _persist_results(self, result):
        from core.db import db_manager
        import json
        conn = db_manager.get_connection()
        
        try:
            cursor = conn.cursor()
            # 1. Create Scan Entry
            cursor.execute(
                "INSERT INTO scans (project_id, type, target, status, results) VALUES (?, ?, ?, ?, ?)",
                (self.project_id, self.tool_type, self.target, result.get("status"), json.dumps(result))
            )
            scan_id = cursor.lastrowid
            
            # 2. Extract and Persist Findings
            raw_findings = result.get("findings", [])
            if "subdomains" in result:
                for sub in result["subdomains"]:
                    raw_findings.append({"type": "DNS", "data": f"Subdomain discovered: {sub}", "severity": "Info"})

            for f in raw_findings:
                title = f.get("title", f"{self.tool_type} Discovery")
                if "info" in f:
                    info = f["info"]
                    title = info.get("name", title)
                    severity = info.get("severity", "Info").capitalize()
                    desc = f.get("matched-at", f.get("template-id", "N/A"))
                else:
                    severity = f.get("severity", "Medium").capitalize()
                    desc = f.get("data", "No additional context provided.")
                
                remediation = "Apply security best practices and restrict access to sensitive endpoints."
                
                cursor.execute(
                    "INSERT INTO findings (scan_id, severity, title, description, remediation) VALUES (?, ?, ?, ?, ?)",
                    (scan_id, severity, title, desc, remediation)
                )
            conn.commit()
            print(f"[+] Persisted {len(raw_findings)} findings for Scan ID: {scan_id}")
        except Exception as e:
            print(f"[!] Persistence Error: {e}")

class RedTeamView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(40, 40, 40, 40)

        header = QLabel("Red Team Operations Center")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #ff3333;")
        self.layout.addWidget(header)

        # 1. Operational Status HUD (Live)
        self.hud_box = QFrame()
        self.hud_box.setStyleSheet("background-color: #0a0a0a; border: 1px solid #333; border-radius: 5px;")
        hud_layout = QVBoxLayout(self.hud_box)
        hud_title = QLabel("LIVE MISSION STATUS")
        hud_title.setStyleSheet("font-size: 10px; font-weight: bold; color: #555; letter-spacing: 1px;")
        hud_layout.addWidget(hud_title)
        
        self.status_grid = QGridLayout()
        self.status_labels = {}
        hud_layout.addLayout(self.status_grid)
        self.layout.addWidget(self.hud_box)
        
        self.thread_pool = QThreadPool.globalInstance()
        self.active_workers = [] # Track for GC safety
        self.running_count = 0

        # Target Selection
        self.project_combo = QComboBox()
        self.project_combo.setPlaceholderText("Select Project")
        self.project_combo.setFixedHeight(35)
        self.project_combo.setStyleSheet("background-color: #2b2b2b; border: 1px solid #3d3d3d;")
        self.refresh_projects()
        self.layout.addWidget(self.project_combo)

        # Config
        config_layout = QVBoxLayout()
        
        target_layout = QHBoxLayout()
        target_layout.addWidget(QLabel("Primary Target/Server:"))
        self.target_input = QLineEdit()
        self.target_input.setPlaceholderText("e.g. internal-api.local or evil-collector.com")
        self.target_input.setStyleSheet("background-color: #2b2b2b; border: 1px solid #3d3d3d;")
        target_layout.addWidget(self.target_input)
        config_layout.addLayout(target_layout)

        tech_layout = QHBoxLayout()
        tech_layout.addWidget(QLabel("Red Team Tool:"))
        self.tool_combo = QComboBox()
        self.tool_combo.addItems([
            "Nuclei (Vuln Scan)",
            "Subfinder (Discovery)",
            "OSINT Hub (Passive Info)",
            "Cloud Hunter (S3/Azure/GCP)",
            "Tech Fingerprint (Web Stack)",
            "Full OSINT Suite (Parallel All)",
            "HTTPS POST (Exfil Beacon)", 
            "DNS (Exfil Tunnel)", 
            "ICMP (Exfil Payload)",
            "Defence Audit (EDR/AV Probing)"
        ])
        self.tool_combo.setStyleSheet("background-color: #2b2b2b; border: 1px solid #3d3d3d;")
        self.tool_combo.currentTextChanged.connect(self.clear_mission_hud)
        tech_layout.addWidget(self.tool_combo)
        config_layout.addLayout(tech_layout)
        
        # Timeout Config
        timeout_layout = QHBoxLayout()
        timeout_layout.addWidget(QLabel("Operation Timeout (Seconds):"))
        self.timeout_input = QLineEdit("60")
        self.timeout_input.setFixedWidth(60)
        self.timeout_input.setStyleSheet("background-color: #2b2b2b; border: 1px solid #3d3d3d;")
        timeout_layout.addWidget(self.timeout_input)
        timeout_layout.addStretch()
        config_layout.addLayout(timeout_layout)

        self.layout.addLayout(config_layout)

        # Data to exfiltrate (Optional for some tools)
        self.data_label = QLabel("Data Payload (Optional for non-exfil tools):")
        self.layout.addWidget(self.data_label)
        self.data_input = QPlainTextEdit()
        self.data_input.setPlaceholderText("Paste sensitive data or custom payload here...")
        self.data_input.setStyleSheet("background-color: #2b2b2b; border: 1px solid #3d3d3d;")
        self.layout.addWidget(self.data_input)

        # Status
        self.log_area = QPlainTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setStyleSheet("background-color: #000; color: #ff3333; font-family: monospace; border: 1px solid #3d3d3d;")
        self.layout.addWidget(self.log_area)

        # Control Buttons
        btn_layout = QHBoxLayout()
        self.run_btn = QPushButton("EXECUTE OPERATION")
        self.run_btn.setFixedHeight(40)
        self.run_btn.setStyleSheet("background-color: #ff3333; color: white; font-weight: bold;")
        self.run_btn.clicked.connect(self.start_operation)
        
        self.clear_btn = QPushButton("CLEAR TERMINAL")
        self.clear_btn.setFixedHeight(40)
        self.clear_btn.setStyleSheet("background-color: #2b2b2b; color: #888; border: 1px solid #3d3d3d;")
        self.clear_btn.clicked.connect(self.log_area.clear)
        
        btn_layout.addWidget(self.run_btn, 3)
        btn_layout.addWidget(self.clear_btn, 1)
        self.layout.addLayout(btn_layout)

    def start_operation(self):
        target = self.target_input.text().strip()
        project_id = self.project_combo.currentData()
        
        if not target:
            QMessageBox.warning(self, "Input Required", "Please enter a target DOMAIN or IP.")
            return
        if not project_id:
            QMessageBox.warning(self, "Project Required", "Please select an active project to store results.")
            return
        
        try:
            timeout = int(self.timeout_input.text())
        except ValueError:
            timeout = 60
        
        data = self.data_input.toPlainText().strip()
        raw_tech = self.tool_combo.currentText()
        self.run_btn.setEnabled(False)
        tech_map = {
            "Nuclei (Vuln Scan)": ["Nuclei"],
            "Subfinder (Discovery)": ["Subfinder"],
            "OSINT Hub (Passive Info)": ["OSINT Hub"],
            "Cloud Hunter (S3/Azure/GCP)": ["Cloud Hunter"],
            "Tech Fingerprint (Web Stack)": ["Tech Fingerprint"],
            "Defence Audit (EDR/AV Probing)": ["Defence Audit"],
            "Full OSINT Suite (Parallel All)": [
                "OSINT Hub", "Subfinder", "Nuclei", 
                "Cloud Hunter", "Tech Fingerprint", "Defence Audit"
            ],
            "HTTPS POST (Exfil Beacon)": ["HTTPS POST"],
            "DNS (Exfil Tunnel)": ["DNS (Simulated)"],
            "ICMP (Exfil Payload)": ["ICMP (Simulated)"]
        }
        
        tools_to_run = tech_map.get(raw_tech, [])
        self.log_area.appendPlainText(f"[!] Launching {raw_tech} Operation(s) against {target} (Project ID: {project_id})\n")

        # Robust Parallel Launch
        self.running_count = len(tools_to_run)
        for tool_name in tools_to_run:
            self._update_hud_status(tool_name, "PENDING")
            worker = ToolRunner(tool_name, target, project_id=project_id, data=data, timeout=timeout)
            worker.signals.progress.connect(lambda msg: self.log_area.appendPlainText(f"[*] {msg}"))
            worker.signals.status_changed.connect(self._update_hud_status)
            worker.signals.finished.connect(self.on_operation_finished)
            self.active_workers.append(worker) # Critical: keep ref alive
            self.thread_pool.start(worker)

    def _update_hud_status(self, tool_name, status):
        if tool_name not in self.status_labels:
            row = len(self.status_labels) // 3
            col = (len(self.status_labels) % 3) * 2
            
            name_lbl = QLabel(tool_name)
            name_lbl.setStyleSheet("color: #888; font-size: 10px;")
            status_lbl = QLabel("READY")
            status_lbl.setStyleSheet("color: #444; font-size: 10px; font-weight: bold;")
            
            self.status_grid.addWidget(name_lbl, row, col)
            self.status_grid.addWidget(status_lbl, row, col + 1)
            self.status_labels[tool_name] = (name_lbl, status_lbl)
        
        color_map = {
            "PENDING": "#ffaa00",
            "RUNNING": "#00ccff",
            "COMPLETED": "#00ff00",
            "TIMEOUT": "#ff3333",
            "FAILED": "#ff3333"
        }
        name_lbl, status_lbl = self.status_labels[tool_name]
        status_lbl.setText(status)
        status_lbl.setStyleSheet(f"color: {color_map.get(status, '#888')}; font-size: 10px; font-weight: bold;")

    def clear_mission_hud(self):
        """Clears the live status HUD labels."""
        for name_lbl, status_lbl in self.status_labels.values():
            self.status_grid.removeWidget(name_lbl)
            self.status_grid.removeWidget(status_lbl)
            name_lbl.deleteLater()
            status_lbl.deleteLater()
        self.status_labels.clear()

    def on_operation_finished(self, result):
        self.running_count -= 1
        if self.running_count <= 0:
            self.run_btn.setEnabled(True)
            self.active_workers.clear() # GC cleanup
            self.running_count = 0
        if result.get("success"):
            self.log_area.appendPlainText(f"\n[+] {result.get('tool', 'Operation')} Completed Successfully.")
            
            # Print logs first for temporal flow
            if "log" in result:
                for l in result["log"]:
                    self.log_area.appendPlainText(l)
            
            # Then print specific findings
            if "subdomains" in result:
                for sub in result["subdomains"]:
                    self.log_area.appendPlainText(f"    Subdomain: {sub}")
            if "findings" in result:
                for f in result["findings"]:
                    self.log_area.appendPlainText(f"    - {f.get('type', f.get('info', {}).get('severity', 'Finding'))}: {f.get('data', f.get('info', {}).get('name', 'N/A'))}")
        else:
            self.log_area.appendPlainText(f"\n[!] Operation Failed: {result.get('error', 'Unknown Error')}")

    def refresh_projects(self):
        self.project_combo.clear()
        from core.db import db_manager
        conn = db_manager.get_connection()
        projs = conn.execute("SELECT id, name FROM projects").fetchall()
        if not projs:
            self.project_combo.addItem("NO ACTIVE PROJECTS", None)
            return
        for p in projs:
            self.project_combo.addItem(p['name'], p['id'])

