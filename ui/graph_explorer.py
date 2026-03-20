from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGraphicsView, QGraphicsScene, 
    QGraphicsItem, QGraphicsEllipseItem, QGraphicsLineItem, QGraphicsTextItem,
    QPushButton, QMenu, QMessageBox, QLineEdit
)
from PySide6.QtCore import Qt, QPointF, QRectF
from PySide6.QtGui import QPen, QBrush, QColor, QPainter
from core.graph_engine import GraphEngine

class NodeItem(QGraphicsEllipseItem):
    def __init__(self, entity, parent=None):
        super().__init__(-20, -20, 40, 40, parent)
        self.entity = entity
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        
        self.setBrush(QBrush(QColor("#00ccff")))
        self.setPen(QPen(Qt.black, 2))
        
        self.label = QGraphicsTextItem(entity.name, self)
        self.label.setPos(-20, 20)
        self.label.setDefaultTextColor(Qt.white)
        
        self.edges = []

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionHasChanged:
            for edge in self.edges:
                edge.update_position()
        return super().itemChange(change, value)

class EdgeItem(QGraphicsLineItem):
    def __init__(self, source_item, target_item, label_text):
        super().__init__()
        self.source_item = source_item
        self.target_item = target_item
        self.label_text = label_text
        self.setPen(QPen(QColor("#888"), 1, Qt.DashLine))
        self.setZValue(-1)
        
        self.label = QGraphicsTextItem(label_text)
        self.label.setDefaultTextColor(QColor("#888"))
        
        self.update_position()

    def update_position(self):
        line = QGraphicsLineItem().line()
        line.setP1(self.source_item.scenePos())
        line.setP2(self.target_item.scenePos())
        self.setLine(line)
        
        # Center label
        mid_point = (self.source_item.scenePos() + self.target_item.scenePos()) / 2
        self.label.setPos(mid_point)

class GraphExplorerView(QWidget):
    def __init__(self):
        super().__init__()
        self.engine = GraphEngine()
        self.node_items = {}
        
        layout = QVBoxLayout(self)
        
        top_bar = QHBoxLayout()
        
        self.domain_input = QLineEdit()
        self.domain_input.setPlaceholderText("Enter target domain (e.g. hackura.io)")
        self.domain_input.setFixedWidth(300)
        self.domain_input.setFixedHeight(35)
        self.domain_input.setStyleSheet("background: #252525; border: 1px solid #333; padding-left: 10px; color: #00ccff;")
        top_bar.addWidget(self.domain_input)
        
        add_btn = QPushButton("Add Target Domain")
        add_btn.setFixedHeight(35)
        add_btn.setStyleSheet("background-color: #333; color: #00ccff; padding: 0 15px;")
        add_btn.clicked.connect(self.add_initial_target)
        top_bar.addWidget(add_btn)
        
        top_bar.addStretch()
        layout.addLayout(top_bar)
        
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setDragMode(QGraphicsView.ScrollHandDrag)
        self.view.setStyleSheet("background-color: #1a1a1a; border: 1px solid #333;")
        layout.addWidget(self.view)
        
        self.view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.view.customContextMenuRequested.connect(self.show_context_menu)

    def add_initial_target(self):
        domain = self.domain_input.text().strip()
        if not domain:
            QMessageBox.warning(self, "Error", "Please enter a valid target domain.")
            return
            
        e = self.engine.add_entity(domain, "Domain")
        self.create_node_item(e, QPointF(0, 0))
        self.domain_input.clear()

    def create_node_item(self, entity, pos):
        item = NodeItem(entity)
        item.setPos(pos)
        self.scene.addItem(item)
        self.node_items[entity.id] = item
        return item

    def show_context_menu(self, pos):
        item = self.view.itemAt(pos)
        if isinstance(item, NodeItem):
            menu = QMenu()
            dns_action = menu.addAction("Run Transform: DNS Resolve")
            whois_action = menu.addAction("Run Transform: Whois Email")
            
            action = menu.exec(self.view.mapToGlobal(pos))
            if action == dns_action:
                self.run_transform_on_item(item, "DNS Resolve")
            elif action == whois_action:
                self.run_transform_on_item(item, "Whois Email")

    def run_transform_on_item(self, item, transform_name):
        new_entities = self.engine.run_transform(item.entity.id, transform_name)
        for i, e in enumerate(new_entities):
            # Place new node nearby
            offset = QPointF(100, (i - (len(new_entities)-1)/2) * 80)
            new_item = self.create_node_item(e, item.scenePos() + offset)
            
            # Create edge
            edge = EdgeItem(item, new_item, transform_name)
            self.scene.addItem(edge)
            self.scene.addItem(edge.label)
            item.edges.append(edge)
            new_item.edges.append(edge)
