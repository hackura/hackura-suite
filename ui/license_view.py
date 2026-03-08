from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, 
    QLabel, QFrame, QMessageBox
)
from PySide6.QtCore import Qt
from core.security import license_manager

class LicenseView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        
        self.card = QFrame()
        self.card.setStyleSheet("background-color: #1e1e1e; border: 1px solid #333; border-radius: 8px;")
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(30, 30, 30, 30)
        card_layout.setSpacing(20)
        
        self.title = QLabel("HACKURA PRO ACTIVATION")
        self.title.setStyleSheet("font-size: 20px; font-weight: bold; color: #00ccff;")
        self.title.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(self.title)
        
        self.desc = QLabel(f"Your unique Machine ID is: <b>{license_manager.get_machine_id()}</b><br><br>Enter your Hackura Pro license key to unlock advanced modules like AI Exploit Generation, Malware Lab, and Professional Reporting.")
        self.desc.setWordWrap(True)
        self.desc.setStyleSheet("color: #aaa; font-size: 13px;")
        card_layout.addWidget(self.desc)
        
        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("HACK-XXXX-XXXX-XXXX")
        self.key_input.setFixedHeight(45)
        self.key_input.setStyleSheet("font-size: 16px; color: #fff; padding-left: 15px;")
        card_layout.addWidget(self.key_input)
        
        self.activate_btn = QPushButton("ACTIVATE LICENSE")
        self.activate_btn.setFixedHeight(50)
        self.activate_btn.setStyleSheet("background-color: #00ccff; color: black; font-weight: bold;")
        self.activate_btn.clicked.connect(self.run_activation)
        card_layout.addWidget(self.activate_btn)
        
        self.status_lbl = QLabel("TRIAL VERSION")
        self.status_lbl.setAlignment(Qt.AlignCenter)
        self.status_lbl.setStyleSheet("color: #ffaa00; font-weight: bold;")
        card_layout.addWidget(self.status_lbl)
        
        layout.addWidget(self.card)
        layout.addStretch()
        
        self.update_status()

    def update_status(self):
        if license_manager.is_pro():
            self.status_lbl.setText("✓ PRO EDITION ACTIVATED")
            self.status_lbl.setStyleSheet("color: #00ff00; font-weight: bold;")
            self.activate_btn.setEnabled(False)
            self.key_input.setEnabled(False)
            self.key_input.setText(license_manager.license_key)
        else:
            self.status_lbl.setText("TRIAL VERSION")
            self.status_lbl.setStyleSheet("color: #ffaa00; font-weight: bold;")

    def run_activation(self):
        key = self.key_input.text().strip()
        if license_manager.validate_key(key):
            QMessageBox.information(self, "Success", "Hackura Pro has been successfully activated!")
            self.update_status()
            # In a real app, we'd trigger a UI refresh of the main window here
        else:
            QMessageBox.warning(self, "Invalid Key", "The license key provided is invalid for this machine ID.")
