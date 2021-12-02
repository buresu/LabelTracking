from PySide6.QtCore import Qt, QFileInfo, QSize
from PySide6.QtWidgets import QMainWindow, QSizePolicy, QVBoxLayout, QHBoxLayout, QFileDialog, QSlider, QPushButton, QToolBar
from PySide6.QtGui import QAction, QIcon
from label_editor import *
from app import *


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.app = App()
        self.setup_ui()

    def setup_ui(self):

        self.setWindowTitle('LabelTrancking')

        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu('&File')
        help_menu = menu_bar.addMenu('&Help')

        open_action = QAction('&Open', self)
        open_action.setShortcut('Ctrl+O')
        open_action.setStatusTip('Open file')
        open_action.setIcon(QIcon.fromTheme('document-open'))
        open_action.triggered.connect(self.open_file)

        file_menu.addAction(open_action)

        quit_action = QAction('&Quit', self)
        quit_action.setShortcut('Ctrl+Q')
        quit_action.setStatusTip('Quit application')
        quit_action.setIcon(QIcon.fromTheme('application-exit'))
        quit_action.triggered.connect(self.close)

        file_menu.addAction(quit_action)

        tool_bar = QToolBar()
        tool_bar.setOrientation(Qt.Vertical)
        tool_bar.setIconSize(QSize(50, 50))

        tool_bar.addAction(open_action)

        self.addToolBar(Qt.LeftToolBarArea, tool_bar)

        size_policy = QSizePolicy()
        size_policy.setVerticalPolicy(QSizePolicy.Expanding)
        size_policy.setHorizontalPolicy(QSizePolicy.Expanding)

        self.editor = LabelEditor()
        self.editor.setSizePolicy(size_policy)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setEnabled(False)
        self.slider.sliderReleased.connect(self.slider_changed)

        self.back_button = QPushButton()
        self.back_button.setEnabled(False)
        self.back_button.setIcon(QIcon.fromTheme("go-previous"))
        self.back_button.pressed.connect(self.back_button_pressed)

        self.next_button = QPushButton()
        self.next_button.setEnabled(False)
        self.next_button.setIcon(QIcon.fromTheme("go-next"))
        self.next_button.pressed.connect(self.next_button_pressed)

        hbox = QHBoxLayout()
        hbox.addWidget(self.slider)
        hbox.addWidget(self.back_button)
        hbox.addWidget(self.next_button)

        vbox = QVBoxLayout()
        vbox.addWidget(self.editor)
        vbox.addLayout(hbox)

        widget = QWidget()
        widget.setLayout(vbox)
        self.setCentralWidget(widget)

    def open_file(self):
        filename = QFileDialog.getOpenFileName(self, 'Open file')
        if len(filename) > 0:
            ext = QFileInfo(filename[0]).completeSuffix()

            image_exts = ['jpg', 'png']
            video_exts = ['mp4', 'm4v']

            if ext in image_exts:
                self.app.open_image(filename[0])
                self.back_button.setEnabled(False)
                self.next_button.setEnabled(False)
                self.slider.setEnabled(False)
                self.slider.setValue(0)
                self.editor.update_view_transform()
                self.editor.update()

            elif ext in video_exts:
                self.app.open_video(filename[0])
                self.back_button.setEnabled(True)
                self.next_button.setEnabled(True)
                self.slider.setEnabled(True)
                self.slider.setValue(0)
                self.slider.setMaximum(self.app.get_frame_count() - 1)
                self.editor.update_view_transform()
                self.editor.update()

    def slider_changed(self):
        self.app.set_frame_position(self.slider.value())
        self.editor.update()

    def back_button_pressed(self):
        self.app.back_frame_position()
        self.slider.setValue(self.app.get_frame_position())
        self.editor.update()

    def next_button_pressed(self):
        self.app.next_frame_position()
        self.slider.setValue(self.app.get_frame_position())
        self.editor.update()
