import sys
import cv2
from PySide6.QtCore import Qt, QTimer, QThread, Signal, Slot
from PySide6.QtGui import QFont, QImage, QPixmap
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QLineEdit, QPushButton, QLabel, QStackedWidget, QTextEdit
)

# ----------------------------------------------------------------------
# 1. OpenCV 카메라 백그라운드 스레드
# ----------------------------------------------------------------------
class CameraThread(QThread):
    # GUI 스레드로 이미지를 전달하기 위한 시그널
    frame_received = Signal(QImage)

    def __init__(self):
        super().__init__()
        self.running = False
        self.cap = None

    def run(self):
        # 0번 기본 웹캠 열기
        self.cap = cv2.VideoCapture(0)
        self.running = True
        
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                continue
            
            # OpenCV(BGR) 이미지를 RGB로 변환
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            
            # QImage 객체로 변환
            qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            
            # 크롭 처리를 하지 않고 스케치 비율에 맞춰 정방형으로 크기 조정 유도 (GUI에서 처리)
            self.frame_received.emit(qt_image)
            
            # 대략 30fps 수준으로 유지
            self.msleep(33)
            
        if self.cap:
            self.cap.release()

    def stop(self):
        self.running = False
        self.wait()

# ----------------------------------------------------------------------
# 2. 커스텀 원형 프로필 및 카메라 뷰 위젯
# ----------------------------------------------------------------------
class CircularCameraWidget(QLabel):
    def __init__(self, size=180, parent=None):
        super().__init__(parent)
        self.setFixedSize(size, size)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 기본 스타일: 녹색 원형 테두리 적용 (스케치북 UI 반영)
        self.setStyleSheet(f"""
            background-color: #E8F5E9;
            border: 4px solid #A6FF4D;
            border-radius: {size // 2}px;
        """)
        
    @Slot(QImage)
    def update_frame(self, qt_image):
        # 원형 위젯 크기에 맞춰 이미지를 자르거나 축소하여 매핑
        # border-radius가 지정되어 있어 라벨 내부 이미지가 원형으로 마스킹됩니다.
        scaled_pixmap = QPixmap.fromImage(qt_image).scaled(
            self.width(), self.height(),
            Qt.AspectRatioMode.KeepAspectRatioByExpanding,
            Qt.TransformationMode.SmoothTransformation
        )
        self.setPixmap(scaled_pixmap)

# ----------------------------------------------------------------------
# 3. 로그인 화면 (Page 1 - 좌측)
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
        
        # 고정 더미 아바타 (로그인 전)
        self.avatar = QLabel("👩")
        self.avatar.setFixedSize(150, 150)
        self.avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.avatar.setFont(QFont("Arial", 48))
        self.avatar.setStyleSheet("background-color: #E0E0E0; border-radius: 75px;")
        
        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("아이디를 입력해주세요.")
        
        self.pw_input = QLineEdit()
        self.pw_input.setPlaceholderText("비밀번호를 입력해주세요.")
        self.pw_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        self.login_btn = QPushButton("로그인")
        self.login_btn.setObjectName("PrimaryBtn")
        self.login_btn.clicked.connect(self.handle_login)
        
        self.register_btn = QPushButton("유저 등록")
        self.register_btn.setObjectName("SecondaryBtn")
        
        layout.addWidget(self.avatar, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(20)
        layout.addWidget(self.id_input)
        layout.addWidget(self.pw_input)
        layout.addSpacing(10)
        layout.addWidget(self.login_btn)
        layout.addWidget(self.register_btn)
        
        self.setLayout(layout)
        
    def handle_login(self):
        self.controller.switch_to_screen(1)

# ----------------------------------------------------------------------
# 4. 얼굴 인식 화면 (Page 1 - 우측, 실제 카메라 구동)
# ----------------------------------------------------------------------
class FaceAuthScreen(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.camera_thread = None
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(25)
        layout.setContentsMargins(40, 50, 40, 50)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.title_label = QLabel("얼굴을 인식중입니다...")
        self.title_label.setFont(QFont("Malgun Gothic", 16, QFont.Weight.Bold))
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 실제 웹캠 영상이 출력될 원형 위젯
        self.camera_view = CircularCameraWidget(180)
        
        self.sub_label = QLabel("정면을 바라봐주세요")
        self.sub_label.setFont(QFont("Malgun Gothic", 12))
        self.sub_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(self.title_label)
        layout.addWidget(self.camera_view, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.sub_label)
        
        self.setLayout(layout)
        
    def start_camera(self):
        # 백그라운드 스레드로 카메라 작동 시동
        self.camera_thread = CameraThread()
        self.camera_thread.frame_received.connect(self.camera_view.update_frame)
        self.camera_thread.start()
        
        # 3초 뒤에 카메라를 끄고 메인화면으로 넘어가도록 시뮬레이션 설정
        QTimer.singleShot(3000, self.stop_camera_and_proceed)

    def stop_camera_and_proceed(self):
        if self.camera_thread and self.camera_thread.isRunning():
            self.camera_thread.stop()
        self.controller.switch_to_screen(2)

# ----------------------------------------------------------------------
# 5. 메인 화면 (Page 2 - 대시보드 로그 기록)
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
        
        self.avatar = QLabel("👩")
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
        
        layout.addWidget(self.avatar, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.toggle_btn, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.log_display)
        
        self.setLayout(layout)

# ----------------------------------------------------------------------
# 6. 메인 윈도우 컨트롤러 (화면 흐름 제어)
# ----------------------------------------------------------------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Face Recognition System")
        self.setFixedSize(380, 620)
        
        self.central_stacked = QStackedWidget()
        self.setCentralWidget(self.central_stacked)
        
        self.login_screen = LoginScreen(self)
        self.face_auth_screen = FaceAuthScreen(self)
        self.main_screen = MainScreen(self)
        
        self.central_stacked.addWidget(self.login_screen)    # Index 0
        self.central_stacked.addWidget(self.face_auth_screen) # Index 1
        self.central_stacked.addWidget(self.main_screen)      # Index 2
        
        # 전역 스타일시트
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
            QLineEdit:focus { border: 1px solid #A6FF4D; }
            QPushButton#PrimaryBtn {
                background-color: #A6FF4D;
                border: none;
                border-radius: 20px;
                padding: 12px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton#PrimaryBtn:hover { background-color: #95E644; }
            QPushButton#SecondaryBtn {
                background-color: #FFFFFF;
                border: 1px solid #D0D0D0;
                border-radius: 8px;
                padding: 10px;
                font-size: 13px;
                color: #555555;
                }
            QPushButton#SecondaryBtn:hover { background-color: #EEEEEE; }
            """)

    def switch_to_screen(self, index):
        self.central_stacked.setCurrentIndex(index)
        # 얼굴 인식 스크린으로 진입할 때 카메라 가동 시작
        if index == 1:
            self.face_auth_screen.start_camera()

    def closeEvent(self, event):
        # 창이 닫힐 때 카메라 스레드가 켜져있다면 확실하게 종료 안전장치
        if hasattr(self.face_auth_screen, 'camera_thread') and self.face_auth_screen.camera_thread:
            self.face_auth_screen.camera_thread.stop()
            event.accept()

# ----------------------------------------------------------------------
# 프로그램 기동
# ----------------------------------------------------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())