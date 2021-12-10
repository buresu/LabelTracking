import os
from PySide6.QtCore import QDir
from PySide6.QtWidgets import QFrame, QVBoxLayout, QLineEdit, QListView, QHBoxLayout, QMenu, QFileSystemModel, QToolButton, QFileDialog
from PySide6.QtGui import QAction
from app import *
from label_list_model import *


class OutputView(QFrame):

    def __init__(self, parent=None):
        super(OutputView, self).__init__(parent)
        self.app = App()

        self.setWindowTitle('Outputs')

        self.output_dir_input = QLineEdit(self.app.output_dir)
        self.output_dir_input.setFocusPolicy(Qt.ClickFocus)
        self.output_dir_input.setReadOnly(True)

        self.select_folder_button = QToolButton()
        self.select_folder_button.setFocusPolicy(Qt.NoFocus)
        self.select_folder_button.setIcon(QIcon(os.path.join(
            os.path.dirname(__file__), 'icons/folder_black_24dp.svg')))
        self.select_folder_button.clicked.connect(self.select_folder)

        hvox = QHBoxLayout()
        hvox.addWidget(self.output_dir_input)
        hvox.addWidget(self.select_folder_button)

        self.model = QFileSystemModel()
        self.model.setReadOnly(True)
        self.model.setFilter(QDir.NoDotAndDotDot | QDir.Files)
        self.model.setRootPath(self.app.output_dir)
        self.model.setNameFilterDisables(False)
        self.model.setNameFilters(['*.jpg'])

        self.file_view = QListView()
        self.file_view.setLayoutMode(QListView.Batched)
        self.file_view.setModel(self.model)
        self.file_view.setRootIndex(self.model.index(self.app.output_dir))
        # self.label_view.setContextMenuPolicy(Qt.CustomContextMenu)
        # self.label_view.customContextMenuRequested.connect(
        #    self.show_context_menu)
        # self.label_view.selectionModel().selectionChanged.connect(self.label_changed)
        # self.label_view.setCurrentIndex(self.model.index(0))

        vbox = QVBoxLayout()
        vbox.addLayout(hvox)
        vbox.addWidget(self.file_view)

        self.setLayout(vbox)

    def select_folder(self):
        dir = QFileDialog.getExistingDirectory(
            self, "Select Output Directory", self.app.output_dir)
        if (dir != ''):
            self.app.output_dir = dir
            self.app.load()
            self.output_dir_input.setText(dir)
            self.model.setRootPath(dir)
            self.file_view.setRootIndex(self.model.index(dir))

    '''
    def label_changed(self, select):
        id = select.indexes()[0].data(Qt.DisplayRole)
        self.label_input.setText(id)
        self.app.current_label = self.app.get_label(id)

    def remove_label(self):
        index = self.label_view.currentIndex()
        if index.isValid():
            self.app.remove_label(index.data(Qt.DisplayRole))

    def change_label_id(self):
        index = self.label_view.currentIndex()
        if index.isValid():
            id, ret = QInputDialog.getText(
                self, 'Type New Label Name', self.app.labels[index.row()].id)
            if ret and id != '':
                self.app.labels[index.row()].id = id
                self.app.request_update()

    def change_label_color(self):
        index = self.label_view.currentIndex()
        if index.isValid():
            color = QColorDialog.getColor(Qt.red, self)
            if color.isValid():
                self.app.labels[index.row()].color = color
                self.app.request_update()

    def show_context_menu(self, p):
        index = self.label_view.indexAt(p)
        if index.isValid():
            menu = QMenu()

            change_id_action = QAction('Change Label Name', self)
            change_id_action.triggered.connect(self.change_label_id)
            menu.addAction(change_id_action)

            change_color_action = QAction('Change Label Color', self)
            change_color_action.triggered.connect(self.change_label_color)
            menu.addAction(change_color_action)

            remove_action = QAction('Remove', self)
            remove_action.triggered.connect(self.remove_label)
            menu.addAction(remove_action)

            menu.exec(self.label_view.mapToGlobal(p))
    '''
