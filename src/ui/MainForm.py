# 메인 화면 # index2
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit, QPushButton

class MainForm(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 40, 30 ,40)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.avatar = QLabel("🐵")
        self.avatar.setFixedSize(130, 130)
        self.avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.avatar.setFont(QFont("Arial", 42))
        self.avatar.setStyleSheet("background-color: #E0E0E0; border-radius: 65px;")

        self.toggle_btn = QPushButton("⏸️")
        self.toggle_btn.setFixedSize(50, 50)
        self.toggle_btn.setStyleSheet("""
            QPushButton {
                background-color: #A6FF4D;
                border-radius: 25px;
                font-size: 18px;
            }
            QPushButton:hover { background-color: #95E644; }
        """)

        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setPlainText("21:38 | Laptop Locked\n21:39 | Laptop UnLocked") # (Temp)
        self.log_display.setStyleSheet("""
            QTextEdit {
                background-color: #FFFFFF;
                border: 1px solid #E0E0E0;
                border-radius: 5px;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 13px;
                color: #333333;
                padding: 10px;
            }
        """)

        layout.addWidget(self.avatar, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.toggle_btn, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.log_display)

        self.setLayout(layout)