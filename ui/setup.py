from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QLineEdit, QStackedWidget, QFrame, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon
import os
from core.db import db_manager
from core.security import EncryptionVault
import core.security as security

class SetupWizard(QWidget):
    finished = Signal(str) # Emits passcode on success

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hackura Suite Setup")
        self.setFixedSize(500, 400)
        self.setStyleSheet("background-color: #1e1e1e; color: white;")
        
        self.layout = QVBoxLayout(self)
        self.stack = QStackedWidget()
        self.layout.addWidget(self.stack)
        
        self.init_welcome_page()
        self.init_passcode_page()
        self.init_final_page()

    def init_welcome_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignCenter)
        
        logo = QLabel()
        icon = QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "logo.png"))
        logo.setPixmap(icon.pixmap(100, 100))
        layout.addWidget(logo, alignment=Qt.AlignCenter)
        
        title = QLabel("WELCOME TO HACKURA")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #00ccff;")
        layout.addWidget(title, alignment=Qt.AlignCenter)
        
        desc = QLabel("Let's configure your professional pentesting environment.")
        desc.setStyleSheet("color: #888;")
        layout.addWidget(desc, alignment=Qt.AlignCenter)
        
        btn = QPushButton("GET STARTED")
        btn.setFixedHeight(40)
        btn.setStyleSheet("background-color: #00ccff; color: black; font-weight: bold; margin-top: 20px;")
        btn.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        layout.addWidget(btn)
        
        self.stack.addWidget(page)

    def init_passcode_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 40, 40, 40)
        
        layout.addWidget(QLabel("CREATE MASTER PASSCODE"))
        layout.addWidget(QLabel("This passcode will encrypt your local vault and API keys."))
        
        self.pass1 = QLineEdit()
        self.pass1.setPlaceholderText("New Passcode")
        self.pass1.setEchoMode(QLineEdit.Password)
        self.pass1.setFixedHeight(35)
        layout.addWidget(self.pass1)
        
        self.pass2 = QLineEdit()
        self.pass2.setPlaceholderText("Confirm Passcode")
        self.pass2.setEchoMode(QLineEdit.Password)
        self.pass2.setFixedHeight(35)
        layout.addWidget(self.pass2)
        
        btn = QPushButton("INITIALIZE SECURITY VAULT")
        btn.setFixedHeight(40)
        btn.setStyleSheet("background-color: #00ccff; color: black; font-weight: bold;")
        btn.clicked.connect(self.validate_passcode)
        layout.addWidget(btn)
        
        self.stack.addWidget(page)

    def init_final_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(QLabel("SETUP COMPLETE"))
        layout.addWidget(QLabel("Your Hackura Suite is now ready for professional use."))
        
        btn = QPushButton("LAUNCH HACKURA SUITE")
        btn.setFixedHeight(40)
        btn.setStyleSheet("background-color: #00ff00; color: black; font-weight: bold;")
        btn.clicked.connect(lambda: self.finished.emit(self.pass1.text()))
        layout.addWidget(btn)
        
        self.stack.addWidget(page)

    def validate_passcode(self):
        p1 = self.pass1.text()
        p2 = self.pass2.text()
        
        if len(p1) < 4:
            QMessageBox.warning(self, "Insecure", "Passcode must be at least 4 characters.")
            return
        if p1 != p2:
            QMessageBox.warning(self, "Mismatch", "Passcodes do not match.")
            return
            
        # Initialize the canary in DB
        v = EncryptionVault(p1)
        security.vault = v
        canary = v.get_canary()
        db_manager.set_setting("vault_canary", canary)
        db_manager.set_setting("is_configured", "true")
        
        self.stack.setCurrentIndex(2)
