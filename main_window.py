import os
from PySide6.QtCore import Qt, QSize, QDir, QEvent
from PySide6.QtWidgets import QMainWindow, QSizePolicy, QVBoxLayout, QHBoxLayout, QFileDialog, QSlider, QPushButton, QToolBar, QDockWidget, QCheckBox, QMessageBox
from PySide6.QtGui import QAction, QIcon
from app import *
from label_editor import *
from label_view import *
from label_area_view import *
from output_view import *
from export import *


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.app = App()
        self.setMouseTracking(True)
        self.installEventFilter(self)
        self.setup_ui()

    def setup_ui(self):

        self.setWindowTitle('LabelTrancking')

        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu('&File')
        help_menu = menu_bar.addMenu('&Help')

        open_action = QAction('&Open', self)
        open_action.setShortcut('Ctrl+O')
        open_action.setStatusTip('Open file')
        open_action.setIcon(QIcon(os.path.join(os.path.dirname(
            __file__), 'icons/file_open_black_24dp.svg')))
        open_action.triggered.connect(self.open_file)

        file_menu.addAction(open_action)

        save_action = QAction('Save', self)
        save_action.setShortcut('Ctrl+S')
        save_action.setIcon(
            QIcon(os.path.join(os.path.dirname(__file__), 'icons/save_black_24dp.svg')))
        save_action.triggered.connect(self.app.save)

        file_menu.addAction(save_action)

        export_action = QAction('Export', self)
        export_action.setIcon(
            QIcon(os.path.join(os.path.dirname(__file__), 'icons/ios_share_black_24dp.svg')))
        export_action.triggered.connect(self.export)

        file_menu.addAction(export_action)

        quit_action = QAction('&Quit', self)
        quit_action.setShortcut('Ctrl+Q')
        quit_action.setIcon(QIcon(os.path.join(os.path.dirname(
            __file__), 'icons/exit_to_app_black_24dp.svg')))
        quit_action.setStatusTip('Quit application')
        quit_action.triggered.connect(self.close)

        file_menu.addAction(quit_action)

        about_qt_action = QAction('About Qt', self)
        about_qt_action.triggered.connect(self.show_about_qt)

        help_menu.addAction(about_qt_action)

        tool_bar = QToolBar()
        tool_bar.setOrientation(Qt.Vertical)
        tool_bar.setIconSize(QSize(40, 40))

        self.draw_mode_action = QAction('Draw', self)
        self.draw_mode_action.setShortcut('D')
        self.draw_mode_action.setIcon(QIcon(os.path.join(
            os.path.dirname(__file__), 'icons/mode_edit_black_24dp.svg')))
        self.draw_mode_action.setCheckable(True)
        self.draw_mode_action.triggered.connect(self.change_draw_mode)

        self.edit_mode_action = QAction('Edit', self)
        self.edit_mode_action.setShortcut('E')
        self.edit_mode_action.setIcon(QIcon(os.path.join(
            os.path.dirname(__file__), 'icons/format_shapes_black_24dp.svg')))
        self.edit_mode_action.setCheckable(True)
        self.edit_mode_action.triggered.connect(self.change_edit_mode)

        tool_bar.addAction(open_action)
        tool_bar.addAction(save_action)
        tool_bar.addAction(export_action)
        tool_bar.addAction(self.draw_mode_action)
        tool_bar.addAction(self.edit_mode_action)

        self.addToolBar(Qt.LeftToolBarArea, tool_bar)

        size_policy = QSizePolicy()
        size_policy.setVerticalPolicy(QSizePolicy.Expanding)
        size_policy.setHorizontalPolicy(QSizePolicy.Expanding)

        self.editor = LabelEditor()
        self.editor.setFocusPolicy(Qt.StrongFocus)
        self.editor.setSizePolicy(size_policy)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setEnabled(False)
        self.slider.setFocusPolicy(Qt.NoFocus)
        self.slider.sliderReleased.connect(self.slider_changed)

        self.back_button = QPushButton()
        self.back_button.setEnabled(False)
        self.back_button.setFocusPolicy(Qt.NoFocus)
        self.back_button.setIcon(QIcon(os.path.join(os.path.dirname(
            __file__), 'icons/arrow_back_ios_new_black_24dp.svg')))
        self.back_button.pressed.connect(self.back_button_pressed)

        self.next_button = QPushButton()
        self.next_button.setEnabled(False)
        self.next_button.setFocusPolicy(Qt.NoFocus)
        self.next_button.setIcon(QIcon(os.path.join(os.path.dirname(
            __file__), 'icons/arrow_forward_ios_black_24dp.svg')))
        self.next_button.pressed.connect(self.next_button_pressed)

        self.auto_tracking = QCheckBox('Auto Tracking')
        self.auto_tracking.setFocusPolicy(Qt.NoFocus)
        self.auto_tracking.setCheckState(Qt.Unchecked)
        self.auto_tracking.stateChanged.connect(self.set_auto_tracking)

        hbox = QHBoxLayout()
        hbox.addWidget(self.slider)
        hbox.addWidget(self.back_button)
        hbox.addWidget(self.next_button)
        hbox.addWidget(self.auto_tracking)

        vbox = QVBoxLayout()
        vbox.addWidget(self.editor)
        vbox.addLayout(hbox)

        widget = QWidget()
        widget.setLayout(vbox)
        self.setCentralWidget(widget)

        self.label_view_dock = QDockWidget('Select Label', self)
        self.label_view_dock.setWidget(LabelView())
        self.addDockWidget(Qt.RightDockWidgetArea, self.label_view_dock)

        self.label_area_view_dock = QDockWidget('Label Areas', self)
        self.label_area_view_dock.setWidget(LabelAreaView())
        self.addDockWidget(Qt.RightDockWidgetArea, self.label_area_view_dock)

        self.output_view_dock = QDockWidget('Output', self)
        self.output_view_dock.setWidget(OutputView())
        self.addDockWidget(Qt.RightDockWidgetArea, self.output_view_dock)

        self.change_draw_mode()
        self.update_video_ui()

    def eventFilter(self, obj, e):
        if e.type() == QEvent.KeyPress:
            if e.key() == Qt.Key_Right and not e.isAutoRepeat():
                self.app.next_frame_position()
                self.slider.setValue(self.app.get_frame_position())
            elif e.key() == Qt.Key_Left and not e.isAutoRepeat():
                self.app.back_frame_position()
                self.slider.setValue(self.app.get_frame_position())
            return True
        return False

    def open_file(self):
        filename = QFileDialog.getOpenFileName(self, 'Open file')
        if len(filename) > 0:
            self.app.open_file(filename[0])
            self.app.set_frame_position(0)
            self.update_video_ui()

    def slider_changed(self):
        self.app.set_frame_position(self.slider.value())

    def back_button_pressed(self):
        self.app.back_frame_position()
        self.slider.setValue(self.app.get_frame_position())

    def next_button_pressed(self):
        self.app.next_frame_position()
        self.slider.setValue(self.app.get_frame_position())

    def change_draw_mode(self):
        self.editor.set_mode(LabelEditor.MODE_DRAW)
        self.draw_mode_action.setChecked(True)
        self.edit_mode_action.setChecked(False)

    def change_edit_mode(self):
        self.editor.set_mode(LabelEditor.MODE_EDIT)
        self.draw_mode_action.setChecked(False)
        self.edit_mode_action.setChecked(True)

    def set_auto_tracking(self):
        if self.auto_tracking.checkState() == Qt.Checked:
            self.app.start_tracking()
        else:
            self.app.stop_tracking()

    def update_video_ui(self):
        if self.app.is_sequential():
            self.back_button.setEnabled(True)
            self.next_button.setEnabled(True)
            self.slider.setEnabled(True)
            self.slider.setMaximum(self.app.get_frame_count() - 1)
            self.slider.setValue(self.app.frame_position)
        else:
            self.back_button.setEnabled(False)
            self.next_button.setEnabled(False)
            self.slider.setEnabled(False)
            self.slider.setValue(0)

    def export(self):
        dirname = QFileDialog.getExistingDirectory(
            self, 'Select Directory', QDir.homePath())
        if len(dirname) > 0:
            exporter = Exporter()
            exporter.export_to_labelme(dirname)

    def show_about_qt(self):
        QMessageBox.aboutQt(self, "About PySide")
