from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, 
    QTableWidget, QTableWidgetItem, QLabel, QHeaderView, QComboBox, QMessageBox
)
from core.osint_engine import OSINTEngine

class OSINTView(QWidget):
    def __init__(self):
        super().__init__()
        self.engine = OSINTEngine()
        
        layout = QVBoxLayout(self)
        
        header = QLabel("OSINT HUB")
        header.setStyleSheet("font-size: 18px; font-weight: bold; color: #00ccff;")
        layout.addWidget(header)
        
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter Alias, Email, or Domain...")
        self.search_type = QComboBox()
        self.search_type.addItems(["Alias", "Email", "Domain", "Search Engines", "Infrastructure"])
        search_btn = QPushButton("Gather Intelligence")
        search_btn.setFixedHeight(40)
        search_btn.setStyleSheet("background-color: #00ccff; color: black; font-weight: bold; border-radius: 4px;")
        search_btn.clicked.connect(self.run_search)
        
        self.clear_btn = QPushButton("CLEAR")
        self.clear_btn.setFixedHeight(40)
        self.clear_btn.setStyleSheet("background-color: #333; color: #aaa; border-radius: 4px;")
        self.clear_btn.clicked.connect(self.clear_results)
        
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_type)
        search_layout.addWidget(search_btn)
        search_layout.addWidget(self.clear_btn)
        layout.addLayout(search_layout)
        
        self.results_table = QTableWidget(0, 3)
        self.results_table.setHorizontalHeaderLabels(["Target/Source", "Status/Data", "Context/Link"])
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.results_table.setStyleSheet("background-color: #1a1a1a; gridline-color: #333;")
        layout.addWidget(self.results_table)

    def run_search(self):
        query = self.search_input.text().strip()
        if not query:
            return
            
        stype = self.search_type.currentText()
        self.results_table.setRowCount(0)
        
        # Immediate status feedback
        row = self.results_table.rowCount()
        self.results_table.insertRow(row)
        self.results_table.setItem(row, 0, QTableWidgetItem("System"))
        self.results_table.setItem(row, 1, QTableWidgetItem(f"Scanning {stype}..."))
        self.results_table.setItem(row, 2, QTableWidgetItem("PLEASE WAIT"))

        # Force UI update if necessary (minimal approach)
        from PySide6.QtCore import QCoreApplication
        QCoreApplication.processEvents()

        if stype == "Alias":
            results = self.engine.search_alias(query)
            footprint = self.engine.calculate_footprint(results)
            
            self.results_table.setRowCount(0) # Clear scanning msg
            
            # Footprint Summary Row
            row = self.results_table.rowCount()
            self.results_table.insertRow(row)
            self.results_table.setItem(row, 0, QTableWidgetItem("FOOTPRINT SCORE"))
            self.results_table.setItem(row, 1, QTableWidgetItem(f"{footprint['score']}% ({footprint['severity']})"))
            self.results_table.setItem(row, 2, QTableWidgetItem(footprint['description']))
            
            for res in results:
                if not isinstance(res, dict): continue
                row = self.results_table.rowCount()
                self.results_table.insertRow(row)
                self.results_table.setItem(row, 0, QTableWidgetItem(str(res.get("platform", "Unknown"))))
                self.results_table.setItem(row, 1, QTableWidgetItem("VERIFIED" if res.get("found") else "NOT FOUND"))
                self.results_table.setItem(row, 2, QTableWidgetItem(str(res.get("url", ""))))
        
        elif stype == "Email":
            results = self.engine.check_email_leak(query)
            self.results_table.setRowCount(0)
            for res in results:
                row = self.results_table.rowCount()
                self.results_table.insertRow(row)
                self.results_table.setItem(row, 0, QTableWidgetItem(res["source"]))
                self.results_table.setItem(row, 1, QTableWidgetItem(res["data"]))
                self.results_table.setItem(row, 2, QTableWidgetItem(res.get("status", "Confirmed")))
                
        elif stype == "Domain":
            info = self.engine.domain_info(query)
            self.results_table.setRowCount(0)
            
            # WHOIS
            row = self.results_table.rowCount()
            self.results_table.insertRow(row)
            self.results_table.setItem(row, 0, QTableWidgetItem("WHOIS DATA"))
            whois_snippet = str(info.get("whois", "N/A"))[:100] + "..."
            self.results_table.setItem(row, 1, QTableWidgetItem(whois_snippet))
            self.results_table.setItem(row, 2, QTableWidgetItem("Registrar Info"))

            for rec in info.get("dns_records", []):
                row = self.results_table.rowCount()
                self.results_table.insertRow(row)
                self.results_table.setItem(row, 0, QTableWidgetItem("DNS Record"))
                self.results_table.setItem(row, 1, QTableWidgetItem(str(rec)))
                self.results_table.setItem(row, 2, QTableWidgetItem("Intelligence"))

            for tech in info.get("technologies", []):
                row = self.results_table.rowCount()
                self.results_table.insertRow(row)
                self.results_table.setItem(row, 0, QTableWidgetItem("Intel"))
                self.results_table.setItem(row, 1, QTableWidgetItem(str(tech)))
                self.results_table.setItem(row, 2, QTableWidgetItem("Technology Detected"))
            for sub in info.get("subdomains", []):
                row = self.results_table.rowCount()
                self.results_table.insertRow(row)
                self.results_table.setItem(row, 0, QTableWidgetItem("Discovery"))
                self.results_table.setItem(row, 1, QTableWidgetItem(str(sub)))
                self.results_table.setItem(row, 2, QTableWidgetItem("Live Subdomain"))
            for mx in info.get("mx_records", []):
                row = self.results_table.rowCount()
                self.results_table.insertRow(row)
                self.results_table.setItem(row, 0, QTableWidgetItem("MX Record"))
                self.results_table.setItem(row, 1, QTableWidgetItem(str(mx)))
                self.results_table.setItem(row, 2, QTableWidgetItem("Mail Server"))

        elif stype == "Search Engines":
            results = self.engine.search_engines(query)
            self.results_table.setRowCount(0)
            for res in results:
                row = self.results_table.rowCount()
                self.results_table.insertRow(row)
                self.results_table.setItem(row, 0, QTableWidgetItem(res["engine"]))
                self.results_table.setItem(row, 1, QTableWidgetItem(res["title"]))
                self.results_table.setItem(row, 2, QTableWidgetItem(res["link"]))

        elif stype == "Infrastructure":
            results = self.engine.infrastructure_intel(query)
            self.results_table.setRowCount(0)
            for res in results:
                row = self.results_table.rowCount()
                self.results_table.insertRow(row)
                self.results_table.setItem(row, 0, QTableWidgetItem(res["platform"]))
                self.results_table.setItem(row, 1, QTableWidgetItem(res["data"]))
                self.results_table.setItem(row, 2, QTableWidgetItem(res["target"]))

    def clear_results(self):
        self.search_input.clear()
        self.results_table.setRowCount(0)

    def refresh_projects(self):
        # Placeholder for main window interface
        pass
