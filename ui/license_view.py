from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, 
    QLabel, QFrame, QMessageBox, QStackedWidget
)
from PySide6.QtCore import Qt
from core.security import license_manager
from core.paystack_engine import paystack_engine
import webbrowser

class LicenseView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(40, 40, 40, 40)
        
        self.stack = QStackedWidget()
        self.layout.addWidget(self.stack)
        
        self.init_trial_view()
        self.init_pro_view()
        
        self.update_status()

    def init_trial_view(self):
        self.trial_widget = QWidget()
        layout = QVBoxLayout(self.trial_widget)
        
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
        
        # Feature Comparison Table
        comparison_table = QLabel()
        comparison_table.setText("""
            <table width='100%' style='border-collapse: collapse; color: #eee; font-size: 13px;'>
                <tr style='background-color: #252525;'>
                    <th style='padding: 10px; border: 1px solid #333;'>Feature</th>
                    <th style='padding: 10px; border: 1px solid #333;'>Trial</th>
                    <th style='padding: 10px; border: 1px solid #333; color: #ff00ff;'>Pro</th>
                </tr>
                <tr>
                    <td style='padding: 10px; border: 1px solid #333;'>Core Scanners</td>
                    <td style='padding: 10px; border: 1px solid #333; color: #00ff00;'>✓</td>
                    <td style='padding: 10px; border: 1px solid #333; color: #00ff00;'>✓</td>
                </tr>
                <tr>
                    <td style='padding: 10px; border: 1px solid #333;'>AI Exploit Gen</td>
                    <td style='padding: 10px; border: 1px solid #333; color: #ff3333;'>✗</td>
                    <td style='padding: 10px; border: 1px solid #333; color: #00ff00;'>✓</td>
                </tr>
                <tr>
                    <td style='padding: 10px; border: 1px solid #333;'>EDR Evasion Lab</td>
                    <td style='padding: 10px; border: 1px solid #333; color: #ff3333;'>✗</td>
                    <td style='padding: 10px; border: 1px solid #333; color: #00ff00;'>✓</td>
                </tr>
                <tr>
                    <td style='padding: 10px; border: 1px solid #333;'>PDF Reporting</td>
                    <td style='padding: 10px; border: 1px solid #333; color: #ffaa00;'>Basic</td>
                    <td style='padding: 10px; border: 1px solid #333; color: #00ff00;'>Pro Tier</td>
                </tr>
                <tr>
                    <td style='padding: 10px; border: 1px solid #333;'>Cloud Sync</td>
                    <td style='padding: 10px; border: 1px solid #333; color: #ff3333;'>✗</td>
                    <td style='padding: 10px; border: 1px solid #333; color: #00ff00;'>✓</td>
                </tr>
            </table>
        """)
        comparison_table.setStyleSheet("border: 1px solid #333; border-radius: 4px; padding: 10px;")
        card_layout.addWidget(comparison_table)

        self.status_lbl = QLabel("TRIAL VERSION")
        self.status_lbl.setAlignment(Qt.AlignCenter)
        self.status_lbl.setStyleSheet("color: #ffaa00; font-weight: bold;")
        card_layout.addWidget(self.status_lbl)

        # Paystack Integration
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("background-color: #333;")
        card_layout.addWidget(sep)

        self.paystack_btn = QPushButton("PAY NOW (250 GHS / YEAR)")
        self.paystack_btn.setFixedHeight(50)
        self.paystack_btn.setStyleSheet("background-color: #ff00ff; color: white; font-weight: bold;")
        self.paystack_btn.clicked.connect(self.initialize_paystack)
        card_layout.addWidget(self.paystack_btn)

        self.check_btn = QPushButton("CHECK SUBSCRIPTION STATUS")
        self.check_btn.setStyleSheet("background-color: #333; color: #888;")
        self.check_btn.clicked.connect(self.check_status)
        card_layout.addWidget(self.check_btn)
        
        layout.addWidget(self.card)
        layout.addStretch()
        self.stack.addWidget(self.trial_widget)

    def init_pro_view(self):
        self.pro_widget = QWidget()
        layout = QVBoxLayout(self.pro_widget)
        
        # Professional Dashboard Layout
        header = QFrame()
        header.setFixedHeight(60)
        header.setStyleSheet("background: #003300; border-radius: 8px; border: 1px solid #00ff00;")
        h_layout = QHBoxLayout(header)
        
        status_icon = QLabel("PRO")
        status_icon.setStyleSheet("background: #00ff00; color: black; font-weight: bold; border-radius: 4px; padding: 5px 10px; border: none;")
        h_layout.addWidget(status_icon)
        
        title = QLabel("HACKURA PROFESSIONAL EDITION")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: white; border: none;")
        h_layout.addWidget(title)
        h_layout.addStretch()
        layout.addWidget(header)
        
        # Content Cards
        content_layout = QHBoxLayout()
        
        left_card = QFrame()
        left_card.setStyleSheet("background: #1a1a1a; border: 1px solid #333; border-radius: 8px;")
        lc_layout = QVBoxLayout(left_card)
        lc_layout.addWidget(QLabel("LICENSE DATA"))
        self.key_display = QLabel("Key: ...")
        lc_layout.addWidget(self.key_display)
        lc_layout.addWidget(QLabel(f"System ID: {license_manager.get_machine_id()}"))
        lc_layout.addWidget(QLabel("Status: Life-Time Professional"))
        content_layout.addWidget(left_card)
        
        right_card = QFrame()
        right_card.setStyleSheet("background: #1a1a1a; border: 1px solid #333; border-radius: 8px;")
        rc_layout = QVBoxLayout(right_card)
        rc_layout.addWidget(QLabel("AUTHORIZED MODULES"))
        modules = ["AI Exploit Gen", "Malware Lab", "Cloud Auditor", "K8s Overseer", "C2 Persistor"]
        for m in modules:
            rc_layout.addWidget(QLabel(f"✓ {m}"))
        content_layout.addWidget(right_card)
        
        layout.addLayout(content_layout)
        layout.addStretch()
        self.stack.addWidget(self.pro_widget)

    def update_status(self):
        if license_manager.is_pro():
            self.key_display.setText(f"Key: {license_manager.license_key or 'MASTER BYPASS (Karl)'}")
            self.stack.setCurrentIndex(1)
        else:
            self.stack.setCurrentIndex(0)

    def run_activation(self):
        key = self.key_input.text().strip()
        if license_manager.validate_key(key):
            QMessageBox.information(self, "Success", "Hackura Pro has been successfully activated!")
            self.update_status()
        else:
            QMessageBox.warning(self, "Invalid Key", "The license key provided is invalid for this machine ID.")

    def initialize_paystack(self):
        m_id = license_manager.get_machine_id()
        # Mock email for now or ask user if needed. In a real app, you'd have an account system.
        email = "user@hackura.com" 
        
        self.paystack_btn.setEnabled(False)
        self.paystack_btn.setText("INITIALIZING SECURE CHECKOUT...")
        
        res = paystack_engine.initialize_transaction(email, 250.0, m_id)
        
        self.paystack_btn.setEnabled(True)
        self.paystack_btn.setText("PAY NOW (250 GHS / YEAR)")
        
        if res.get("success"):
            QMessageBox.information(self, "Checkout Ready", "Opening secure Paystack checkout in your browser. After payment is complete, click 'Check Status'.")
            webbrowser.open(res["checkout_url"])
        else:
            QMessageBox.critical(self, "Error", f"Failed to connect to Hackura billing server: {res.get('error')}")

    def check_status(self):
        if license_manager.check_subscription_status():
            QMessageBox.information(self, "Pro Active", "Payment verified! Hackura Pro is now active.")
            self.update_status()
        else:
            QMessageBox.warning(self, "Still Trial", "No active subscription found for this machine. If you just paid, please wait a minute for the webhook to process.")
