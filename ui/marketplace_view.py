from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QFrame, QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit, QMessageBox
)
from PySide6.QtCore import Qt, QDateTime
from core.plugin_manager import plugin_manager

class PluginMarketplaceView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(40, 40, 40, 40)
        self.layout.setSpacing(20)

        # Header Row
        header_layout = QHBoxLayout()
        header = QLabel("Hackura Plugin Marketplace")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #ff00ff; text-shadow: 0 0 10px #ff00ff;")
        header_layout.addWidget(header)
        
        header_layout.addStretch()
        
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #888; font-style: italic;")
        header_layout.addWidget(self.status_label)
        
        self.refresh_btn = QPushButton("REFRESH MARKETPLACE")
        self.refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #ff00ff;
                border: 1px solid #ff00ff;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ff00ff11;
            }
        """)
        self.refresh_btn.clicked.connect(self.sync_plugins)
        header_layout.addWidget(self.refresh_btn)
        
        self.layout.addLayout(header_layout)

        # Marketplace List
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["Plugin Name", "Category", "Version", "Rating", "Status", "Actions"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #1a1a1a;
                gridline-color: #333;
                color: #ccc;
                border: 1px solid #333;
            }
            QHeaderView::section {
                background-color: #222;
                color: #ff00ff;
                padding: 10px;
                border: 1px solid #333;
                font-weight: bold;
            }
        """)
        self.layout.addWidget(self.table)
        
        self.load_plugins()

    def sync_plugins(self):
        self.status_label.setText("Syncing...")
        self.refresh_btn.setEnabled(False)
        
        if plugin_manager.sync_remote_plugins():
            self.status_label.setText(f"Last Sync: {QDateTime.currentDateTime().toString('HH:mm:ss')}")
            self.load_plugins()
        else:
            self.status_label.setText("Sync Failed")
            QMessageBox.warning(self, "Marketplace", "Failed to sync with remote repository.")
        
        self.refresh_btn.setEnabled(True)

    def load_plugins(self):
        plugins = plugin_manager.get_plugins()
        
        self.table.setRowCount(0)
        for p in plugins:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(p["name"]))
            self.table.setItem(row, 1, QTableWidgetItem(p["category"]))
            self.table.setItem(row, 2, QTableWidgetItem(p["version"]))
            self.table.setItem(row, 3, QTableWidgetItem("⭐" * p["rating"]))
            self.table.setItem(row, 4, QTableWidgetItem(p["status"]))

            install_btn = QPushButton("INSTALL" if p['status'] == 'Available' else "INSTALLED")
            install_btn.setEnabled(p['status'] == 'Available')
            if p['status'] == 'Available':
                install_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #ff00ff; 
                        color: black; 
                        font-weight: bold; 
                        border-radius: 2px;
                        padding: 5px;
                    }
                    QPushButton:hover {
                        background-color: #d400d4;
                    }
                """)
                install_btn.clicked.connect(lambda checked, pid=p['id']: self.run_install(pid))
            else:
                install_btn.setStyleSheet("background-color: #333; color: #555; border: none; padding: 5px;")
            
            self.table.setCellWidget(row, 5, install_btn)

    def run_install(self, plugin_id):
        if plugin_manager.install_plugin(plugin_id):
            QMessageBox.information(self, "Marketplace", f"Plugin {plugin_id} installed successfully! Restart app to activate.")
            self.load_plugins()

    def refresh_projects(self): pass
