import sys
from PySide6.QtWidgets import QApplication
from main_window import *


def main():
    app = QApplication(sys.argv)
    app.setApplicationName('LabelTracking')
    w = MainWindow()
    w.showMaximized()
    app.exec()


if __name__ == "__main__":
    main()
