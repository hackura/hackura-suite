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
from ui.graph_explorer import GraphExplorerView
from ui.osint_view import OSINTView
from ui.license_view import LicenseView
from core.security import license_manager
from PySide6.QtGui import QIcon, QColor
import os

class NavButton(QPushButton):
    def __init__(self, text, is_category=False, parent=None):
        super().__init__(text, parent)
        self.setCheckable(True)
        self.setFixedHeight(35 if is_category else 30)
        self.setCursor(Qt.PointingHandCursor)
        self.is_category = is_category
        
        if is_category:
            self.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                    color: #aaa;
                    padding: 0 15px;
                    font-size: 11px;
                    font-weight: bold;
                    letter-spacing: 1px;
                }
                QPushButton:hover {
                    color: #fff;
                }
                QPushButton:checked {
                    color: #00ccff;
                    border-bottom: 2px solid #00ccff;
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #252525;
                    border: 1px solid #333;
                    border-radius: 4px;
                    color: #e0e0e0;
                    padding: 0 10px;
                    font-size: 10px;
                }
                QPushButton:hover {
                    background-color: #3d3d3d;
                }
                QPushButton:checked {
                    background-color: #1a1a1a;
                    color: #00ccff;
                    border: 1px solid #00ccff;
                }
            """)

class TopBar(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(100) # Total height for both tiers
        self.setObjectName("TopBar")
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # Tier 1: Main Categories
        self.tier1_frame = QFrame()
        self.tier1_frame.setFixedHeight(50)
        self.tier1_frame.setStyleSheet("background-color: #1a1a1a; border-bottom: 1px solid #333;")
        tier1_layout = QHBoxLayout(self.tier1_frame)
        tier1_layout.setContentsMargins(15, 0, 15, 0)
        tier1_layout.setSpacing(10)

        self.brand_label = QLabel("HACKURA")
        self.brand_label.setStyleSheet("font-weight: bold; font-size: 18px; color: #00ccff; margin-right: 20px;")
        tier1_layout.addWidget(self.brand_label)
        
        self.license_lbl = QLabel("TRIAL")
        self.license_lbl.setStyleSheet("font-size: 9px; background-color: #ffaa00; color: black; padding: 2px 6px; border-radius: 3px; font-weight: bold; margin-right: 15px;")
        tier1_layout.addWidget(self.license_lbl)

        self.cat_buttons = {}
        self.categories = [
            "CORE", "INTELLIGENCE", "OFFENSIVE", "RED ADVANCED", "DEFENSIVE", "SYSTEM"
        ]
        
        for cat in self.categories:
            btn = NavButton(cat, is_category=True)
            tier1_layout.addWidget(btn)
            self.cat_buttons[cat] = btn
        
        tier1_layout.addStretch()
        self.layout.addWidget(self.tier1_frame)

        # Tier 2: Specific Tools (Sub-bar)
        self.tier2_frame = QFrame()
        self.tier2_frame.setFixedHeight(50)
        self.tier2_frame.setStyleSheet("background-color: #121212; border-bottom: 1px solid #333;")
        self.tier2_layout = QHBoxLayout(self.tier2_frame)
        self.tier2_layout.setContentsMargins(15, 0, 15, 0)
        self.tier2_layout.setSpacing(8)
        self.layout.addWidget(self.tier2_frame)

        self.tool_buttons = {}

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hackura Pentest Suite - Pro-Grade Security Assessments")
        self.resize(1280, 850)
        self.setMinimumSize(1000, 700)
        
        self.category_map = {
            "CORE": [("DASHBOARD", "dashboard"), ("CLIENTS", "clients"), ("PROJECTS", "projects")],
            "INTELLIGENCE": [("GRAPH EXPLORER", "graph_explorer"), ("OSINT HUB", "osint")],
            "OFFENSIVE": [("NETWORK", "network"), ("WEB SCANS", "web"), ("CLOUD SCAN", "cloud"), ("RED TEAM", "red_team"), ("API FUZZER", "api_fuzzer"), ("CREDENTIALS", "credentials"), ("WIRELESS/BT", "wireless"), ("AI EXPLOIT", "ai_exploit")],
            "RED ADVANCED": [("EDR EVASION", "evasion"), ("MALWARE GEN", "malware"), ("CONTAINER/K8S", "k8s"), ("SECRETS SCAN", "secrets"), ("OBFUSCATOR", "obfuscation"), ("C2 PERSISTENCE", "persistence")],
            "DEFENSIVE": [("MONITORING", "monitoring"), ("BLUE DASH", "blue_dashboard"), ("BLUE TOOLS", "blue_team"), ("AUDIT LOGS", "audit"), ("COMPLIANCE", "compliance"), ("LOG ANALYZER", "log_analyzer")],
            "SYSTEM": [("CONSOLE", "console"), ("REPORTING", "reporting"), ("SETTINGS", "settings"), ("MARKETPLACE", "marketplace"), ("LICENSING", "license"), ("ENGAGEMENTS", "engagements"), ("ASSET TRACKER", "assets"), ("REPORT GEN", "report_customizer"), ("ORCHESTRATOR", "orchestrator"), ("VULN REPLAY", "vuln_replay"), ("SANDBOX TESTER", "sandbox")]
        }

        self.setWindowFlags(Qt.Window | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)
        
        logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "logo.png")
        if os.path.exists(logo_path):
            self.setWindowIcon(QIcon(logo_path))

        from core.db import db_manager
        current_theme = db_manager.get_setting("theme", "Dark (Kali)")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Top Navigation
        self.top_bar = TopBar()
        self.main_layout.addWidget(self.top_bar)

        # Content Area
        self.content_stack = QStackedWidget()
        self.main_layout.addWidget(self.content_stack)

        # Status Bar
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
        self.main_layout.addWidget(self.status_bar_frame)
        
        self.update_cloud_indicator()
        self.setup_views()
        self.connect_signals()
        self.apply_styles(current_theme)
        
        # Initial Category
        self.switch_category("CORE")

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
            "marketplace": PluginMarketplaceView(),
            "graph_explorer": GraphExplorerView(),
            "osint": OSINTView(),
            "license": LicenseView()
        }
        self.stack_widgets = {}
        for name, view in self.views.items():
            if name in ["dashboard", "monitoring", "settings", "reporting", "audit", "blue_team", "blue_dashboard", "credentials", "wireless", "evasion", "malware", "k8s", "secrets", "ai_exploit", "report_customizer", "engagements", "assets", "orchestrator", "vuln_replay", "sandbox", "obfuscation", "persistence", "log_analyzer", "marketplace", "osint", "graph_explorer", "license"]:
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
        for name, btn in self.top_bar.cat_buttons.items():
            btn.clicked.connect(lambda checked, n=name: self.switch_category(n))

    def switch_category(self, cat_name):
        # Update category buttons
        for name, btn in self.top_bar.cat_buttons.items():
            btn.setChecked(name == cat_name)
        
        # Clear tier 2
        while self.top_bar.tier2_layout.count():
            child = self.top_bar.tier2_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        self.top_bar.tool_buttons = {}
        
        # Add new tools for category
        tools = self.category_map.get(cat_name, [])
        pro_tools = ["ai_exploit", "malware", "k8s", "persistence", "orchestrator"]
        
        for label, view_name in tools:
            is_locked = view_name in pro_tools and not license_manager.is_pro()
            btn_label = f"{label} 🔒" if is_locked else label
            
            btn = NavButton(btn_label)
            if is_locked:
                btn.clicked.connect(lambda chk: self.switch_view("license"))
                btn.setStyleSheet(btn.styleSheet() + " color: #555;")
            else:
                btn.clicked.connect(lambda checked, v=view_name: self.switch_view(v))
                
            self.top_bar.tier2_layout.addWidget(btn)
            self.top_bar.tool_buttons[view_name] = btn
            
        self.top_bar.tier2_layout.addStretch()
        
        # Switch to first tool in category if not already in a tool of this category
        if tools:
            current_view_name = None
            for name, widget in self.stack_widgets.items():
                if self.content_stack.currentWidget() == widget:
                    current_view_name = name
                    break
            
            is_current_in_cat = any(t[1] == current_view_name for t in tools)
            if not is_current_in_cat:
                self.switch_view(tools[0][1])
            else:
                if current_view_name in self.top_bar.tool_buttons:
                    self.top_bar.tool_buttons[current_view_name].setChecked(True)

    def switch_view(self, name):
        # Update License Indicator in Header
        if license_manager.is_pro():
            self.top_bar.license_lbl.setText("PRO")
            self.top_bar.license_lbl.setStyleSheet("font-size: 9px; background-color: #00ff00; color: black; padding: 2px 6px; border-radius: 3px; font-weight: bold; margin-right: 15px;")
        else:
            self.top_bar.license_lbl.setText("TRIAL")
            self.top_bar.license_lbl.setStyleSheet("font-size: 9px; background-color: #ffaa00; color: black; padding: 2px 6px; border-radius: 3px; font-weight: bold; margin-right: 15px;")

        for n, btn in self.top_bar.tool_buttons.items():
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
        elif name in self.views:
            if hasattr(self.views[name], "refresh_projects"):
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
        border = "#cccccc" if is_light else "#333333"
        accent = "#0078d4" if is_light else "#00ccff"
        input_bg = "#ffffff" if is_light else "#2b2b2b"
        header_bg = "#e0e0e0" if is_light else "#1a1a1a"

        self.setStyleSheet(f"""
            QMainWindow, QWidget {{
                background-color: {bg};
                color: {fg};
                font-family: 'Inter', 'Segoe UI', Arial;
            }}
            QFrame#TopBar {{
                background-color: {header_bg};
                border-bottom: 1px solid {border};
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
                background-color: {header_bg};
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

