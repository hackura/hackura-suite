from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QFrame
)
from PySide6.QtCore import Qt
from core.db import db_manager
from core.client_manager import ClientScraper
import os

class ClientView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(40, 40, 40, 40)
        self.scraper = ClientScraper()
        self.scraper.finished.connect(self.on_logo_scraped)

        header = QLabel("Client CRM & Authorization")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #00ccff;")
        self.layout.addWidget(header)

        # Add Client Form
        form_frame = QFrame()
        form_frame.setObjectName("CRMForm")
        form_layout = QHBoxLayout(form_frame)
        form_layout.setContentsMargins(15, 15, 15, 15)
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Client Name")
        self.name_input.setFixedHeight(35)

        self.website_input = QLineEdit()
        self.website_input.setPlaceholderText("Website (for logo scraping)")
        self.website_input.setFixedHeight(35)
        
        self.add_btn = QPushButton("ADD NEW CLIENT")
        self.add_btn.setFixedHeight(35)
        self.add_btn.setStyleSheet("background-color: #00ccff; color: black; font-weight: bold; padding: 0 20px;")
        self.add_btn.clicked.connect(self.add_client)
        
        form_layout.addWidget(self.name_input, 2) # Stretch factor 2
        form_layout.addWidget(self.website_input, 2) # Stretch factor 2
        form_layout.addWidget(self.add_btn, 1) # Stretch factor 1
        self.layout.addWidget(form_frame)

        # Client Table
        self.table = QTableWidget(0, 5) # Increased column count
        self.table.setHorizontalHeaderLabels(["Client Identity", "Domain/Website", "Authorization", "Logo Status", "Actions"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setVisible(True)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #2b2b2b;
                gridline-color: #3d3d3d;
                color: #f0f0f0;
                margin-top: 20px;
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

    def add_client(self):
        name = self.name_input.text()
        website = self.website_input.text()
        if not name: return
        
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO clients (name, website) VALUES (?, ?)",
            (name, website)
        )
        self.last_client_id = cursor.lastrowid
        conn.commit()
        
        if website:
            QMessageBox.information(self, "Scanning", f"Attempting to scrape logo for {name}...")
            storage_dir = os.path.join(os.path.expanduser("~"), "HackuraSuite", "assets", "clients")
            os.makedirs(storage_dir, exist_ok=True)
            self.scraper.scrape_logo(website, storage_dir)
        
        self.name_input.clear()
        self.website_input.clear()
        self.refresh_table()

    def on_logo_scraped(self, path):
        if path:
            conn = db_manager.get_connection()
            conn.execute("UPDATE clients SET logo_path = ? WHERE id = ?", (path, self.last_client_id))
            conn.commit()
            QMessageBox.information(self, "Success", "Client logo retrieved successfully!")
            self.refresh_table()

    def refresh_table(self):
        self.table.setRowCount(0)
        conn = db_manager.get_connection()
        clients = conn.execute("SELECT id, name, website, authorization_status, logo_path FROM clients").fetchall()
        for c in clients:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(c['name']))
            self.table.setItem(row, 1, QTableWidgetItem(c['website'] or "N/A"))
            status_item = QTableWidgetItem(c['authorization_status'])
            if c['authorization_status'] == 'AUTHORIZED':
                status_item.setForeground(Qt.green)
            else:
                status_item.setForeground(Qt.red)
            self.table.setItem(row, 2, status_item)
            logo_status = "Retrieved" if c['logo_path'] else "Missing"
            self.table.setItem(row, 3, QTableWidgetItem(logo_status))
            
            # Action Buttons
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(0, 0, 0, 0)
            action_layout.setSpacing(5)
            
            toggle_btn = QPushButton("TOGGLE AUTH")
            is_auth = c['authorization_status'] == 'AUTHORIZED'
            toggle_btn.setStyleSheet(f"""
                background-color: {'#444' if is_auth else '#00ccff'}; 
                color: {'#888' if is_auth else 'black'}; 
                font-weight: bold; border-radius: 2px;
            """)
            toggle_btn.clicked.connect(lambda checked, cid=c['id'], status=c['authorization_status']: self.toggle_auth(cid, status))
            
            delete_btn = QPushButton("REMOVE")
            delete_btn.setStyleSheet("background-color: #ff3333; color: white; font-weight: bold; border-radius: 2px;")
            delete_btn.clicked.connect(lambda checked, cid=c['id']: self.remove_client(cid))
            
            action_layout.addWidget(toggle_btn)
            action_layout.addWidget(delete_btn)
            self.table.setCellWidget(row, 4, action_widget)

    def toggle_auth(self, client_id, current_status):
        new_status = 'AUTHORIZED' if current_status == 'Pending' else 'Pending'
        msg = f"Change authorization for this client to {new_status}?"
        if QMessageBox.question(self, "Confirm Authorization", msg) == QMessageBox.Yes:
            conn = db_manager.get_connection()
            conn.execute("UPDATE clients SET authorization_status = ? WHERE id = ?", (new_status, client_id))
            conn.commit()
            db_manager.log_action("Authorization Changed", f"Client ID: {client_id} -> {new_status}")
            self.refresh_table()

    def remove_client(self, client_id):
        reply = QMessageBox.question(self, "Confirm Delete", "Are you sure you want to remove this client? All linked projects will be affected.", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            conn = db_manager.get_connection()
            conn.execute("DELETE FROM clients WHERE id = ?", (client_id,))
            conn.commit()
            db_manager.log_action("Client Removed", f"Client ID: {client_id}")
            self.refresh_table()
