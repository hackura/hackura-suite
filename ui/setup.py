from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QLineEdit, QStackedWidget, QFrame, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon
import os
from core.db import db_manager
from core.security import EncryptionVault, license_manager
from core.paystack_engine import paystack_engine
import core.security as security
from PySide6.QtGui import QIcon, QDesktopServices
from PySide6.QtCore import Qt, Signal, QUrl

class SetupWizard(QWidget):
    finished = Signal(str) # Emits passcode on success

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hackura Suite Deployment Wizard")
        self.setFixedSize(600, 500)
        self.setStyleSheet("background-color: #121212; color: white; font-family: 'Inter';")
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        self.stack = QStackedWidget()
        self.layout.addWidget(self.stack)
        
        self.init_welcome_page()
        self.init_identity_page()
        self.init_payment_page()
        self.init_final_page()

    def _create_page_frame(self):
        frame = QFrame()
        frame.setStyleSheet("background-color: #1e1e1e; border-top: 2px solid #00ccff;")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(50, 40, 50, 40)
        layout.setSpacing(20)
        return frame, layout

    def init_welcome_page(self):
        page, layout = self._create_page_frame()
        layout.setAlignment(Qt.AlignCenter)
        
        logo = QLabel()
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "logo.png")
        if os.path.exists(icon_path):
            logo.setPixmap(QIcon(icon_path).pixmap(120, 120))
        layout.addWidget(logo, alignment=Qt.AlignCenter)
        
        title = QLabel("HACKURA SUITE v2.0")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #00ccff; letter-spacing: 2px;")
        layout.addWidget(title, alignment=Qt.AlignCenter)
        
        desc = QLabel("Initialize your professional high-performance terminal. Your data will be locally encrypted using industry-standard AES-256.")
        desc.setWordWrap(True)
        desc.setAlignment(Qt.AlignCenter)
        desc.setStyleSheet("color: #aaa; font-size: 13px; line-height: 20px;")
        layout.addWidget(desc)
        
        btn = QPushButton("DEPLOY SYSTEM")
        btn.setFixedHeight(50)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet("background-color: #00ccff; color: black; font-weight: bold; font-size: 14px; border-radius: 4px;")
        btn.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        layout.addWidget(btn)
        
        self.stack.addWidget(page)

    def init_identity_page(self):
        page, layout = self._create_page_frame()
        
        title = QLabel("IDENTITY & SECURITY")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #00ccff;")
        layout.addWidget(title)
        
        layout.addWidget(QLabel("Operator Username:"))
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("e.g. Ghost_Operator")
        self.user_input.setFixedHeight(40)
        self.user_input.setStyleSheet("background: #252525; border: 1px solid #333; padding-left: 10px;")
        layout.addWidget(self.user_input)
        
        layout.addWidget(QLabel("Secure 6-Digit Passcode:"))
        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Numeric Only (e.g. 883921)")
        self.pass_input.setEchoMode(QLineEdit.Password)
        self.pass_input.setMaxLength(6)
        self.pass_input.setFixedHeight(40)
        self.pass_input.setStyleSheet("background: #252525; border: 1px solid #333; padding-left: 10px;")
        layout.addWidget(self.pass_input)
        
        layout.addWidget(QLabel("Operator Email (for Licensing):"))
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("operator@hackura.io")
        self.email_input.setFixedHeight(40)
        self.email_input.setStyleSheet("background: #252525; border: 1px solid #333; padding-left: 10px;")
        layout.addWidget(self.email_input)
        
        self.next_btn = QPushButton("VALIDATE CREDENTIALS")
        self.next_btn.setFixedHeight(50)
        self.next_btn.setStyleSheet("background-color: #00ccff; color: black; font-weight: bold;")
        self.next_btn.clicked.connect(self.process_identity)
        layout.addWidget(self.next_btn)
        
        self.stack.addWidget(page)

    def init_payment_page(self):
        page, layout = self._create_page_frame()
        
        title = QLabel("UNLOCK PRO CAPABILITIES")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #ffaa00;")
        layout.addWidget(title)
        
        features = [
            "✓ AI-Assisted Exploit Generation",
            "✓ Multi-Cloud Misconfiguration Scanner",
            "✓ Advanced EDR & AV Evasion Lab",
            "✓ Professional PDF Reporting Tier"
        ]
        feat_box = QFrame()
        feat_box.setStyleSheet("background: #151515; border: 1px solid #222; border-radius: 4px;")
        flayout = QVBoxLayout(feat_box)
        for f in features:
            l = QLabel(f)
            l.setStyleSheet("color: #00ff00; font-size: 12px; border: none;")
            flayout.addWidget(l)
        layout.addWidget(feat_box)
        
        price = QLabel("Standard License Fee: 50 GHS")
        price.setStyleSheet("font-size: 16px; font-weight: bold; color: white;")
        layout.addWidget(price, alignment=Qt.AlignCenter)
        
        self.pay_status = QLabel("Ready to secure your operator license.")
        self.pay_status.setStyleSheet("color: #888; font-size: 12px;")
        self.pay_status.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.pay_status)

        btn_layout = QHBoxLayout()
        self.pay_btn = QPushButton("PAY NOW")
        self.pay_btn.setFixedHeight(45)
        self.pay_btn.setStyleSheet("background-color: #ffaa00; color: black; font-weight: bold;")
        self.pay_btn.clicked.connect(self.initiate_paystack)
        
        self.verify_btn = QPushButton("VERIFY PAYMENT")
        self.verify_btn.setFixedHeight(45)
        self.verify_btn.setVisible(False)
        self.verify_btn.setStyleSheet("background-color: #00ff00; color: black; font-weight: bold;")
        self.verify_btn.clicked.connect(self.verify_paystack)

        self.skip_btn = QPushButton("CONTINUE WITH TRIAL")
        self.skip_btn.setFixedHeight(45)
        self.skip_btn.setStyleSheet("background-color: transparent; border: 1px solid #444; color: #888;")
        self.skip_btn.clicked.connect(lambda: self.stack.setCurrentIndex(3))
        
        btn_layout.addWidget(self.skip_btn)
        btn_layout.addWidget(self.pay_btn)
        btn_layout.addWidget(self.verify_btn)
        layout.addLayout(btn_layout)
        
        self.stack.addWidget(page)

    def initiate_paystack(self):
        email = self.email_input.text().strip()
        self.pay_status.setText("Connecting to Paystack...")
        self.pay_btn.setEnabled(False)
        
        m_id = license_manager.get_machine_id()
        res = paystack_engine.initialize_transaction(email, 50.0, m_id)
        if res["success"]:
            self.current_ref = res["reference"]
            QDesktopServices.openUrl(QUrl(res["authorization_url"]))
            self.pay_status.setText("Checkout opened in browser. Click VERIFY once paid.")
            self.pay_btn.setVisible(False)
            self.verify_btn.setVisible(True)
        else:
            self.pay_status.setText(f"Error: {res['error']}")
            self.pay_btn.setEnabled(True)

    def verify_paystack(self):
        self.pay_status.setText("Verifying transaction...")
        res = paystack_engine.verify_transaction(self.current_ref)
        if res["success"]:
            key = license_manager.generate_license_key()
            if license_manager.validate_key(key):
                QMessageBox.information(self, "Payment Successful", "Hackura PRO License issued successfully! Launching Suite.")
                self.stack.setCurrentIndex(3)
        else:
            QMessageBox.warning(self, "Payment Issue", res["error"])
            self.pay_status.setText("Payment not yet confirmed. Please complete checkout.")

    def init_final_page(self):
        page, layout = self._create_page_frame()
        layout.setAlignment(Qt.AlignCenter)
        
        icon = QLabel("✓")
        icon.setStyleSheet("font-size: 64px; color: #00ff00;")
        layout.addWidget(icon, alignment=Qt.AlignCenter)
        
        title = QLabel("SYSTEM CONFIGURED")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: white;")
        layout.addWidget(title, alignment=Qt.AlignCenter)
        
        self.final_btn = QPushButton("LAUNCH HACKURA SUITE")
        self.final_btn.setFixedHeight(50)
        self.final_btn.setStyleSheet("background-color: #00ff00; color: black; font-weight: bold;")
        self.final_btn.clicked.connect(self.finish_wizard)
        layout.addWidget(self.final_btn)
        
        self.stack.addWidget(page)

    def process_identity(self):
        user = self.user_input.text().strip()
        passcode = self.pass_input.text().strip()
        
        if not user:
            QMessageBox.warning(self, "Error", "Username is required.")
            return
        if len(passcode) != 6 or not passcode.isdigit():
            QMessageBox.warning(self, "Insecure", "Master Passcode must be exactly 6 digits.")
            return
        if "@" not in self.email_input.text():
            QMessageBox.warning(self, "Error", "A valid Operator Email is required for licensing.")
            return
            
        db_manager.set_setting("username", user)
        db_manager.set_setting("email", self.email_input.text())
        # Store passcode for finalization
        self.temp_pass = passcode
        
        if user == "Karl":
            self.stack.setCurrentIndex(3) # Skip payment
        else:
            self.stack.setCurrentIndex(2)

    def finish_wizard(self):
        # Initialize the canary in DB
        v = EncryptionVault(self.temp_pass)
        security.vault = v
        canary = v.get_canary()
        db_manager.set_setting("vault_canary", canary)
        db_manager.set_setting("is_configured", "true")
        
        self.finished.emit(self.temp_pass)
