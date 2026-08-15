import sys
import cv2
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout,
    QHBoxLayout, QStackedWidget, QFormLayout, QFrame, QSizePolicy, QTextEdit
)
from PySide6.QtCore import Qt, QTimer, Signal, Slot
from PySide6.QtGui import QFont, QImage, QPixmap, QColor, QPainter, QBrush

# --- 간단한 원형 아바타 (카메라 미리보기가 없을 때 사용) ---
class AvatarLabel(QLabel):
    def __init__(self, diameter=140, text="🙂", parent=None):
        super().__init__(parent)
        self.diameter = diameter
        self.text = text
        self.setFixedSize(diameter, diameter)
        self.setAlignment(Qt.AlignCenter)
        self.setFont(QFont("Arial", int(diameter/3)))
        self._bg_color = QColor(200, 245, 210)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = self.rect()
        painter.setBrush(QBrush(self._bg_color))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(rect)
        painter.setPen(Qt.black)
        painter.setFont(self.font())
        painter.drawText(rect, Qt.AlignCenter, self.text)

# --- OpenCV 카메라 캡처 래퍼 ---
class CameraCapture:
    def __init__(self, device_index=0, width=320, height=240):
        self.device_index = device_index
        self.width = width
        self.height = height
        self.cap = None

    def start(self):
        if self.cap is None:
            self.cap = cv2.VideoCapture(self.device_index, cv2.CAP_DSHOW)
            if not self.cap.isOpened():
                self.cap = None
                raise RuntimeError("카메라를 열 수 없습니다.")
            # 원하는 해상도 설정 (성공하지 않을 수도 있음)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)

    def read(self):
        if self.cap is None:
            return False, None
        ret, frame = self.cap.read()
        return ret, frame

    def stop(self):
        if self.cap is not None:
            try:
                self.cap.release()
            except Exception:
                pass
            self.cap = None

# --- Login 화면 ---
class LoginWidget(QWidget):
    request_register = Signal()
    request_face_scan = Signal(str)

    def __init__(self):
        super().__init__()
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        avatar = AvatarLabel(140, "🙂")
        layout.addWidget(avatar, alignment=Qt.AlignCenter)

        form = QFormLayout()
        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("아이디를 입력해주세요.")
        self.pw_input = QLineEdit()
        self.pw_input.setEchoMode(QLineEdit.Password)
        self.pw_input.setPlaceholderText("비밀번호를 입력해주세요.")
        form.addRow("아이디", self.id_input)
        form.addRow("비밀번호", self.pw_input)
        layout.addLayout(form)

        btn_layout = QHBoxLayout()
        login_btn = QPushButton("로그인")
        register_btn = QPushButton("유저 등록")
        btn_layout.addWidget(login_btn)
        btn_layout.addWidget(register_btn)
        layout.addLayout(btn_layout)

        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        self.setLayout(layout)

        login_btn.clicked.connect(self._on_login)
        register_btn.clicked.connect(lambda: self.request_register.emit())

    @Slot()
    def _on_login(self):
        user_id = self.id_input.text().strip()
        if not user_id:
            self.status_label.setText("아이디를 입력해주세요.")
            return
        self.status_label.setText("얼굴을 인식중입니다...")
        self.request_face_scan.emit(user_id)

