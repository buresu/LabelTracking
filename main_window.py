from PySide6.QtWidgets import QMainWindow, QSizePolicy, QVBoxLayout, QFileDialog
from PySide6.QtGui import QAction
from label_editor import *


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.setup_ui()

    def setup_ui(self):

        self.setWindowTitle('LabelTrancking')

        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu('&File')

        open_action = QAction('&Open', self)
        open_action.setShortcut('Ctrl+O')
        open_action.setStatusTip('Open image')
        open_action.triggered.connect(self.open_file)

        file_menu.addAction(open_action)

        quit_action = QAction('&Quit', self)
        quit_action.setShortcut('Ctrl+Q')
        quit_action.setStatusTip('Quit application')
        quit_action.triggered.connect(self.close)

        file_menu.addAction(quit_action)

        size_policy = QSizePolicy()
        size_policy.setVerticalPolicy(QSizePolicy.Expanding)
        size_policy.setHorizontalPolicy(QSizePolicy.Expanding)

        self.editor = LabelEditor()
        self.editor.setSizePolicy(size_policy)

        box = QVBoxLayout()
        box.addWidget(self.editor)

        widget = QWidget()
        widget.setLayout(box)
        self.setCentralWidget(widget)

    def open_file(self):
        filename = QFileDialog.getOpenFileName(self, 'Open Image')
        if len(filename) > 0:
            self.editor.open_image(filename[0])
