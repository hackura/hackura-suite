from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QFrame
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QIcon
import os

class LockScreen(QWidget):
    unlocked = Signal(str) # Password emitted

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hackura Vault - Locked")
        self.setFixedSize(400, 500)
        self.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint | Qt.WindowStaysOnTopHint)
        self.setStyleSheet("background-color: #1e1e1e; color: white;")

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)

        # Logo
        logo_lbl = QLabel()
        icon = QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "logo.png"))
        logo_lbl.setPixmap(icon.pixmap(120, 120))
        logo_lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo_lbl)

        title = QLabel("VAULT LOCKED")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #ff3333;")
        layout.addWidget(title)

        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Enter Unlock Passcode")
        self.pass_input.setEchoMode(QLineEdit.Password)
        self.pass_input.setFixedHeight(40)
        self.pass_input.setStyleSheet("""
            QLineEdit {
                background-color: #2b2b2b;
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                padding: 5px;
                font-size: 16px;
                text-align: center;
            }
            QLineEdit:focus { border-color: #00ccff; }
        """)
        self.pass_input.returnPressed.connect(self.attempt_unlock)
        layout.addWidget(self.pass_input)

        self.unlock_btn = QPushButton("UNLOCK SUITE")
        self.unlock_btn.setFixedHeight(40)
        self.unlock_btn.setStyleSheet("""
            QPushButton {
                background-color: #00ccff;
                color: black;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #00b3e6; }
        """)
        self.unlock_btn.clicked.connect(self.attempt_unlock)
        layout.addWidget(self.unlock_btn)

        self.status = QLabel("Authorization Required")
        self.status.setStyleSheet("color: #888;")
        layout.addWidget(self.status)

    def attempt_unlock(self):
        password = self.pass_input.text()
        if not password: return
        
        # For this professional version, we emit the password
        # The main app will try to initialize the Vault with it
        self.unlocked.emit(password)
