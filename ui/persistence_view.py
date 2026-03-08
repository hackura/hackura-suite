from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QPlainTextEdit, QFrame, QTableWidget, QTableWidgetItem, QHeaderView
)
from PySide6.QtCore import Qt
from core.c2_server import c2_server

class PersistenceView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(40, 40, 40, 40)
        self.layout.setSpacing(20)

        header = QLabel("Post-Exploitation Persistence (C2)")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #ff3333;")
        self.layout.addWidget(header)

        # C2 Monitor
        main_layout = QHBoxLayout()
        
        # Left: Agents Table
        table_frame = QFrame()
        table_frame.setStyleSheet("background-color: #2b2b2b; border: 1px solid #3d3d3d; border-radius: 8px;")
        table_layout = QVBoxLayout(table_frame)
        
        table_layout.addWidget(QLabel("Active Beaconing Agents:"))
        self.agent_table = QTableWidget(0, 3)
        self.agent_table.setHorizontalHeaderLabels(["Agent ID", "IP Address", "Target OS"])
        self.agent_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.agent_table.setStyleSheet("background-color: #1a1a1a;")
        table_layout.addWidget(self.agent_table)
        
        self.start_c2_btn = QPushButton("START C2 LISTENER (PORT 4444)")
        self.start_c2_btn.setStyleSheet("background-color: #ff3333; color: white; font-weight: bold;")
        self.start_c2_btn.clicked.connect(self.toggle_c2)
        table_layout.addWidget(self.start_c2_btn)
        
        main_layout.addWidget(table_frame, 3)
        
        # Right: Interaction Console
        self.console = QPlainTextEdit()
        self.console.setReadOnly(True)
        self.console.setStyleSheet("background-color: #000; color: #ff3333; font-family: monospace;")
        main_layout.addWidget(self.console, 2)
        
        self.layout.addLayout(main_layout)

    def toggle_c2(self):
        if not c2_server.running:
            self.start_c2_btn.setText("STOP C2 LISTENER")
            c2_server.start_server(callback=self.update_log)
        else:
            self.start_c2_btn.setText("START C2 LISTENER (PORT 4444)")
            c2_server.stop_server()
            self.console.appendPlainText("[!] C2 Server Stopped.")

    def update_log(self, msg):
        self.console.appendPlainText(msg)
        if "New connection" in msg:
            self.refresh_agents()

    def refresh_agents(self):
        self.agent_table.setRowCount(0)
        for aid, info in c2_server.clients.items():
            row = self.agent_table.rowCount()
            self.agent_table.insertRow(row)
            self.agent_table.setItem(row, 0, QTableWidgetItem(aid))
            self.agent_table.setItem(row, 1, QTableWidgetItem(info['ip']))
            self.agent_table.setItem(row, 2, QTableWidgetItem(info['os']))

    def refresh_projects(self): pass
