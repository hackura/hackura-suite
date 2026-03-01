from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QComboBox
)
from core.db import db_manager

class ProjectView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(40, 40, 40, 40)

        header = QLabel("Project & Target Management")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #00ccff;")
        self.layout.addWidget(header)

        # Create Project
        create_layout = QHBoxLayout()
        
        self.client_combo = QComboBox()
        self.client_combo.setPlaceholderText("Select Client")
        self.client_combo.setFixedHeight(35)
        self.refresh_clients()
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Project Name")
        self.name_input.setFixedHeight(35)
        
        self.add_btn = QPushButton("CREATE PROJECT")
        self.add_btn.setStyleSheet("background-color: #00ccff; color: black; font-weight: bold;")
        self.add_btn.clicked.connect(self.create_project)
        
        create_layout.addWidget(self.client_combo)
        create_layout.addWidget(self.name_input)
        create_layout.addWidget(self.add_btn)
        self.layout.addLayout(create_layout)

        # Projects Table
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["ID", "Client", "Project Name"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setVisible(True)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #2b2b2b;
                gridline-color: #3d3d3d;
                color: #f0f0f0;
            }
            QHeaderView::section {
                background-color: #1e1e1e;
                color: #00ccff;
                padding: 10px;
                font-weight: bold;
                border: 1px solid #3d3d3d;
            }
        """)
        self.layout.addWidget(self.table)
        
        self.refresh_table()

    def refresh_clients(self):
        self.client_combo.clear()
        conn = db_manager.get_connection()
        clients = conn.execute("SELECT id, name FROM clients").fetchall()
        for c in clients:
            self.client_combo.addItem(c['name'], c['id'])

    def create_project(self):
        name = self.name_input.text()
        client_id = self.client_combo.currentData()
        if not name or not client_id: 
            QMessageBox.warning(self, "Input Error", "Please provide a project name and select a client.")
            return
        
        try:
            conn = db_manager.get_connection()
            conn.execute("INSERT INTO projects (name, client_id) VALUES (?, ?)", (name, client_id))
            conn.commit()
            db_manager.log_action("Project Created", f"Name: {name} | Client ID: {client_id}")
            self.name_input.clear()
            self.refresh_table()
            QMessageBox.information(self, "Success", f"Project '{name}' created.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create project: {str(e)}")

    def refresh_table(self):
        self.table.setRowCount(0)
        self.refresh_clients()
        conn = db_manager.get_connection()
        projs = conn.execute("""
            SELECT p.id, p.name, c.name as client_name 
            FROM projects p 
            JOIN clients c ON p.client_id = c.id
        """).fetchall()
        for p in projs:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(p['id'])))
            self.table.setItem(row, 1, QTableWidgetItem(p['client_name']))
            self.table.setItem(row, 2, QTableWidgetItem(p['name']))
