import sys
from PySide6.QtCore import Qt, QTimer, QSize
from PySide6.QtGui import QFont, QPixmap, QPainter, QBrush, QColor
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QLabel, QStackedWidget, QTextEdit
)

# ----------------------------------------------------------------------
# 1. 커스텀 원형 아바타 위젯 (스케치의 원형 프로필 구현)
# ----------------------------------------------------------------------
class CircularAvatar(QLabel):
    def __init__(self, size=150, parent=None):
        super().__init__(parent)
        self.setFixedSize(size, size)
        self.setScaledContents(True)
        # 기본 배경 원 칠하기 (이미지가 없을 때 대비)
        self.setStyleSheet("background-color: #E0E0E0; border-radius: 75px;")
        
    def set_avatar_text(self, text="👤"):
        self.setText(text)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFont(QFont("Arial", 48))

# ----------------------------------------------------------------------
# 2. 로그인 화면 (Page 1 - 좌측)
# ----------------------------------------------------------------------
class LoginScreen(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(40, 50, 40, 50)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 상단 아바타
        self.avatar = CircularAvatar(150)
        self.avatar.set_avatar_text("👩")
        
        # 입력 필드
        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("아이디를 입력해주세요.")
        
        self.pw_input = QLineEdit()
        self.pw_input.setPlaceholderText("비밀번호를 입력해주세요.")
        self.pw_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        # 버튼들
        self.login_btn = QPushButton("로그인")
        self.login_btn.setObjectName("PrimaryBtn")
        self.login_btn.clicked.connect(self.handle_login)
        
        self.register_btn = QPushButton("유저 등록")
        self.register_btn.setObjectName("SecondaryBtn")
        
        # 레이아웃 조립
        layout.addWidget(self.avatar, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(20)
        layout.addWidget(self.id_input)
        layout.addWidget(self.pw_input)
        layout.addSpacing(10)
        layout.addWidget(self.login_btn)
        layout.addWidget(self.register_btn)
        
        self.setLayout(layout)
        
    def handle_login(self):
        # 로그인 버튼 클릭 시 얼굴 인식 화면으로 전환
        self.controller.switch_to_screen(1)

# ----------------------------------------------------------------------
# 3. 얼굴 인식 화면 (Page 1 - 우측 로딩 상태)
# ----------------------------------------------------------------------
class FaceAuthScreen(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(25)
        layout.setContentsMargins(40, 50, 40, 50)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 상태 타이틀
        self.title_label = QLabel("얼굴을 인식중입니다...")
        self.title_label.setFont(QFont("Malgun Gothic", 16, QFont.Weight.Bold))
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 인식 영역 링 효과 디자인 (연두색 글로우 스타일)
        self.avatar = CircularAvatar(180)
        self.avatar.set_avatar_text("👩")
        self.avatar.setStyleSheet("""
            background-color: #E8F5E9;
            border: 4px solid #A6FF4D;
            border-radius: 90px;
        """)
        
        # 하단 안내 텍스트
        self.sub_label = QLabel("정면을 바라봐주세요")
        self.sub_label.setFont(QFont("Malgun Gothic", 12))
        self.sub_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(self.title_label)
        layout.addWidget(self.avatar, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.sub_label)
        
        self.setLayout(layout)
        
    def start_auth_simulation(self):
        # 2초 뒤 자동으로 메인 화면으로 넘어가도록 타이머 설정
        QTimer.singleShot(2000, lambda: self.controller.switch_to_screen(2))

# ----------------------------------------------------------------------
# 4. 메인 화면 (Page 2 - 대시보드 및 로그 기록)
# ----------------------------------------------------------------------
class MainScreen(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 40, 30, 40)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 중앙 아바타
        self.avatar = CircularAvatar(130)
        self.avatar.set_avatar_text("👩")
        
        # 토글 버튼 (재생/일시정지 형태의 컨트롤러 버튼)
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
        
        # 상태 로그창 (텍스트 에디터)
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setPlainText("21:38 | Laptop Locked\n21:39 | Laptop UnLocked")
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
        
        # 레이아웃 조립
        layout.addWidget(self.avatar, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.toggle_btn, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.log_display)
        
        self.setLayout(layout)

# ----------------------------------------------------------------------
# 5. 메인 윈도우 컨트롤러 (화면 전환 관리)
# ----------------------------------------------------------------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Face Recognition System")
        self.setFixedSize(380, 620) # 스케치 비율에 맞춘 세로형 모바일/키오스크 크기
        
        # 메인 스택 위젯 선언
        self.central_stacked = QStackedWidget()
        self.setCentralWidget(self.central_stacked)
        
        # 각 화면 인스턴스 생성 및 스택 등록
        self.login_screen = LoginScreen(self)
        self.face_auth_screen = FaceAuthScreen(self)
        self.main_screen = MainScreen(self)
        
        self.central_stacked.addWidget(self.login_screen)    # Index 0
        self.central_stacked.addWidget(self.face_auth_screen) # Index 1
        self.central_stacked.addWidget(self.main_screen)      # Index 2
        
        # 글로벌 QSS 스타일시트 적용 (스케치북 감성 반영)
        self.setStyleSheet("""
            QWidget {
                background-color: #F5F5F5;
                color: #333333;
                font-family: 'Malgun Gothic', Arial, sans-serif;
            }
            QLineEdit {
                background-color: #FFFFFF;
                border: 1px solid #E0E0E0;
                border-radius: 20px;
                padding: 10px 15px;
                font-size: 13px;
                color: #666666;
            }
            QLineEdit:focus {
                border: 1px solid #A6FF4D;
            }
            QPushButton#PrimaryBtn {
                background-color: #A6FF4D;
                border: none;
                border-radius: 20px;
                padding: 12px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton#PrimaryBtn:hover {
                background-color: #95E644;
            }
            QPushButton#SecondaryBtn {
                background-color: #FFFFFF;
                border: 1px solid #D0D0D0;
                border-radius: 8px;
                padding: 10px;
                font-size: 13px;
                color: #555555;
            }
            QPushButton#SecondaryBtn:hover {
                background-color: #EEEEEE;
            }
        """)

    def switch_to_screen(self, index):
        self.central_stacked.setCurrentIndex(index)
        # 얼굴 인식 화면(Index 1)으로 들어갔을 때만 시뮬레이션 타이머 작동
        if index == 1:
            self.face_auth_screen.start_auth_simulation()

# ----------------------------------------------------------------------
# 프로그램 실행 진입점
# ----------------------------------------------------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
