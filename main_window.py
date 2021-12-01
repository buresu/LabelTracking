from PySide6.QtCore import Qt, QFileInfo
from PySide6.QtWidgets import QMainWindow, QSizePolicy, QVBoxLayout, QFileDialog, QSlider
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
        help_menu = menu_bar.addMenu('&Help')

        open_action = QAction('&Open', self)
        open_action.setShortcut('Ctrl+O')
        open_action.setStatusTip('Open file')
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

        self.slider = QSlider(Qt.Horizontal)
        self.slider.sliderReleased.connect(self.update_video_position)

        box = QVBoxLayout()
        box.addWidget(self.editor)
        box.addWidget(self.slider)

        widget = QWidget()
        widget.setLayout(box)
        self.setCentralWidget(widget)

    def open_file(self):
        filename = QFileDialog.getOpenFileName(self, 'Open file')
        if len(filename) > 0:
            ext = QFileInfo(filename[0]).completeSuffix()

            image_exts = ['jpg', 'png']
            video_exts = ['mp4', 'm4v']

            if ext in image_exts:
                self.editor.open_image(filename[0])
            elif ext in video_exts:
                self.editor.open_video(filename[0])
                self.slider.setValue(0)
                self.slider.setMaximum(self.editor.get_frame_count() - 1)

    def update_video_position(self):
        self.editor.set_frame_position(self.slider.value())
