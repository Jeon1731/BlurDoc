# 로그인 GUI
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton

class LoginForm(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(40, 50, 40, 50)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 고정 더미 아바타 (로그인 전)
        self.avatar = QLabel("🐵")
        self.avatar.setFixedSize(150, 150)
        self.avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.avatar.setFont(QFont("Arial", 48))
        self.avatar.setStyleSheet("background-color: #E0E0E0; border-radius: 75px;")

        self.id_textedit = QLineEdit()
        self.id_textedit.setPlaceholderText("아이디를 입력해주세요.")

        self.pw_textedit = QLineEdit()
        self.pw_textedit.setPlaceholderText("비밀번호를 입력해주세요.")
        self.pw_textedit.setEchoMode(QLineEdit.EchoMode.Password)

        self.login_btn = QPushButton("로그인")
        self.login_btn.setObjectName("LoginBTN")
        self.login_btn.clicked.connect(self.handle_login)

        self.register_btn = QPushButton("유저 등록")
        self.register_btn.setObjectName("RegisterBTN")

        layout.addWidget(self.avatar, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(20)
        layout.addWidget(self.id_textedit)
        layout.addWidget(self.pw_textedit)
        layout.addSpacing(10)
        layout.addWidget(self.login_btn)
        layout.addWidget(self.register_btn)

        self.setLayout(layout)

    def handle_login(self):
        self.controller.switch_to_screen(1)