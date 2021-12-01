import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QLabel


def main():
    app = QApplication(sys.argv)
    label = QLabel("Hello World", alignment=Qt.AlignCenter)
    label.show()
    app.exec()


if __name__ == "__main__":
    main()
