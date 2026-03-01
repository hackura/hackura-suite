import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from PySide6.QtCore import QTimer
from ui.main_window import MainWindow
from ui.splash import HackuraSplashScreen
from ui.lock import LockScreen
from ui.setup import SetupWizard
from core.security import EncryptionVault
import core.security as security
from core.db import db_manager
from PySide6.QtWidgets import QMessageBox

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Hackura Pentest Suite")
    
    # Show Splash Screen
    splash = HackuraSplashScreen()
    splash.show()

    def start_app():
        splash.hide()
        is_configured = db_manager.get_setting("is_configured") == "true"
        
        if not is_configured:
            global setup_wizard
            setup_wizard = SetupWizard()
            setup_wizard.finished.connect(finish_unlock)
            setup_wizard.show()
        else:
            global lock_screen
            lock_screen = LockScreen()
            lock_screen.unlocked.connect(finish_unlock)
            lock_screen.show()

    def finish_unlock(password):
        # Initialize Security Vault
        v = EncryptionVault(password)
        
        # Verify if existing setup
        canary = db_manager.get_setting("vault_canary")
        if canary and not v.verify_canary(canary):
            # If we have a local lock screen, update its status
            if 'lock_screen' in globals():
                lock_screen.status.setText("INVALID PASSCODE")
                lock_screen.status.setStyleSheet("color: #ff3333;")
            return

        security.vault = v
        
        # Try Cloud DB if configured
        cloud_url = db_manager.get_setting("cloud_db_url", is_secret=True)
        if cloud_url:
            db_manager.setup_cloud(cloud_url, callback=lambda success: window.update_cloud_indicator() if 'window' in globals() else None)
        
        db_manager.log_action("Suite Unlocked", "Professional Authentication Successful")
        
        global window
        window = MainWindow()
        # Branding
        icon_path = os.path.join(os.path.dirname(__file__), "assets", "logo.png")
        if os.path.exists(icon_path):
            window.setWindowIcon(QIcon(icon_path))
        window.show()
        
        if 'lock_screen' in globals(): lock_screen.close()
        if 'setup_wizard' in globals(): setup_wizard.close()
        splash.finish(window)

    # Transition after 2.5 seconds
    QTimer.singleShot(2500, start_app)
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
