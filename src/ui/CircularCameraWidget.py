# 커스텀 원형 프로필 및 카메라 뷰 위젯
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QLabel

class CircularCameraWidget(QLabel):
    def __init__(self, size=180, parent=None):
        super().__init__(parent)
        self.setFixedSize(size, size)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # StyleSheet
        self.setStyleSheet(f"""
            background-color: #E8F5E9;
            border: 4px solid #A6FF4D;
            border-radius: {size // 2}px;
        """)

    @Slot(QImage)
    def update_frame(self, qt_image):
        scaled_pixmap = QPixmap.fromImage(qt_image).scaled(
            self.width(), self.height(),
            Qt.AspectRatioMode.KeepAspectRatioByExpanding,
            Qt.TransformationMode.SmoothTransformation
        )
        self.setPixmap(scaled_pixmap)