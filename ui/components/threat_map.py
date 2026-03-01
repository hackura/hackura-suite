from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QPixmap, QColor, QPen, QRadialGradient, QPainterPath, QFont, QMouseEvent, QWheelEvent
from PySide6.QtCore import Qt, QTimer, QPointF, QRect, QPoint
from core.db import db_manager
import random
import os

class ThreatMapWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.map_pixmap = QPixmap()
        self.threats = [] # List of {pos, age, color, is_dst}
        self.attacks = [] # List of {path, age, color}
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(50)
        self.setMinimumHeight(400)
        
        theme = db_manager.get_setting("theme", "Dark (Kali)")
        self.apply_styles(theme)


    def apply_styles(self, theme_name):
        self.is_light = theme_name == "Light (Professional)"
        # Enforce DARK MAP as requested by user ("make sure all maps are in dark mode")
        asset_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "assets", "threat_map_v3.png")
        self.map_pixmap = QPixmap(asset_path)
        self.update()

    def coord_to_pos(self, lat, lon, target_rect):
        # Precise mapping based on the actual drawn map rectangle
        w = target_rect.width()
        h = target_rect.height()
        x = target_rect.left() + (lon + 180) * (w / 360)
        # Standard Equirectangular projection mapping
        y = target_rect.top() + (90 - lat) * (h / 180) 
        return QPointF(x, y)

    def add_threat(self, src_lat, src_lon, dst_lat, dst_lon, severity="High"):
        # Store raw coordinates for aspect-aware calculation in paintEvent
        colors = {
            "Critical": QColor("#ff3333"),
            "High": QColor("#ffaa00"),
            "Medium": QColor("#ffff00"),
            "Info": QColor("#00ccff")
        }
        color = colors.get(severity, QColor("#ffffff"))
        
        # Add source pulse
        self.threats.append({
            "lat": src_lat, "lon": src_lon, 
            "age": 0.0, "color": color, "is_dst": False
        })
        # Add destination target
        self.threats.append({
            "lat": dst_lat, "lon": dst_lon, 
            "age": 0.5, "color": color, "is_dst": True
        })
        
        # Create arc path data (will be built in paintEvent)
        self.attacks.append({
            "src": (src_lat, src_lon), 
            "dst": (dst_lat, dst_lon), 
            "age": 0.0, "color": color
        })

    def update_animation(self):
        # Update threats (pulses)
        for t in self.threats[:]:
            t["age"] += 0.03
            if t["age"] > 1.0:
                self.threats.remove(t)
                
        # Update attacks (arcs)
        for a in self.attacks[:]:
            a["age"] += 0.02
            if a["age"] > 1.2: # Allow lingering
                self.attacks.remove(a)
                
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 1. Calculate Aspect-Preserving Map Rect
        if self.map_pixmap.isNull(): return
        
        map_w = self.map_pixmap.width()
        map_h = self.map_pixmap.height()
        widget_w = self.width()
        widget_h = self.height()
        
        scale_aspect = min(widget_w / map_w, widget_h / map_h)
        draw_w = map_w * scale_aspect
        draw_h = map_h * scale_aspect
        draw_x = (widget_w - draw_w) / 2
        draw_y = (widget_h - draw_h) / 2
        map_rect = QRect(int(draw_x), int(draw_y), int(draw_w), int(draw_h))

        # 2. Draw Background Map (Aspect Preserved)
        painter.drawPixmap(map_rect, self.map_pixmap)
            
        # 3. Draw Arcs (Attacks)
        for a in self.attacks:
            src_lat, src_lon = a["src"]
            dst_lat, dst_lon = a["dst"]
            src_pos = self.coord_to_pos(src_lat, src_lon, map_rect)
            dst_pos = self.coord_to_pos(dst_lat, dst_lon, map_rect)
            
            # Reconstruct Path
            path = QPainterPath()
            path.moveTo(src_pos)
            mid_x = (src_pos.x() + dst_pos.x()) / 2
            mid_y = min(src_pos.y(), dst_pos.y()) - (abs(src_pos.x() - dst_pos.x()) * 0.2)
            path.quadTo(QPointF(mid_x, mid_y), dst_pos)
            
            age = a["age"]
            color = QColor(a["color"])
            
            path_alpha = max(0, min(255, int(200 * (1.0 - age))))
            if path_alpha > 0:
                pen_color = QColor(color)
                pen_color.setAlpha(path_alpha)
                painter.setPen(QPen(pen_color, 1, Qt.DotLine))
                painter.drawPath(path)
            
            if age <= 1.0:
                for i in range(10):
                    p = max(0, age - (i * 0.01))
                    pos = path.pointAtPercent(p)
                    tail_alpha = max(0, min(255, int(255 * (1.0 - (i / 10.0)))))
                    tail_color = QColor(color)
                    tail_color.setAlpha(tail_alpha)
                    size = (4 - (i * 0.3))
                    if size > 0:
                        painter.setBrush(tail_color)
                        painter.setPen(Qt.NoPen)
                        painter.drawEllipse(pos, size, size)
            
            if 0.95 < age < 1.1:
                flash_alpha = max(0, min(255, int(255 * (1.1 - age) * 10)))
                flash_color = QColor(color)
                flash_color.setAlpha(flash_alpha)
                painter.setBrush(flash_color)
                painter.drawEllipse(dst_pos, 10, 10)

        # 4. Draw Pulses
        for t in self.threats:
            pos = self.coord_to_pos(t["lat"], t["lon"], map_rect)
            alpha = max(0, min(255, int(255 * (1.0 - t["age"]))))
            color = QColor(t["color"])
            color.setAlpha(alpha)
            
            radius = t["age"] * (50 if t["is_dst"] else 30)
            painter.setBrush(Qt.NoBrush)
            painter.setPen(QPen(color, 2))
            painter.drawEllipse(pos, radius, radius)
            
            color.setAlpha(255)
            painter.setBrush(color)
            painter.drawEllipse(pos, 4, 4)

        self.draw_legend(painter)

    def draw_legend(self, painter):
        # Professional HUD-style legend (Always High Contrast for Dark Map)
        bg_color = QColor(0, 0, 0, 180) 
        border_color = QColor("#00ccff") 
        text_primary = QColor("#ffffff") 
        text_secondary = QColor("#a0a0a0") 
 
        legend_rect = QRect(20, self.height() - 140, 180, 120)
        painter.setBrush(bg_color)
        painter.setPen(QPen(border_color, 1))
        painter.drawRoundedRect(legend_rect, 5, 5)
        
        painter.setPen(text_primary)
        painter.setFont(QFont("Inter", 10, QFont.Bold))
        painter.drawText(35, self.height() - 110, "THREAT SEVERITY")
        
        painter.setFont(QFont("Inter", 8, QFont.Bold))
        items = [
            ("CRITICAL", "#ff3333"),
            ("HIGH RISK", "#ffaa00"),
            ("MEDIUM", "#ffff00"),
            ("PASSIVE", "#00ccff")
        ]
        
        for i, (label, color_code) in enumerate(items):
            y_off = self.height() - 90 + (i * 20)
            painter.setBrush(QColor(color_code))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(35, y_off - 8, 8, 8)
            painter.setPen(text_secondary)
            painter.drawText(50, y_off, label)
