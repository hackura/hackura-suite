from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QLineEdit, QPlainTextEdit, QFrame, QListWidget, QListWidgetItem
)
from PySide6.QtCore import Qt, Signal, QObject
from core.dag_engine import dag_engine

class OrchestratorView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(40, 40, 40, 40)
        self.layout.setSpacing(20)

        header = QLabel("Workflow Orchestrator (DAG)")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #ffaa00;")
        self.layout.addWidget(header)

        # Pipeline Builder
        main_h_layout = QHBoxLayout()
        
        # Left: Builder
        builder_frame = QFrame()
        builder_frame.setStyleSheet("background-color: #2b2b2b; border: 1px solid #3d3d3d; border-radius: 8px;")
        builder_layout = QVBoxLayout(builder_frame)
        
        builder_layout.addWidget(QLabel("Pipeline Steps:"))
        self.step_list = QListWidget()
        self.step_list.setStyleSheet("background-color: #1a1a1a;")
        builder_layout.addWidget(self.step_list)
        
        add_step_layout = QHBoxLayout()
        self.tool_input = QLineEdit()
        self.tool_input.setPlaceholderText("Tool (e.g. Nmap)")
        self.target_input = QLineEdit()
        self.target_input.setPlaceholderText("Target")
        add_btn = QPushButton("ADD STEP")
        add_btn.clicked.connect(self.add_step)
        
        add_step_layout.addWidget(self.tool_input)
        add_step_layout.addWidget(self.target_input)
        add_step_layout.addWidget(add_btn)
        builder_layout.addLayout(add_step_layout)
        
        self.run_btn = QPushButton("EXECUTE ORCHESTRATION")
        self.run_btn.setStyleSheet("background-color: #ffaa00; color: black; font-weight: bold; height: 40px;")
        self.run_btn.clicked.connect(self.run_pipeline)
        builder_layout.addWidget(self.run_btn)
        
        main_h_layout.addWidget(builder_frame, 1)
        
        # Right: Console
        self.console = QPlainTextEdit()
        self.console.setReadOnly(True)
        self.console.setStyleSheet("background-color: #000; color: #ffaa00; font-family: monospace; border: 1px solid #333;")
        main_h_layout.addWidget(self.console, 2)
        
        self.layout.addLayout(main_h_layout)

    def add_step(self):
        tool = self.tool_input.text()
        target = self.target_input.text()
        if not tool or not target: return
        
        item_text = f"{tool} -> {target}"
        item = QListWidgetItem(item_text)
        item.setData(Qt.UserRole, {"tool": tool, "target": target})
        self.step_list.addItem(item)
        self.tool_input.clear()
        self.target_input.clear()

    def run_pipeline(self):
        steps = []
        for i in range(self.step_list.count()):
            item = self.step_list.item(i)
            data = item.data(Qt.UserRole)
            steps.append({
                "id": str(i+1),
                "tool": data['tool'],
                "target": data['target']
            })
            
        if not steps: return
        
        self.run_btn.setEnabled(False)
        self.console.clear()
        
        dag_engine.execute_workflow(
            "Custom DAG", 
            steps, 
            callback=self.update_console
        )

    def update_console(self, msg):
        self.console.appendPlainText(msg)
        if "Finished" in msg or "Stopping" in msg:
            self.run_btn.setEnabled(True)

    def refresh_projects(self): pass
