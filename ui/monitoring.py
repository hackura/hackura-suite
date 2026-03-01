from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar, QPlainTextEdit, QFrame, QScrollArea
)
from PySide6.QtCore import Qt, QTimer
from core.monitor import MonitoringWorker
from core.db import db_manager
from ui.components.threat_map import ThreatMapWidget
from datetime import datetime

class MonitoringView(QWidget):
    def __init__(self):
        super().__init__()
        self.metric_containers = []
        
        # Main Layout (Contains Scroll Area)
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Scroll Area Setup
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.main_layout.addWidget(self.scroll_area)
        
        # Container for Scrollable Content
        self.container = QWidget()
        self.scroll_area.setWidget(self.container)
        self.layout = QVBoxLayout(self.container)
        self.layout.setContentsMargins(40, 40, 40, 40)
        self.layout.setSpacing(30)

        self.header_lbl = QLabel("Live Security Monitoring")
        self.header_lbl.setStyleSheet("font-size: 24px; font-weight: bold; color: #00ff00;")
        self.layout.addWidget(self.header_lbl)

        # 1. Full-Page Threat Map Visualization
        self.threat_map = ThreatMapWidget()
        self.threat_map.setMinimumHeight(800) # Immersion mode
        self.layout.addWidget(self.threat_map)

        # 2. Metrics Row (Below Map)
        metrics_layout = QHBoxLayout()
        self.cpu_bar = self.create_metric_widget("CPU Usage", metrics_layout)
        self.ram_bar = self.create_metric_widget("RAM Usage", metrics_layout)
        self.layout.addLayout(metrics_layout)

        # 3. Recent Activity (Below Metrics)
        self.stream_label = QLabel("Real-time Event Stream:")
        self.layout.addWidget(self.stream_label)
        self.event_log = QPlainTextEdit()
        self.event_log.setReadOnly(True)
        self.event_log.setMinimumHeight(300)
        self.layout.addWidget(self.event_log)
        # Initialize Theme
        theme = db_manager.get_setting("theme", "Dark (Kali)")
        self.apply_styles(theme)

        # Start Worker
        self.worker = MonitoringWorker()
        self.worker.metrics_updated.connect(self.update_metrics)
        self.worker.event_detected.connect(self.add_event)
        self.worker.global_threat.connect(lambda data: self.threat_map.add_threat(
            data["src_lat"], data["src_lon"], data["dst_lat"], data["dst_lon"], data["severity"]
        ))
        self.worker.start()

    def create_metric_widget(self, label, parent_layout):
        container = QFrame()
        self.metric_containers.append(container)
        lay = QVBoxLayout(container)
        lbl = QLabel(label)
        lbl.setWordWrap(True)
        lay.addWidget(lbl)
        bar = QProgressBar()
        lay.addWidget(bar)
        parent_layout.addWidget(container)
        return bar

    def apply_styles(self, theme_name):
        is_light = theme_name == "Light (Professional)"
        accent = "#0078d4" if is_light else "#00ff00"
        bg = "#ffffff" if is_light else "#000000"
        card_bg = "#f0f0f0" if is_light else "#1e1e1e"
        border = "#cccccc" if is_light else "#3d3d3d"
        text = "#333333" if is_light else "#00ff00"
        label_color = "#555555" if is_light else "#f0f0f0"

        self.header_lbl.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {accent};")
        self.stream_label.setStyleSheet(f"color: {label_color}; font-weight: bold;")
        
        self.event_log.setStyleSheet(f"""
            background-color: {bg};
            color: {text};
            font-family: 'Consolas', monospace;
            border: 1px solid {border};
        """)

        # Custom Scrollbar Styling
        self.scroll_area.setStyleSheet(f"""
            QScrollArea {{
                background-color: transparent;
                border: none;
            }}
            QScrollBar:vertical {{
                background: {bg};
                width: 12px;
                margin: 0px 0px 0px 0px;
            }}
            QScrollBar::handle:vertical {{
                background: {accent};
                min-height: 20px;
                border-radius: 6px;
                margin: 2px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
        """)
        self.container.setStyleSheet(f"background-color: {bg};")

        for container in self.metric_containers:
            container.setStyleSheet(f"background-color: {card_bg}; border-radius: 8px; padding: 15px; border: 1px solid {border};")
            # The progress bars inside can't be easily reached here without storing them, but we can use global stylesheet in MainWindow
            # or just style them here too.
        
        self.cpu_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: {bg};
                border: 1px solid {border};
                border-radius: 5px;
                height: 12px;
                text-align: center;
            }}
            QProgressBar::chunk {{
                background-color: {accent};
                border-radius: 4px;
            }}
        """)
        self.ram_bar.setStyleSheet(self.cpu_bar.styleSheet())
        
        # Propagate to Threat Map
        self.threat_map.apply_styles(theme_name)

    def update_metrics(self, data):
        self.cpu_bar.setValue(int(data["cpu"]))
        self.ram_bar.setValue(int(data["ram"]))

    def add_event(self, event):
        ts = datetime.now().strftime("%H:%M:%S")
        self.event_log.appendPlainText(f"[{ts}] {event['type']}: {event['details']}")

    def closeEvent(self, event):
        self.worker.stop()
        self.worker.wait()
        super().closeEvent(event)
