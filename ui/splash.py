from PySide6.QtWidgets import QSplashScreen, QLabel, QVBoxLayout, QWidget
from PySide6.QtGui import QPixmap, QColor, QIcon
from PySide6.QtCore import Qt, QTimer
import os

class HackuraSplashScreen(QSplashScreen):
    def __init__(self):
        # Create a professional styled pixmap for splash
        pixmap = QPixmap(600, 400)
        pixmap.fill(QColor("#1e1e1e"))
        
        super().__init__(pixmap)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        
        # Overlay Layout for custom text
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        
        # Logo
        logo_lbl = QLabel()
        logo_pix = QPixmap(os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "logo.png"))
        if not logo_pix.isNull():
            logo_lbl.setPixmap(logo_pix.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        layout.addWidget(logo_lbl, alignment=Qt.AlignCenter)
        
        # App Name
        title = QLabel("HACKURA SUITE")
        title.setStyleSheet("font-size: 32px; font-weight: bold; color: #00ccff; margin-top: 20px;")
        layout.addWidget(title, alignment=Qt.AlignCenter)
        
        # Signature
        sub = QLabel("Professional Pentesting & Security Assessments")
        sub.setStyleSheet("color: #888; font-size: 14px;")
        layout.addWidget(sub, alignment=Qt.AlignCenter)
        
        signature = QLabel("Built by Hackura Consult")
        signature.setStyleSheet("color: #00ff00; font-weight: bold; margin-top: 40px; font-family: monospace;")
        layout.addWidget(signature, alignment=Qt.AlignTop | Qt.AlignRight)
        
        self.showMessage("Initializing Security Core...", Qt.AlignBottom | Qt.AlignCenter, QColor("#888"))

    def set_loading_message(self, message):
        self.showMessage(message, Qt.AlignBottom | Qt.AlignCenter, QColor("#888"))
