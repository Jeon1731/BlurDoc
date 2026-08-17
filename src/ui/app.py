import sys
from PySide6.QtWidgets import QApplication
from MainWindowController import MainWindowContoller

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindowContoller()
    window.show()
    sys.exit(app.exec())