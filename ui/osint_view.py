from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, 
    QTableWidget, QTableWidgetItem, QLabel, QHeaderView, QComboBox
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
        self.search_type.addItems(["Alias", "Email", "Domain"])
        search_btn = QPushButton("Gather Intelligence")
        search_btn.clicked.connect(self.run_search)
        
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_type)
        search_layout.addWidget(search_btn)
        layout.addLayout(search_layout)
        
        self.results_table = QTableWidget(0, 3)
        self.results_table.setHorizontalHeaderLabels(["Platform/Source", "Status/Data", "Link/Details"])
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.results_table)

    def run_search(self):
        query = self.search_input.text()
        stype = self.search_type.currentText()
        self.results_table.setRowCount(0)
        
        if stype == "Alias":
            results = self.engine.search_alias(query)
            for res in results:
                row = self.results_table.rowCount()
                self.results_table.insertRow(row)
                self.results_table.setItem(row, 0, QTableWidgetItem(res["platform"]))
                self.results_table.setItem(row, 1, QTableWidgetItem("Found" if res["found"] else "Not Found"))
                self.results_table.setItem(row, 2, QTableWidgetItem(res["url"]))
        
        elif stype == "Email":
            results = self.engine.check_email_leak(query)
            for res in results:
                row = self.results_table.rowCount()
                self.results_table.insertRow(row)
                self.results_table.setItem(row, 0, QTableWidgetItem(res["source"]))
                self.results_table.setItem(row, 1, QTableWidgetItem(res["data"]))
                self.results_table.setItem(row, 2, QTableWidgetItem("N/A"))
                
        elif stype == "Domain":
            info = self.engine.domain_info(query)
            for tech in info["technologies"]:
                row = self.results_table.rowCount()
                self.results_table.insertRow(row)
                self.results_table.setItem(row, 0, QTableWidgetItem("Technology"))
                self.results_table.setItem(row, 1, QTableWidgetItem(tech))
                self.results_table.setItem(row, 2, QTableWidgetItem(query))

    def refresh_projects(self):
        # Placeholder for main window interface
        pass
