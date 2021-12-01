from PySide6.QtWidgets import QMainWindow, QSizePolicy, QVBoxLayout
from label_editor import *


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.setup_ui()

    def setup_ui(self):

        self.setWindowTitle('LabelTrancking')

        size_policy = QSizePolicy()
        size_policy.setVerticalPolicy(QSizePolicy.Expanding)
        size_policy.setHorizontalPolicy(QSizePolicy.Expanding)

        editor = LabelEditor()
        editor.setSizePolicy(size_policy)

        box = QVBoxLayout()
        box.addWidget(editor)

        widget = QWidget()
        widget.setLayout(box)
        self.setCentralWidget(widget)
