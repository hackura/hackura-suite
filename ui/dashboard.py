from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout,
    QStackedWidget, QPushButton
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QImage
from core.db import db_manager
import matplotlib.pyplot as plt
from io import BytesIO
import random

class StatCard(QFrame):
    def __init__(self, title, value, color="#00ccff"):
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
        
        theme = db_manager.get_setting("theme", "Dark")
        self.apply_styles(theme)

    def apply_styles(self, theme_name):
        is_light = theme_name == "Light (Professional)"
        bg = "#ffffff" if is_light else "#2b2b2b"
        border = "#cccccc" if is_light else "#3d3d3d"
        text = "#333333" if is_light else "#f0f0f0"
        subtext = "#777777" if is_light else "#a0a0a0"
        
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {bg};
                border: 1px solid {border};
                border-radius: 10px;
                padding: 15px;
            }}
        """)
        self.val_lbl.setStyleSheet(f"font-size: 32px; font-weight: bold; color: {self.accent_color};")
        self.title_lbl.setStyleSheet(f"font-size: 12px; color: {subtext}; font-weight: bold;")

class DashboardView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(40, 40, 40, 40)
        self.layout.setSpacing(30) # Better spacing for scrolling

        self.header_lbl = QLabel("Executive Dashboard")
        self.header_lbl.setStyleSheet("font-size: 28px; font-weight: bold; color: #f0f0f0;")
        self.layout.addWidget(self.header_lbl)

        # Stats Row
        stats_layout = QHBoxLayout()
        self.project_stat = StatCard("Active Projects", "0")
        self.scan_stat = StatCard("Total Scans", "0")
        self.finding_stat = StatCard("Critical Findings", "0", "#ff3333")
        self.health_stat = StatCard("Security Health", "Calculating...", "#00ff00")
        
        stats_layout.addWidget(self.project_stat)
        stats_layout.addWidget(self.scan_stat)
        stats_layout.addWidget(self.finding_stat)
        stats_layout.addWidget(self.health_stat)
        self.layout.addLayout(stats_layout)

        # Analytics Divider
        self.divider = QFrame()
        self.divider.setFrameShape(QFrame.HLine)
        self.divider.setFrameShadow(QFrame.Sunken)
        self.divider.setStyleSheet("background-color: #333;")
        self.layout.addWidget(self.divider)

        # Charts Row (Carousel)
        charts_header_layout = QHBoxLayout()
        self.analytics_title = QLabel("Platform Security Analytics")
        self.analytics_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #00ccff;")
        charts_header_layout.addWidget(self.analytics_title)
        
        self.prev_btn = QPushButton("<")
        self.next_btn = QPushButton(">")
        self.prev_btn.setFixedSize(35, 35)
        self.next_btn.setFixedSize(35, 35)
        self.prev_btn.setStyleSheet("background-color: #2b2b2b; color: white; border-radius: 4px;")
        self.next_btn.setStyleSheet("background-color: #2b2b2b; color: white; border-radius: 4px;")
        self.prev_btn.clicked.connect(self.prev_chart)
        self.next_btn.clicked.connect(self.next_chart)
        
        charts_header_layout.addStretch()
        charts_header_layout.addWidget(self.prev_btn)
        charts_header_layout.addWidget(self.next_btn)
        self.layout.addLayout(charts_header_layout)

        self.chart_stack = QStackedWidget()
        self.chart_stack.setFixedHeight(500) 
        
        # Risk Chart Page
        self.risk_page = QWidget()
        risk_vbox = QVBoxLayout(self.risk_page)
        risk_vbox.setContentsMargins(0, 20, 0, 20)
        self.risk_title_lbl = QLabel("VULNERABILITY SEVERITY RISK MATRIX")
        self.risk_title_lbl.setStyleSheet("font-size: 16px; font-weight: bold; color: #888; letter-spacing: 1px;")
        self.risk_title_lbl.setAlignment(Qt.AlignCenter)
        self.risk_chart_lbl = QLabel()
        self.risk_chart_lbl.setAlignment(Qt.AlignCenter)
        risk_vbox.addWidget(self.risk_title_lbl)
        risk_vbox.addWidget(self.risk_chart_lbl)
        
        # Scan Chart Page
        self.scan_page = QWidget()
        scan_vbox = QVBoxLayout(self.scan_page)
        scan_vbox.setContentsMargins(0, 20, 0, 20)
        self.scan_title_lbl = QLabel("ASSESSMENT VELOCITY (7-DAY TREND)")
        self.scan_title_lbl.setStyleSheet("font-size: 16px; font-weight: bold; color: #888; letter-spacing: 1px;")
        self.scan_title_lbl.setAlignment(Qt.AlignCenter)
        self.scan_chart_lbl = QLabel()
        self.scan_chart_lbl.setAlignment(Qt.AlignCenter)
        scan_vbox.addWidget(self.scan_title_lbl)
        scan_vbox.addWidget(self.scan_chart_lbl)
        
        self.chart_stack.addWidget(self.risk_page)
        self.chart_stack.addWidget(self.scan_page)
        self.layout.addWidget(self.chart_stack)

        # Recent Activity (Moved to Bottom as Terminal)
        self.recent_events_title = QLabel("RECENT SECURITY EVENTS")
        self.recent_events_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #555; letter-spacing: 1px;")
        self.layout.addWidget(self.recent_events_title)
        
        self.activity_box = QFrame()
        self.activity_box.setMinimumHeight(250)
        box_layout = QVBoxLayout(self.activity_box)
        box_layout.setContentsMargins(10, 10, 10, 10)
        
        self.layout.addWidget(self.activity_box)
        
        theme = db_manager.get_setting("theme", "Dark (Kali)")
        self.apply_styles(theme)
        self.refresh_stats()

    def apply_styles(self, theme_name):
        is_light = theme_name == "Light (Professional)"
        accent = "#0078d4" if is_light else "#00ccff"
        text = "#333333" if is_light else "#f0f0f0"
        subtext = "#777777" if is_light else "#555555"
        label_text = "#555555" if is_light else "#888888"
        bg = "#ffffff" if is_light else "#0d0d0d"
        border = "#cccccc" if is_light else "#333"
        card_bg = "#f0f0f0" if is_light else "#2b2b2b"

        # Update StatCards
        for card in [self.project_stat, self.scan_stat, self.finding_stat, self.health_stat]:
            card.apply_styles(theme_name)

        # Update Headers
        self.header_lbl.setStyleSheet(f"font-size: 28px; font-weight: bold; color: {text};")
        self.analytics_title.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {accent};")
        self.recent_events_title.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {label_text}; letter-spacing: 1px;")
        
        # Update Nav Buttons
        btn_style = f"background-color: {card_bg}; color: {text}; border-radius: 4px;"
        self.prev_btn.setStyleSheet(btn_style)
        self.next_btn.setStyleSheet(btn_style)
        
        # Update Chart Titles
        self.risk_title_lbl.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {label_text}; letter-spacing: 1px;")
        self.scan_title_lbl.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {label_text}; letter-spacing: 1px;")
        
        # Update Activity Box
        self.activity_box.setStyleSheet(f"background-color: {bg}; border: 1px solid {border}; border-radius: 4px;")
        
        # Refresh Charts with new colors
        self.generate_charts()

    def next_chart(self):
        curr = self.chart_stack.currentIndex()
        self.chart_stack.setCurrentIndex((curr + 1) % self.chart_stack.count())

    def prev_chart(self):
        curr = self.chart_stack.currentIndex()
        self.chart_stack.setCurrentIndex((curr - 1) % self.chart_stack.count())

    def generate_charts(self):
        try:
            conn = db_manager.get_connection()
            theme = db_manager.get_setting("theme", "Dark (Kali)")
            text_color = "white" if "Dark" in theme else "black"
            bg_color = "#1e1e1e" if "Dark" in theme else "#f4f4f4"

            # Risk Distribution Chart
            findings = conn.execute("SELECT severity, COUNT(*) FROM findings GROUP BY severity").fetchall()
            if findings:
                labels = [f[0] for f in findings]
                counts = [f[1] for f in findings]
                colors_map = {
                    'Critical': '#8B0000', 'High': '#FF4500', 
                    'Medium': '#DAA520', 'Low': '#2E8B57', 'Info': '#4682B4'
                }
                c_list = [colors_map.get(l.capitalize(), '#808080') for l in labels]

                plt.figure(figsize=(7, 4.5), facecolor=bg_color)
                plt.pie(counts, labels=labels, colors=c_list, autopct='%1.1f%%', textprops={'color': text_color}, wedgeprops=dict(width=0.4))
                
                buf = BytesIO()
                plt.savefig(buf, format='png', transparent=True, dpi=100, bbox_inches='tight', pad_inches=0.05)
                plt.close()
                self.risk_chart_lbl.setPixmap(QPixmap.fromImage(QImage.fromData(buf.getvalue())))
            else:
                self.risk_chart_lbl.setText("NO RISK DATA DISCOVERED YET")
                self.risk_chart_lbl.setStyleSheet("color: #555; font-style: italic;")

            # Scan Activity Chart
            scans = conn.execute("SELECT date(created_at) as d, COUNT(*) FROM scans GROUP BY d ORDER BY d DESC LIMIT 7").fetchall()
            if scans:
                dates = [s[0] for s in scans]
                counts = [s[1] for s in scans]
                
                plt.figure(figsize=(7, 4.5), facecolor=bg_color)
                plt.bar(dates, counts, color='#00ccff')
                plt.xticks(rotation=45, color=text_color)
                plt.yticks(color=text_color)
                plt.tight_layout()
                
                buf = BytesIO()
                plt.savefig(buf, format='png', transparent=True, dpi=100, bbox_inches='tight', pad_inches=0.1)
                plt.close()
                self.scan_chart_lbl.setPixmap(QPixmap.fromImage(QImage.fromData(buf.getvalue())))
            else:
                self.scan_chart_lbl.setText("NO ASSESSMENT ACTIVITY LOGGED")
                self.scan_chart_lbl.setStyleSheet("color: #555; font-style: italic;")
        except Exception:
            pass

    def refresh_stats(self):
        try:
            conn = db_manager.get_connection()
            # Summary stats
            proj_count = conn.execute("SELECT COUNT(*) FROM projects").fetchone()[0]
            scan_count = conn.execute("SELECT COUNT(*) FROM scans").fetchone()[0]
            critical_findings = conn.execute("SELECT COUNT(*) FROM findings WHERE severity = 'Critical'").fetchone()[0]
            
            self.project_stat.val_lbl.setText(str(proj_count))
            self.scan_stat.val_lbl.setText(str(scan_count))
            self.finding_stat.val_lbl.setText(str(critical_findings))
            
            # Health Logic: Start at 100%, -5% per critical finding (min 0%)
            health = max(0, 100 - (critical_findings * 5))
            self.health_stat.val_lbl.setText(f"{health}%")
            if health < 80: self.health_stat.val_lbl.setStyleSheet(self.health_stat.val_lbl.styleSheet() + " color: #ff3333;")
            elif health < 90: self.health_stat.val_lbl.setStyleSheet(self.health_stat.val_lbl.styleSheet() + " color: #ffaa00;")
            
            # Recent Activity
            recent_scans = conn.execute("SELECT type, target, status, created_at FROM scans ORDER BY created_at DESC LIMIT 5").fetchall()
            
            if recent_scans:
                # Clear placeholder
                for i in reversed(range(self.activity_box.layout().count())): 
                    self.activity_box.layout().itemAt(i).widget().setParent(None)
                
                for scan in recent_scans:
                    item = QLabel(f"<span style='color: #555;'>[{scan['created_at']}]</span> <span style='color: #00ccff;'>{scan['type']}</span> operation on <span style='color: #00ff00;'>{scan['target']}</span> status: <span style='color: #ffaa00;'>{scan['status']}</span>")
                    item.setStyleSheet("padding: 2px; color: #f0f0f0; font-family: 'Courier New'; font-size: 11px;")
                    self.activity_box.layout().addWidget(item)
                self.activity_box.layout().addStretch()
            
            self.generate_charts()
        except Exception:
            pass
