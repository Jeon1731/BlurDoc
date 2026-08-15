# 얼굴 인식 화면
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

from CircularCameraWidget import CircularCameraWidget
from CameraThread import CameraThread

class FaceAuthForm(QWidget):
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
        self.title_label.setFont(QFont("Malgun Gothic", 12))
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.title_label)
        layout.addWidget(self.camera_view, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.sub_label)

        self.setLayout(layout)

    def start_camera(self):
        # 백그라운드 스레드로 카메라 작동 시동
        self.camera_thread = CameraThread()
        self.camera_thread.frame_received.connect(self.camera_view.update_frame)
        self.camera_thread.start()

        # (Temp) 3초 뒤 카메라를 끄고 메인 화면으로 이동
        QTimer.singleShot(3000, self.stop_camera_and_proceed)


    def stop_camera_and_proceed(self):
        if self.camera_thread and self.camera_thread.isRunning:
            self.camera_thread.stop()
        self.controller.switch_to_screen(2)