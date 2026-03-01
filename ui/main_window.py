from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, 
    QStackedWidget, QLabel, QFrame, QScrollArea
)
from PySide6.QtCore import Qt
from ui.network import NetworkView
from ui.web import WebView
from ui.cloud import CloudView
from ui.exfiltrate import RedTeamView
from ui.reporting import ReportingView
from ui.settings import SettingsView
from ui.dashboard import DashboardView
from ui.console import ConsoleView
from ui.projects import ProjectView
from ui.clients import ClientView
from ui.audit import SecurityAuditView
from ui.monitoring import MonitoringView
from ui.blue_team import BlueTeamView
from PySide6.QtGui import QIcon, QColor
import os

class NavButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setCheckable(True)
        self.setFixedHeight(45)
        self.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #e0e0e0;
                text-align: center;
                padding: 0 8px;
                font-size: 12px;
                border-bottom: 3px solid transparent;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
            }
            QPushButton:checked {
                color: #00ccff;
                font-weight: bold;
                border-bottom: 3px solid #00ccff;
            }
        """)

class TopBar(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(60)
        self.setObjectName("TopBar")
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(10, 0, 10, 0)
        self.layout.setSpacing(5)
        
        # Logo/Brand
        self.brand_label = QLabel("HACKURA")
        self.brand_label.setObjectName("LogoHeader")
        self.brand_label.setStyleSheet("font-weight: bold; font-size: 18px; margin-right: 20px; padding-left: 10px;")
        self.layout.addWidget(self.brand_label)

        self.buttons = {}
        self.add_nav("DASHBOARD", "dashboard")
        self.add_nav("CLIENTS", "clients")
        self.add_nav("PROJECTS", "projects")
        self.add_nav("NETWORK", "network")
        self.add_nav("WEB", "web")
        self.add_nav("CLOUD", "cloud")
        self.add_nav("MONITOR", "monitoring")
        self.add_nav("RED TEAM", "red_team")
        self.add_nav("CONSOLE", "console")
        self.add_nav("REPORTING", "reporting")
        self.add_nav("BLUE TEAM", "blue_team")
        self.add_nav("AUDIT", "audit")
        
        self.layout.addStretch()
        self.add_nav("SETTINGS", "settings")

    def add_nav(self, label, view_name):
        btn = NavButton(label)
        self.layout.addWidget(btn)
        self.buttons[view_name] = btn

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hackura Pentest Suite - Pro-Grade Security Assessments")
        self.resize(1200, 800)
        self.setMinimumSize(1000, 700)
        
        # Ensure window is resizable and has maximize button
        self.setWindowFlags(Qt.Window | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)
        
        # Set Window Icon
        logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "logo.png")
        if os.path.exists(logo_path):
            self.setWindowIcon(QIcon(logo_path))

        from core.db import db_manager
        current_theme = db_manager.get_setting("theme", "Dark (Kali)")
        self.apply_styles(current_theme)

        # Set central widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # Top Navigation Bar
        self.navbar = TopBar()
        self.layout.addWidget(self.navbar)

        # Content Area (Stacked Widget)
        self.content_stack = QStackedWidget()
        self.layout.addWidget(self.content_stack)

        # Status Bar
        self.status_bar = self.statusBar()
        self.status_bar.setStyleSheet("background-color: #2b2b2b; color: #888; border-top: 1px solid #3d3d3d;")
        self.cloud_indicator = QLabel("☁ OFFLINE")
        self.cloud_indicator.setStyleSheet("padding: 0 20px; color: #ff3333; font-weight: bold;")
        self.status_bar.addPermanentWidget(self.cloud_indicator)
        self.update_cloud_indicator()

        self.setup_views()
        self.connect_signals()

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
            "console": ConsoleView(),
            "reporting": ReportingView(),
            "blue_team": BlueTeamView(),
            "audit": SecurityAuditView(),
            "settings": SettingsView()
        }
        self.stack_widgets = {}
        for name, view in self.views.items():
            if name in ["dashboard", "monitoring", "settings", "reporting", "audit", "blue_team"]:
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
        
        # Default view
        self.switch_view("dashboard")

    def create_placeholder(self, title):
        view = QWidget()
        layout = QVBoxLayout(view)
        layout.setContentsMargins(40, 40, 40, 40)
        
        lbl = QLabel(title)
        lbl.setStyleSheet("font-size: 24px; font-weight: bold; color: #f0f0f0;")
        layout.addWidget(lbl)
        layout.addStretch()
        return view

    def connect_signals(self):
        for name, btn in self.navbar.buttons.items():
            btn.clicked.connect(lambda checked, n=name: self.switch_view(n))

    def switch_view(self, name):
        # Update nav buttons
        for n, btn in self.navbar.buttons.items():
            btn.setChecked(n == name)
        
        self.content_stack.setCurrentWidget(self.stack_widgets[name])
        
        # Refresh dashboard or project list if entering them
        if name == "dashboard":
            self.views["dashboard"].refresh_stats()
        elif name == "projects":
            self.views["projects"].refresh_table()
        elif name == "clients":
            self.views["clients"].refresh_table()
        elif name == "audit":
            self.views["audit"].refresh_logs()
        elif name in ["network", "web", "cloud", "reporting", "blue_team", "red_team"]:
            self.views[name].refresh_projects()

    def update_cloud_indicator(self):
        from core.db import db_manager
        if db_manager.use_cloud:
            self.cloud_indicator.setText("☁ CLOUD SYNC ACTIVE")
            self.cloud_indicator.setStyleSheet("padding: 0 20px; color: #00ff00; font-weight: bold;")
        else:
            self.cloud_indicator.setText("☁ LOCAL MODE")
            self.cloud_indicator.setStyleSheet("padding: 0 20px; color: #ffaa00; font-weight: bold;")

    def apply_styles(self, theme_name="Dark (Kali)"):
        if theme_name == "Light (Professional)":
            bg = "#f4f4f4"
            fg = "#333333"
            sidebar_bg = "#e0e0e0"
            sidebar_fg = "#555555"
            card_bg = "#ffffff"
            border = "#cccccc"
            accent = "#0078d4"
            input_bg = "#ffffff"
        else:
            bg = "#1e1e1e"
            fg = "#f0f0f0"
            sidebar_bg = "#2b2b2b"
            sidebar_fg = "#e0e0e0"
            card_bg = "#2b2b2b"
            border = "#3d3d3d"
            accent = "#00ccff"
            input_bg = "#2b2b2b"

        self.setStyleSheet(f"""
            QMainWindow, QWidget {{
                background-color: {bg};
                color: {fg};
                font-family: 'Segoe UI', Arial, sans-serif;
            }}
            QFrame#TopBar {{
                background-color: {sidebar_bg};
                border-bottom: 1px solid {border};
            }}
            QGroupBox {{
                border: 1px solid {border};
                border-radius: 8px;
                margin-top: 20px;
                padding-top: 20px;
                font-weight: bold;
                color: {accent};
            }}
            QLineEdit, QComboBox, QPlainTextEdit, QTableWidget {{
                background-color: {input_bg};
                border: 1px solid {border};
                border-radius: 4px;
                padding: 6px;
                color: {fg};
            }}
            QComboBox QAbstractItemView {{
                background-color: {input_bg};
                color: {fg};
                selection-background-color: {accent};
                selection-color: {"black" if theme_name == "Light (Professional)" else "white"};
                border: 1px solid {border};
            }}
            QFrame#CRMForm, QFrame#ReportingFrame {{
                background-color: {card_bg};
                border: 1px solid {border};
                border-radius: 8px;
            }}
            QLineEdit:focus, QComboBox:focus {{
                border-color: {accent};
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
            QScrollArea {{
                border: none;
                background-color: transparent;
            }}
            QScrollBar:vertical {{
                border: none;
                background: {bg};
                width: 10px;
                margin: 0px 0px 0px 0px;
            }}
            QScrollBar::handle:vertical {{
                background: {border};
                min-height: 20px;
                border-radius: 5px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QHeaderView::section {{
                background-color: {sidebar_bg};
                color: {fg};
                padding: 4px;
                border: none;
            }}
            QLabel#LogoHeader {{
                color: {accent};
            }}
        """)
        
        # Update navbar specifically if it exists
        if hasattr(self, 'navbar'):
            self.navbar.setStyleSheet(f"background-color: {sidebar_bg}; border-bottom: 1px solid {border};")
            for btn in self.navbar.buttons.values():
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: transparent;
                        border: none;
                        color: {sidebar_fg};
                        text-align: center;
                        padding: 0 8px;
                        font-size: 12px;
                        border-bottom: 3px solid transparent;
                    }}
                    QPushButton:hover {{
                        background-color: {border};
                    }}
                    QPushButton:checked {{
                        color: {accent};
                        font-weight: bold;
                        border-bottom: 3px solid {accent};
                    }}
                """)

        # Propagate to current view if reactive
        if hasattr(self, 'stack'):
            current_view = self.stack.currentWidget()
            if hasattr(current_view, 'apply_styles'):
                current_view.apply_styles(theme_name)
