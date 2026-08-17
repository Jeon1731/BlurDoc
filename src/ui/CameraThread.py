# OpenCV 카메라 백그라운드 스레드
import cv2
from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QImage

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

            # BGR2RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w

            # QImage로 변환
            qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)

            # 정방형 크기 조정 유도 (GUI 처리)
            self.frame_received.emit(qt_image)

            self.msleep(33) # 약 30fps

        if self.cap:
            self.cap.release()

    def stop(self):
        self.running = False
        self.wait()