import sys
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QApplication
from main_window import *


def main():
    app = QApplication(sys.argv)
    w = MainWindow()
    w.showMaximized()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
