# 유저 등록 GUI # index3
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QWidget, QFrame,
    QVBoxLayout,
    QLabel, QLineEdit, QPushButton, QCheckBox
    )

class RegistrationForm(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(40, 50, 40, 50)
        layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        # 이전 버튼 (로그인 화면)
        self.back_btn = QPushButton()
        icon = QIcon("src/assets/icons/arrow-pointing-to-left-64px.png")
        self.back_btn.setIcon(icon)
        self.back_btn.setIconSize(QSize(25, 25))
        self.back_btn.clicked.connect(self.handle_back)

        self.id_label = QLabel("아이디")
        self.id_textedit = QLineEdit()
        self.id_textedit.setPlaceholderText("아이디를 입력해주세요.")

        self.pw_label = QLabel("비밀번호")
        self.pw_textedit = QLineEdit()
        self.pw_textedit.setPlaceholderText("비밀번호를 입력해주세요.")
        self.pw_textedit.setEchoMode(QLineEdit.EchoMode.Password)

        self.check_label = QLabel("비밀번호 확인")
        self.check_textedit = QLineEdit()
        self.check_textedit.setPlaceholderText("다시 한번 입력해주세요.")
        self.check_textedit.setEchoMode(QLineEdit.EchoMode.Password)

        self.check_agree = QCheckBox("얼굴 등록 및 인식 동의")

        self.face_register_btn = QPushButton("얼굴 등록")
        self.face_register_btn.setObjectName("FaceRegisterBTN")
        self.face_register_btn.clicked.connect(self.handle_face_regist)

        self.line = QFrame()
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setStyleSheet("QFrame { color: #D0D0D0; }")

        self.user_register_btn = QPushButton("유저 등록")
        self.user_register_btn.setObjectName("UserRegisterBTN")
        self.user_register_btn.clicked.connect(self.handle_user_regist)

        layout.addWidget(self.back_btn, 0, Qt.AlignmentFlag.AlignLeft)
        layout.addSpacing(15)
        layout.addWidget(self.id_label)
        layout.addWidget(self.id_textedit)
        layout.addWidget(self.pw_label)
        layout.addWidget(self.pw_textedit)
        layout.addWidget(self.check_label)
        layout.addWidget(self.check_textedit)
        layout.addSpacing(15)
        layout.addWidget(self.check_agree)
        layout.addSpacing(15)
        layout.addWidget(self.face_register_btn)
        layout.addWidget(self.line)
        layout.addWidget(self.user_register_btn)

        self.setLayout(layout)

    def handle_back(self):
        self.controller.switch_to_screen(0)

    def handle_face_regist(self):
        self.controller.switch_to_screen(4)

    def handle_user_regist(self):
        self.controller.switch_to_screen(2)