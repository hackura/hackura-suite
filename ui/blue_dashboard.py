from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap, QImage
from core.db import db_manager
import matplotlib.pyplot as plt
from io import BytesIO
import random
import psutil

class MetricCard(QFrame):
    def __init__(self, title, value, color="#00ff00"):
        super().__init__()
        self.title = title
        self.value = value
        self.accent_color = color
        
        layout = QVBoxLayout(self)
        
        self.val_lbl = QLabel(str(value))
        self.val_lbl.setAlignment(Qt.AlignCenter)
        
        self.title_lbl = QLabel(title.upper())
        self.title_lbl.setAlignment(Qt.AlignCenter)
        self.title_lbl.setWordWrap(True)
        
        layout.addWidget(self.val_lbl)
        layout.addWidget(self.title_lbl)
        
        self.apply_styles()

    def apply_styles(self):
        theme = db_manager.get_setting("theme", "Dark (Kali)")
        is_light = theme == "Light (Professional)"
        bg = "#ffffff" if is_light else "#2b2b2b"
        border = "#cccccc" if is_light else "#3d3d3d"
        subtext = "#777777" if is_light else "#a0a0a0"
        
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {bg};
                border: 1px solid {border};
                border-radius: 10px;
                padding: 15px;
            }}
        """)
        self.val_lbl.setStyleSheet(f"font-size: 28px; font-weight: bold; color: {self.accent_color};")
        self.title_lbl.setStyleSheet(f"font-size: 10px; color: {subtext}; font-weight: bold;")

class BlueDashboardView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(40, 40, 40, 40)
        self.layout.setSpacing(25)

        self.header_lbl = QLabel("Blue Team Defensive Dashboard")
        self.header_lbl.setStyleSheet("font-size: 26px; font-weight: bold; color: #00ff00;")
        self.layout.addWidget(self.header_lbl)

        # Metrics Row
        metrics_layout = QHBoxLayout()
        self.traffic_card = MetricCard("Active Connections", "0")
        self.alerts_card = MetricCard("Alert Volume (1h)", "0", "#ffaa00")
        self.cpu_card = MetricCard("System Load", "0%", "#00ccff")
        self.hardening_card = MetricCard("Hardening Score", "88/100", "#00ff00")
        
        metrics_layout.addWidget(self.traffic_card)
        metrics_layout.addWidget(self.alerts_card)
        metrics_layout.addWidget(self.cpu_card)
        metrics_layout.addWidget(self.hardening_card)
        self.layout.addLayout(metrics_layout)

        # Main Visualization Area
        viz_layout = QGridLayout()
        
        # Network Traffic Chart
        self.net_viz_box = QFrame()
        self.net_viz_box.setFrameShape(QFrame.StyledPanel)
        net_layout = QVBoxLayout(self.net_viz_box)
        net_layout.addWidget(QLabel("LIVE NETWORK TRAFFIC (PPS)"))
        self.net_chart_lbl = QLabel()
        self.net_chart_lbl.setAlignment(Qt.AlignCenter)
        net_layout.addWidget(self.net_chart_lbl)
        viz_layout.addWidget(self.net_viz_box, 0, 0)

        # Alert Distribution
        self.alert_viz_box = QFrame()
        self.alert_viz_box.setFrameShape(QFrame.StyledPanel)
        alert_layout = QVBoxLayout(self.alert_viz_box)
        alert_layout.addWidget(QLabel("THREAT CATEGORY DISTRIBUTION"))
        self.alert_chart_lbl = QLabel()
        self.alert_chart_lbl.setAlignment(Qt.AlignCenter)
        alert_layout.addWidget(self.alert_chart_lbl)
        viz_layout.addWidget(self.alert_viz_box, 0, 1)

        self.layout.addLayout(viz_layout)

        # Live Feed
        self.feed_title = QLabel("REAL-TIME DEFENSIVE TELEMETRY")
        self.feed_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #555;")
        self.layout.addWidget(self.feed_title)
        
        self.feed_box = QFrame()
        self.feed_box.setMinimumHeight(200)
        self.feed_layout = QVBoxLayout(self.feed_box)
        self.feed_layout.setContentsMargins(10, 10, 10, 10)
        self.layout.addWidget(self.feed_box)

        # Update Timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_metrics)
        self.timer.start(3000)

        self.history = [random.randint(10, 50) for _ in range(20)]
        
        self.apply_styles()
        self.update_metrics()

    def apply_styles(self):
        theme = db_manager.get_setting("theme", "Dark (Kali)")
        is_light = theme == "Light (Professional)"
        text = "#333333" if is_light else "#f0f0f0"
        bg = "#ffffff" if is_light else "#0d0d0d"
        border = "#cccccc" if is_light else "#333"
        box_bg = "#f9f9f9" if is_light else "#1a1a1a"

        self.header_lbl.setStyleSheet(f"font-size: 26px; font-weight: bold; color: #00ff00;")
        self.feed_box.setStyleSheet(f"background-color: {bg}; border: 1px solid {border}; border-radius: 4px;")
        
        style = f"background-color: {box_bg}; border: 1px solid {border}; border-radius: 8px; padding: 10px;"
        self.net_viz_box.setStyleSheet(style)
        self.alert_viz_box.setStyleSheet(style)

    def update_metrics(self):
        # Update cards
        conns = len(psutil.net_connections())
        cpu = psutil.cpu_percent()
        alerts = random.randint(0, 15)
        
        self.traffic_card.val_lbl.setText(str(conns))
        self.cpu_card.val_lbl.setText(f"{cpu}%")
        self.alerts_card.val_lbl.setText(str(alerts))
        
        if alerts > 10:
            self.alerts_card.val_lbl.setStyleSheet("font-size: 28px; font-weight: bold; color: #ff3333;")
        else:
            self.alerts_card.val_lbl.setStyleSheet("font-size: 28px; font-weight: bold; color: #ffaa00;")

        # Update log feed
        if alerts > 0:
            events = ["Blocked suspicious IP", "Deep packet inspection triggered", "SSH brute-force attempt mitigated", "WAF rule matched: SQLi"]
            evt = random.choice(events)
            log = QLabel(f"<span style='color: #00ff00;'>[OK]</span> {evt} - {random.randint(1,255)}.{random.randint(1,255)}.x.x")
            log.setStyleSheet("font-family: monospace; font-size: 11px;")
            self.feed_layout.insertWidget(0, log)
            if self.feed_layout.count() > 8:
                self.feed_layout.itemAt(self.feed_layout.count()-1).widget().setParent(None)

        self.generate_charts()

    def generate_charts(self):
        try:
            theme = db_manager.get_setting("theme", "Dark (Kali)")
            text_color = "white" if "Dark" in theme else "black"
            bg_color = "#1e1e1e" if "Dark" in theme else "#f4f4f4"
            
            # Network Chart
            self.history.append(random.randint(10, 100))
            self.history = self.history[-20:]
            
            plt.figure(figsize=(5, 3), facecolor=bg_color)
            plt.plot(self.history, color='#00ff00', linewidth=2)
            plt.fill_between(range(len(self.history)), self.history, color='#00ff00', alpha=0.2)
            plt.axis('off')
            plt.tight_layout()
            
            buf = BytesIO()
            plt.savefig(buf, format='png', transparent=True, dpi=80)
            plt.close()
            self.net_chart_lbl.setPixmap(QPixmap.fromImage(QImage.fromData(buf.getvalue())))

            # Alert Distribution
            plt.figure(figsize=(5, 3), facecolor=bg_color)
            cats = ['DDoS', 'Phishing', 'Malware', 'Injection', 'Auth']
            vals = [random.randint(1, 10) for _ in cats]
            plt.barh(cats, vals, color='#ffaa00')
            plt.xticks(color=text_color)
            plt.yticks(color=text_color)
            plt.tight_layout()
            
            buf2 = BytesIO()
            plt.savefig(buf2, format='png', transparent=True, dpi=80)
            plt.close()
            self.alert_chart_lbl.setPixmap(QPixmap.fromImage(QImage.fromData(buf2.getvalue())))

        except Exception as e:
            print(f"Chart Error: {e}")
