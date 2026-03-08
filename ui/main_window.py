from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, 
    QStackedWidget, QLabel, QFrame, QScrollArea
)
from PySide6.QtCore import Qt
from ui.network import NetworkView
from ui.web import WebView
from ui.cloud import CloudView
from ui.exfiltrate import RedTeamView
from ui.api_view import APIFuzzerView
from ui.compliance_view import ComplianceView
from ui.reporting import ReportingView
from ui.settings import SettingsView
from ui.dashboard import DashboardView
from ui.console import ConsoleView
from ui.projects import ProjectView
from ui.clients import ClientView
from ui.audit import SecurityAuditView
from ui.monitoring import MonitoringView
from ui.blue_team import BlueTeamView
from ui.blue_dashboard import BlueDashboardView
from ui.credential_view import CredentialView
from ui.cloud_scanner_view import CloudScannerView
from ui.wireless_view import WirelessView
from ui.evasion_view import EvasionView
from ui.malware_view import MalwareView
from ui.k8s_view import K8sView
from ui.secrets_view import SecretsView
from ui.ai_exploit_view import AIExploitView
from ui.report_customizer import ReportCustomizerView
from ui.engagement_tracker import EngagementTrackerView
from ui.asset_tracker import AssetTrackerView
from ui.orchestrator_view import OrchestratorView
from ui.vuln_replay import VulnReplayView
from ui.sandbox_view import SandboxView
from ui.obfuscation_view import ObfuscationView
from ui.persistence_view import PersistenceView
from ui.log_analyzer_view import LogAnalyzerView
from ui.marketplace_view import PluginMarketplaceView
from PySide6.QtGui import QIcon, QColor
import os

class NavButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setCheckable(True)
        self.setFixedHeight(40)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #e0e0e0;
                text-align: left;
                padding-left: 15px;
                font-size: 11px;
                border-left: 3px solid transparent;
                font-weight: normal;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
            }
            QPushButton:checked {
                color: #00ccff;
                font-weight: bold;
                border-left: 3px solid #00ccff;
                background-color: #1a1a1a;
            }
        """)

class SideBar(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(200)
        self.setObjectName("SideBar")
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Logo/Brand Area
        self.brand_frame = QFrame()
        self.brand_frame.setFixedHeight(60)
        brand_layout = QHBoxLayout(self.brand_frame)
        self.brand_label = QLabel("HACKURA SUITE")
        self.brand_label.setObjectName("LogoHeader")
        self.brand_label.setStyleSheet("font-weight: bold; font-size: 16px; color: #00ccff;")
        brand_layout.addWidget(self.brand_label)
        self.main_layout.addWidget(self.brand_frame)

        # Scrollable Nav Area
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.scroll.setStyleSheet("background-color: transparent;")
        
        self.nav_container = QWidget()
        self.nav_layout = QVBoxLayout(self.nav_container)
        self.nav_layout.setContentsMargins(0, 10, 0, 10)
        self.nav_layout.setSpacing(2)
        
        self.buttons = {}
        
        self.add_category("CORE")
        self.add_nav("DASHBOARD", "dashboard")
        self.add_nav("CLIENTS", "clients")
        self.add_nav("PROJECTS", "projects")

        self.nav_layout.addSpacing(15)
        self.add_category("MANAGEMENT")
        self.add_nav("ENGAGEMENTS", "engagements")
        self.add_nav("ASSET TRACKER", "assets")
        self.add_nav("REPORT GEN", "report_customizer")

        self.nav_layout.addSpacing(15)
        self.add_category("AUTOMATION")
        self.add_nav("ORCHESTRATOR", "orchestrator")
        self.add_nav("VULN REPLAY", "vuln_replay")
        
        self.nav_layout.addSpacing(15)
        self.add_category("EVASION & PERSISTENCE")
        self.add_nav("OBFUSCATOR", "obfuscation")
        self.add_nav("C2 PERSISTENCE", "persistence")

        self.nav_layout.addSpacing(15)
        self.add_category("SYSTEM LABS")
        self.add_nav("SANDBOX TESTER", "sandbox")
        self.add_nav("LOG ANALYZER", "log_analyzer")
        self.add_nav("MARKETPLACE", "marketplace")
        
        self.nav_layout.addSpacing(15)
        self.add_category("OFFENSIVE")
        self.add_nav("NETWORK", "network")
        self.add_nav("WEB SCANS", "web")
        self.add_nav("CLOUD SCAN", "cloud")
        self.add_nav("RED TEAM", "red_team")
        self.add_nav("API FUZZER", "api_fuzzer")
        self.add_nav("CREDENTIALS", "credentials")
        self.add_nav("WIRELESS/BT", "wireless")
        self.add_nav("AI EXPLOIT", "ai_exploit")
        
        self.nav_layout.addSpacing(15)
        self.add_category("RED - ADVANCED")
        self.add_nav("EDR EVASION", "evasion")
        self.add_nav("MALWARE GEN", "malware")
        self.add_nav("CONTAINER/K8S", "k8s")
        self.add_nav("SECRETS SCAN", "secrets")

        self.nav_layout.addSpacing(15)
        self.add_category("DEFENSIVE")
        self.add_nav("MONITORING", "monitoring")
        self.add_nav("BLUE DASH", "blue_dashboard")
        self.add_nav("BLUE TOOLS", "blue_team")
        self.add_nav("AUDIT LOGS", "audit")
        self.add_nav("COMPLIANCE", "compliance")
        
        self.nav_layout.addSpacing(15)
        self.add_category("SYSTEM")
        self.add_nav("CONSOLE", "console")
        self.add_nav("REPORTING", "reporting")
        self.add_nav("SETTINGS", "settings")

        self.nav_layout.addStretch()
        
        self.scroll.setWidget(self.nav_container)
        self.main_layout.addWidget(self.scroll)

    def add_category(self, title):
        lbl = QLabel(title)
        lbl.setStyleSheet("color: #555; font-size: 10px; font-weight: bold; padding: 5px 15px; letter-spacing: 1px;")
        self.nav_layout.addWidget(lbl)

    def add_nav(self, label, view_name):
        btn = NavButton(label)
        self.nav_layout.addWidget(btn)
        self.buttons[view_name] = btn

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hackura Pentest Suite - Pro-Grade Security Assessments")
        self.resize(1280, 850)
        self.setMinimumSize(1000, 700)
        
        self.setWindowFlags(Qt.Window | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)
        
        logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "logo.png")
        if os.path.exists(logo_path):
            self.setWindowIcon(QIcon(logo_path))

        from core.db import db_manager
        current_theme = db_manager.get_setting("theme", "Dark (Kali)")

        # Main UI structure: SideBar + VerticalLayout(Content + StatusBar)
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Sidebar
        self.sidebar = SideBar()
        self.main_layout.addWidget(self.sidebar)

        # Right side content
        self.content_container = QWidget()
        self.content_layout = QVBoxLayout(self.content_container)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)
        self.main_layout.addWidget(self.content_container)

        # Content Area (Stacked Widget)
        self.content_stack = QStackedWidget()
        self.content_layout.addWidget(self.content_stack)

        # Status Bar (moved inside content container at the bottom)
        self.status_bar_frame = QFrame()
        self.status_bar_frame.setFixedHeight(30)
        self.status_bar_frame.setStyleSheet("background-color: #1a1a1a; border-top: 1px solid #333;")
        status_layout = QHBoxLayout(self.status_bar_frame)
        status_layout.setContentsMargins(15, 0, 15, 0)
        
        self.status_msg = QLabel("READY")
        self.status_msg.setStyleSheet("color: #888; font-size: 10px;")
        status_layout.addWidget(self.status_msg)
        
        status_layout.addStretch()
        
        self.cloud_indicator = QLabel("☁ OFFLINE")
        self.cloud_indicator.setStyleSheet("color: #ff3333; font-weight: bold; font-size: 10px;")
        status_layout.addWidget(self.cloud_indicator)
        
        self.content_layout.addWidget(self.status_bar_frame)
        
        self.update_cloud_indicator()
        self.setup_views()
        self.connect_signals()
        self.apply_styles(current_theme)

    def setup_views(self):
        self.views = {
            "dashboard": DashboardView(),
            "clients": ClientView(),
            "projects": ProjectView(),
            "network": NetworkView(),
            "web": WebView(),
            "cloud": CloudView(),
            "monitoring": MonitoringView(),
            "red_team": RedTeamView(),
            "api_fuzzer": APIFuzzerView(),
            "compliance": ComplianceView(),
            "console": ConsoleView(),
            "reporting": ReportingView(),
            "blue_dashboard": BlueDashboardView(),
            "blue_team": BlueTeamView(),
            "audit": SecurityAuditView(),
            "settings": SettingsView(),
            "credentials": CredentialView(),
            "wireless": WirelessView(),
            "evasion": EvasionView(),
            "malware": MalwareView(),
            "k8s": K8sView(),
            "secrets": SecretsView(),
            "ai_exploit": AIExploitView(),
            "report_customizer": ReportCustomizerView(),
            "engagements": EngagementTrackerView(),
            "assets": AssetTrackerView(),
            "orchestrator": OrchestratorView(),
            "vuln_replay": VulnReplayView(),
            "sandbox": SandboxView(),
            "obfuscation": ObfuscationView(),
            "persistence": PersistenceView(),
            "log_analyzer": LogAnalyzerView(),
            "marketplace": PluginMarketplaceView()
        }
        self.stack_widgets = {}
        for name, view in self.views.items():
            if name in ["dashboard", "monitoring", "settings", "reporting", "audit", "blue_team", "blue_dashboard", "credentials", "wireless", "evasion", "malware", "k8s", "secrets", "ai_exploit", "report_customizer", "engagements", "assets", "orchestrator", "vuln_replay", "sandbox", "obfuscation", "persistence", "log_analyzer", "marketplace"]:
                scroll = QScrollArea()
                scroll.setWidgetResizable(True)
                scroll.setFrameShape(QFrame.NoFrame)
                scroll.setWidget(view)
                scroll.setStyleSheet("background-color: transparent;")
                self.content_stack.addWidget(scroll)
                self.stack_widgets[name] = scroll
            else:
                self.content_stack.addWidget(view)
                self.stack_widgets[name] = view
        
        self.switch_view("dashboard")

    def connect_signals(self):
        for name, btn in self.sidebar.buttons.items():
            btn.clicked.connect(lambda checked, n=name: self.switch_view(n))

    def switch_view(self, name):
        for n, btn in self.sidebar.buttons.items():
            btn.setChecked(n == name)
        
        self.content_stack.setCurrentWidget(self.stack_widgets[name])
        
        if name == "dashboard":
            self.views["dashboard"].refresh_stats()
        elif name == "projects":
            self.views["projects"].refresh_table()
        elif name == "clients":
            self.views["clients"].refresh_table()
        elif name == "audit":
            self.views["audit"].refresh_logs()
        elif name in ["network", "web", "cloud", "reporting", "blue_team", "red_team", "api_fuzzer", "compliance", "credentials", "wireless", "evasion", "malware", "k8s", "secrets", "ai_exploit", "report_customizer", "engagements", "assets", "orchestrator", "vuln_replay", "sandbox", "obfuscation", "persistence", "log_analyzer", "marketplace"]:
            self.views[name].refresh_projects()

    def update_cloud_indicator(self):
        from core.db import db_manager
        if db_manager.use_cloud:
            self.cloud_indicator.setText("☁ CLOUD SYNC ACTIVE")
            self.cloud_indicator.setStyleSheet("color: #00ff00; font-weight: bold; font-size: 10px;")
        else:
            self.cloud_indicator.setText("☁ LOCAL MODE")
            self.cloud_indicator.setStyleSheet("color: #ffaa00; font-weight: bold; font-size: 10px;")

    def apply_styles(self, theme_name="Dark (Kali)"):
        is_light = theme_name == "Light (Professional)"
        bg = "#f4f4f4" if is_light else "#121212"
        fg = "#333333" if is_light else "#f0f0f0"
        sidebar_bg = "#e0e0e0" if is_light else "#1e1e1e"
        border = "#cccccc" if is_light else "#333333"
        accent = "#0078d4" if is_light else "#00ccff"
        input_bg = "#ffffff" if is_light else "#2b2b2b"

        self.setStyleSheet(f"""
            QMainWindow, QWidget {{
                background-color: {bg};
                color: {fg};
                font-family: 'Inter', 'Segoe UI', Arial;
            }}
            QFrame#SideBar {{
                background-color: {sidebar_bg};
                border-right: 1px solid {border};
            }}
            QLineEdit, QComboBox, QPlainTextEdit, QTableWidget {{
                background-color: {input_bg};
                border: 1px solid {border};
                border-radius: 4px;
                padding: 6px;
                color: {fg};
            }}
            QPushButton {{
                border-radius: 4px;
                padding: 8px;
                background-color: {sidebar_bg};
                color: {fg};
            }}
            QProgressBar {{
                border: 1px solid {border};
                border-radius: 4px;
                text-align: center;
                background-color: {input_bg};
            }}
            QProgressBar::chunk {{
                background-color: {accent};
            }}
        """)
        
        # Specific button styles for sidebar
        for btn in self.sidebar.buttons.values():
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    border: none;
                    color: {"#555" if is_light else "#aaa"};
                    text-align: left;
                    padding-left: 20px;
                    font-size: 12px;
                    border-left: 3px solid transparent;
                    height: 35px;
                }}
                QPushButton:hover {{
                    background-color: {"#d0d0d0" if is_light else "#2a2a2a"};
                    color: {fg};
                }}
                QPushButton:checked {{
                    color: {accent};
                    font-weight: bold;
                    border-left: 3px solid {accent};
                    background-color: {"#d8d8d8" if is_light else "#151515"};
                }}
            """)