# --- FaceAuth 화면 (OpenCV 미리보기 포함) ---
class FaceAuthWidget(QWidget):
    face_registered = Signal(str)
    face_recognized = Signal(str)

    def __init__(self, camera: CameraCapture, mode="scan"):
        super().__init__()
        self.camera = camera
        self.mode = mode
        self._timer = QTimer(self)
        self._timer.setInterval(30)  # 약 30 FPS 목표
        self._timer.timeout.connect(self._update_frame)

        self._progress_timer = QTimer(self)
        self._progress_timer.setInterval(1200)
        self._progress_timer.timeout.connect(self._simulate_progress)
        self._progress_step = 0

        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        # 비디오 표시용 QLabel
        self.video_label = QLabel()
        self.video_label.setFixedSize(320, 240)
        self.video_label.setStyleSheet("background-color: #e0e0e0; border-radius: 8px;")
        self.video_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.video_label, alignment=Qt.AlignCenter)

        self.title_label = QLabel("")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(self.title_label)

        self.hint_label = QLabel("정면을 바라봐주세요")
        self.hint_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.hint_label)

        # 등록 폼
        self.form_frame = QFrame()
        form_layout = QFormLayout()
        self.reg_id = QLineEdit()
        self.reg_id.setPlaceholderText("아이디를 입력해주세요.")
        self.reg_pw = QLineEdit()
        self.reg_pw.setEchoMode(QLineEdit.Password)
        self.reg_pw.setPlaceholderText("비밀번호를 입력해주세요.")
        self.reg_pw_confirm = QLineEdit()
        self.reg_pw_confirm.setEchoMode(QLineEdit.Password)
        self.reg_pw_confirm.setPlaceholderText("비밀번호를 입력해주세요.")
        form_layout.addRow("아이디", self.reg_id)
        form_layout.addRow("비밀번호", self.reg_pw)
        form_layout.addRow("비밀번호 확인", self.reg_pw_confirm)
        self.form_frame.setLayout(form_layout)

        btn_layout = QHBoxLayout()
        self.register_face_btn = QPushButton("얼굴 등록 및 인식동의")
        self.register_user_btn = QPushButton("유저 등록")
        btn_layout.addWidget(self.register_face_btn)
        btn_layout.addWidget(self.register_user_btn)

        layout.addWidget(self.form_frame)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

        # 연결
        self.register_face_btn.clicked.connect(self._start_register_process)
        self.register_user_btn.clicked.connect(self._on_user_register)

        self.set_mode(self.mode)

    def set_mode(self, mode):
        self.mode = mode
        if mode == "register":
            self.form_frame.show()
            self.title_label.setText("얼굴을 등록합니다")
        else:
            self.form_frame.hide()
            self.title_label.setText("얼굴을 인식중입니다...")

    @Slot()
    def _on_user_register(self):
        uid = self.reg_id.text().strip()
        pw = self.reg_pw.text()
        pwc = self.reg_pw_confirm.text()
        if not uid:
            self.title_label.setText("아이디를 입력해주세요.")
            return
        if not pw or pw != pwc:
            self.title_label.setText("비밀번호가 일치하지 않습니다.")
            return
        self.title_label.setText("얼굴 등록 준비중...")
        self._start_register_process()

    def _start_camera(self):
        try:
            self.camera.start()
        except RuntimeError as e:
            self.title_label.setText(str(e))
            return
        self._timer.start()

    def _stop_camera(self):
        self._timer.stop()
        self.camera.stop()
        # 비디오 라벨을 기본 상태로 되돌림
        self.video_label.clear()
        self.video_label.setText("카메라 정지")

    @Slot()
    def _update_frame(self):
        ret, frame = self.camera.read()
        if not ret or frame is None:
            return
        # BGR -> RGB
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pix = QPixmap.fromImage(qt_image).scaled(
            self.video_label.width(), self.video_label.height(), Qt.KeepAspectRatio
        )
        self.video_label.setPixmap(pix)

    @Slot()
    def _start_register_process(self):
        # 카메라 시작 및 진행 시뮬레이션
        self._progress_step = 0
        self.title_label.setText("얼굴을 등록중입니다...")
        self.hint_label.setText("정면을 바라봐주세요")
        self._start_camera()
        self._progress_timer.start()

    @Slot()
    def _simulate_progress(self):
        self._progress_step += 1
        if self._progress_step == 1:
            self.hint_label.setText("정면을 바라봐주세요")
        elif self._progress_step == 2:
            self.hint_label.setText("조금만 더 유지해주세요")
        else:
            self._progress_timer.stop()
            # 완료 처리
            if self.mode == "register":
                self.title_label.setText("얼굴 등록 완료!")
                uid = self.reg_id.text().strip() or "new_user"
                self.face_registered.emit(uid)
            else:
                self.title_label.setText("얼굴 인식 완료!")
                uid = "recognized_user"
                self.face_recognized.emit(uid)
            # 카메라 정지
            self._stop_camera()

# --- Main 화면 ---
class MainWidget(QWidget):
    def __init__(self):
        super().__init__()
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)

        top_label = QLabel("메인 화면")
        top_label.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(top_label, alignment=Qt.AlignCenter)

        left = QFrame()
        left_layout = QVBoxLayout()
        left_layout.setAlignment(Qt.AlignCenter)
        self.play_avatar = AvatarLabel(120, "▶")
        left_layout.addWidget(self.play_avatar)
        self.play_btn = QPushButton("Play")
        left_layout.addWidget(self.play_btn)
        left.setLayout(left_layout)

        right = QFrame()
        right_layout = QVBoxLayout()
        right_layout.setAlignment(Qt.AlignTop)
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFixedHeight(140)
        right_layout.addWidget(QLabel("이력"))
        right_layout.addWidget(self.log_text)
        right.setLayout(right_layout)

        h = QHBoxLayout()
        h.addWidget(left)
        h.addWidget(right)
        layout.addLayout(h)

        self.setLayout(layout)

        self.log_text.append("21:38 | Laptop Locked")
        self.log_text.append("21:39 | Laptop UnLocked")

# --- 메인 윈도우 ---
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FaceAuth OpenCV Demo")
        self.resize(800, 600)
        self.camera = CameraCapture(device_index=0, width=640, height=480)
        self._build_ui()

    def _build_ui(self):
        main_layout = QVBoxLayout()
        self.stack = QStackedWidget()

        self.login = LoginWidget()
        self.face_scan = FaceAuthWidget(camera=self.camera, mode="scan")
        self.face_register = FaceAuthWidget(camera=self.camera, mode="register")
        self.main_screen = MainWidget()

        self.stack.addWidget(self.login)
        self.stack.addWidget(self.face_scan)
        self.stack.addWidget(self.face_register)
        self.stack.addWidget(self.main_screen)

        main_layout.addWidget(self.stack)
        self.setLayout(main_layout)

        # 시그널 연결
        self.login.request_register.connect(self._go_register)
        self.login.request_face_scan.connect(self._go_face_scan)
        self.face_register.face_registered.connect(self._on_registered)
        self.face_scan.face_recognized.connect(self._on_recognized)

    @Slot()
    def _go_register(self):
        self.face_register.set_mode("register")
        self.stack.setCurrentWidget(self.face_register)

    @Slot(str)
    def _go_face_scan(self, user_id):
        self.face_scan.set_mode("scan")
        self.stack.setCurrentWidget(self.face_scan)

    @Slot(str)
    def _on_registered(self, user_id):
        self.main_screen.log_text.append(f"{user_id} 등록 완료")
        self.stack.setCurrentWidget(self.main_screen)

    @Slot(str)
    def _on_recognized(self, user_id):
        self.main_screen.log_text.append(f"{user_id} 얼굴 인식 성공")
        self.stack.setCurrentWidget(self.main_screen)

    def closeEvent(self, event):
        # 창 닫을 때 카메라 정리
        try:
            self.camera.stop()
        except Exception:
            pass
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
