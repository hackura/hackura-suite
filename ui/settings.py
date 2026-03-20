from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QLineEdit, QComboBox, QFormLayout, QGroupBox, QMessageBox
)
import os
from core.db import db_manager

class SettingsView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(40, 40, 40, 40)

        header = QLabel("System Settings")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #00ccff;")
        self.layout.addWidget(header)

        # General Settings
        gen_group = QGroupBox("General")
        gen_layout = QFormLayout(gen_group)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark (Kali)", "Light (Professional)"])
        self.theme_combo.setCurrentText(db_manager.get_setting("theme", "Dark (Kali)"))
        self.theme_combo.currentTextChanged.connect(self.on_theme_changed)
        gen_layout.addRow("Application Theme:", self.theme_combo)
        
        self.layout.addWidget(gen_group)

        # Cloud API & Persistence
        cloud_group = QGroupBox("Cloud & Security Architecture")
        cloud_layout = QFormLayout(cloud_group)
        
        self.cloud_url = QLineEdit()
        self.cloud_url.setPlaceholderText("Postgres/Supabase Connection String")
        self.cloud_url.setEchoMode(QLineEdit.Password)
        self.cloud_url.setText(db_manager.get_setting("cloud_db_url", "", is_secret=True))
        cloud_layout.addRow("Cloud DB Link:", self.cloud_url)

        self.aws_key = QLineEdit()
        self.aws_key.setEchoMode(QLineEdit.Password)
        self.aws_key.setText(db_manager.get_setting("aws_key", "", is_secret=True))
        cloud_layout.addRow("AWS Access Key:", self.aws_key)

        self.azure_key = QLineEdit()
        self.azure_key.setEchoMode(QLineEdit.Password)
        self.azure_key.setText(db_manager.get_setting("azure_key", "", is_secret=True))
        cloud_layout.addRow("Azure Client Secret:", self.azure_key)
        
        self.save_btn = QPushButton("SAVE & SYNC CLOUD VAULT")
        self.save_btn.setFixedHeight(40)
        self.save_btn.setStyleSheet("background-color: #00ccff; color: black; font-weight: bold;")
        self.save_btn.clicked.connect(self.save_security_settings)
        cloud_layout.addRow("", self.save_btn)
        
        self.layout.addWidget(cloud_group)

        # Tool Paths
        tool_group = QGroupBox("External Tool Paths")
        tool_layout = QFormLayout(tool_group)
        
        self.nmap_path = QLineEdit()
        self.nmap_path.setPlaceholderText("Auto-detecting...")
        self.nmap_path.setText(db_manager.get_setting("nmap_path", ""))
        self.nmap_path.textChanged.connect(lambda v: db_manager.set_setting("nmap_path", v))
        tool_layout.addRow("Nmap Path:", self.nmap_path)
        
        self.layout.addWidget(tool_group)
        
        # Unified API Vault
        vault_group = QGroupBox("Security API Vault")
        vault_layout = QFormLayout(vault_group)
        
        # Reconnaissance Section
        recon_hdr = QLabel("RECONNAISSANCE & OSINT")
        recon_hdr.setStyleSheet("color: #888; font-weight: bold; font-size: 10px; margin-top: 10px;")
        vault_layout.addRow(recon_hdr)
        
        self.shodan_key = QLineEdit()
        self.shodan_key.setPlaceholderText("Shodan.io API Key")
        self.shodan_key.setEchoMode(QLineEdit.Password)
        self.shodan_key.setText(db_manager.get_setting("shodan_api_key", "", is_secret=True))
        vault_layout.addRow("Shodan API Key:", self.shodan_key)

        # Threat Intelligence Section
        intel_hdr = QLabel("THREAT INTELLIGENCE FEEDS")
        intel_hdr.setStyleSheet("color: #888; font-weight: bold; font-size: 10px; margin-top: 15px;")
        vault_layout.addRow(intel_hdr)

        self.otx_key = QLineEdit()
        self.otx_key.setPlaceholderText("AlienVault OTX API Key")
        self.otx_key.setEchoMode(QLineEdit.Password)
        self.otx_key.setText(db_manager.get_setting("otx_api_key", "", is_secret=True))
        vault_layout.addRow("AlienVault OTX Key:", self.otx_key)

        self.honeydb_key = QLineEdit()
        self.honeydb_key.setPlaceholderText("HoneyDB.io API Key")
        self.honeydb_key.setEchoMode(QLineEdit.Password)
        self.honeydb_key.setText(db_manager.get_setting("honeydb_api_key", "", is_secret=True))
        vault_layout.addRow("HoneyDB API Key:", self.honeydb_key)

        self.intel_key = QLineEdit()
        self.intel_key.setPlaceholderText("Universal/Custom Intel Key")
        self.intel_key.setEchoMode(QLineEdit.Password)
        self.intel_key.setText(db_manager.get_setting("intel_api_key", "", is_secret=True))
        vault_layout.addRow("Universal Intel Key:", self.intel_key)

        # Provider Logic Header (below keys but in vault group)
        self.intel_provider = QComboBox()
        self.intel_provider.addItems(["Simulated Intelligence (Internal AI)", "AlienVault OTX", "HoneyDB Live Feed", "Multi-Source Aggregator"])
        self.intel_provider.setCurrentText(db_manager.get_setting("intel_provider", "Simulated Intelligence (Internal AI)"))
        vault_layout.addRow("Active Intelligence Focus:", self.intel_provider)

        self.save_vault_btn = QPushButton("SAVE VAULT CREDENTIALS")
        self.save_vault_btn.setFixedHeight(40)
        self.save_vault_btn.setStyleSheet("background-color: #ffaa00; color: black; font-weight: bold;")
        self.save_vault_btn.clicked.connect(self.save_vault_settings)
        vault_layout.addRow("", self.save_vault_btn)
        
        self.layout.addWidget(vault_group)

        # Maintenance Tools
        maint_group = QGroupBox("Suite Maintenance")
        maint_layout = QVBoxLayout(maint_group)
        
        btn_layout = QHBoxLayout()
        self.clean_cache_btn = QPushButton("CLEAR LOGO CACHE")
        self.clean_cache_btn.clicked.connect(self.clear_logo_cache)
        
        self.prune_logs_btn = QPushButton("PRUNE AUDIT LOGS")
        self.prune_logs_btn.clicked.connect(self.prune_audit_logs)
        
        self.optimize_btn = QPushButton("OPTIMIZE DATABASE")
        self.optimize_btn.clicked.connect(self.optimize_db)
        
        self.clear_projs_btn = QPushButton("CLEAR ALL PROJECTS")
        self.clear_projs_btn.setStyleSheet("color: #ffaa00;")
        self.clear_projs_btn.clicked.connect(self.clear_all_projects)
        
        self.factory_reset_btn = QPushButton("FACTORY RESET")
        self.factory_reset_btn.setStyleSheet("color: #ff3333; font-weight: bold;")
        self.factory_reset_btn.clicked.connect(self.perform_factory_reset)
        
        btn_layout.addWidget(self.clean_cache_btn)
        btn_layout.addWidget(self.prune_logs_btn)
        btn_layout.addWidget(self.optimize_btn)
        btn_layout.addWidget(self.clear_projs_btn)
        btn_layout.addWidget(self.factory_reset_btn)
        maint_layout.addLayout(btn_layout)
        
        self.layout.addWidget(maint_group)

        self.layout.addStretch()

    def save_security_settings(self):
        db_manager.set_setting("cloud_db_url", self.cloud_url.text(), is_secret=True)
        db_manager.set_setting("aws_key", self.aws_key.text(), is_secret=True)
        db_manager.set_setting("azure_key", self.azure_key.text(), is_secret=True)
        
        # Immediate sync attempt if URL is provided
        if self.cloud_url.text():
            if db_manager.setup_cloud(self.cloud_url.text()):
                db_manager.log_action("Cloud DB Synced", "Manual cloud synchronization successful")
                QMessageBox.information(self, "Success", "Cloud DB Linked & Synchronized!")
            else:
                QMessageBox.warning(self, "Sync Issue", "Settings saved locally, but Cloud DB connection failed.")
        else:
            QMessageBox.information(self, "Success", "Security settings updated locally.")

    def save_vault_settings(self):
        db_manager.set_setting("shodan_api_key", self.shodan_key.text(), is_secret=True)
        db_manager.set_setting("otx_api_key", self.otx_key.text(), is_secret=True)
        db_manager.set_setting("honeydb_api_key", self.honeydb_key.text(), is_secret=True)
        db_manager.set_setting("intel_api_key", self.intel_key.text(), is_secret=True)
        db_manager.set_setting("intel_api_key", self.intel_key.text(), is_secret=True)
        db_manager.set_setting("intel_provider", self.intel_provider.currentText())
        
        db_manager.log_action("API Vault Updated", "Shodan/OTX/HoneyDB/Intel keys refreshed")
        QMessageBox.information(self, "Security Vault", "API credentials have been encrypted and saved successfully.")

    def on_theme_changed(self, theme_v):
        db_manager.set_setting("theme", theme_v)
        # Refresh main window stylesheet
        from PySide6.QtWidgets import QApplication
        for widget in QApplication.topLevelWidgets():
            if hasattr(widget, "apply_styles"):
                widget.apply_styles(theme_v)

    def clear_logo_cache(self):
        import shutil
        path = os.path.join(os.path.expanduser("~"), "HackuraSuite", "assets", "clients")
        if os.path.exists(path):
            shutil.rmtree(path)
            os.makedirs(path)
            db_manager.log_action("Maintenance", "Logo cache cleared")
            QMessageBox.information(self, "Maintenance", "Logo cache successfully cleared.")

    def prune_audit_logs(self):
        db_manager.prune_logs()
        QMessageBox.information(self, "Maintenance", "Audit logs pruned to last 30 days.")

    def optimize_db(self):
        db_manager.vacuum()
        QMessageBox.information(self, "Maintenance", "Database vacuum and optimization complete.")

    def clear_all_projects(self):
        reply = QMessageBox.question(self, "Confirm Reset", "Are you sure you want to delete ALL projects, scans, and findings? This cannot be undone.", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            db_manager.clear_projects()
            QMessageBox.information(self, "Reset Complete", "All project data has been cleared.")

    def perform_factory_reset(self):
        reply = QMessageBox.critical(self, "FACTORY RESET", "WARNING: This will wipe ALL data, including clients, settings, and your vault passcode. The app will restart in Setup mode. Continue?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            db_manager.factory_reset()
            QMessageBox.information(self, "Reset Complete", "Factory reset successful. The application will now close. Please restart it to begin setup.")
            from PySide6.QtWidgets import QApplication
            QApplication.quit()
