from PySide6.QtWidgets import QFrame, QVBoxLayout, QLineEdit, QListView, QHBoxLayout, QPushButton, QMenu, QColorDialog
from PySide6.QtGui import QAction
from app import *
from label_list_model import *


class LabelView(QFrame):

    def __init__(self, parent=None):
        super(LabelView, self).__init__(parent)
        self.app = App()

        self.setWindowTitle('Select Label')

        self.label_input = QLineEdit('Label1')
        self.label_input.setFocusPolicy(Qt.ClickFocus)
        self.label_input.editingFinished.connect(self.add_label)

        self.label_add_button = QPushButton()
        self.label_add_button.setFocusPolicy(Qt.ClickFocus)
        self.label_add_button.setIcon(QIcon.fromTheme("document-new"))
        self.label_add_button.clicked.connect(self.add_label)

        hvox = QHBoxLayout()
        hvox.addWidget(self.label_input)
        hvox.addWidget(self.label_add_button)

        self.model = LabelListModel()

        self.label_view = QListView()
        self.label_view.setModel(self.model)
        self.label_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.label_view.customContextMenuRequested.connect(
            self.show_context_menu)
        self.label_view.selectionModel().selectionChanged.connect(self.label_changed)
        self.label_view.setCurrentIndex(self.model.index(0))

        vbox = QVBoxLayout()
        vbox.addLayout(hvox)
        vbox.addWidget(self.label_view)

        self.setLayout(vbox)

    def label_changed(self, select):
        id = select.indexes()[0].data(Qt.DisplayRole)
        self.label_input.setText(id)
        self.app.current_label = self.app.get_label(id)

    def add_label(self):
        self.app.add_label(self.label_input.text())

    def remove_label(self):
        index = self.label_view.currentIndex()
        if index.isValid():
            self.app.remove_label(index.data(Qt.DisplayRole))

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

            change_color_action = QAction('Change Label Color', self)
            change_color_action.triggered.connect(self.change_label_color)
            menu.addAction(change_color_action)

            remove_action = QAction('Remove', self)
            remove_action.triggered.connect(self.remove_label)
            menu.addAction(remove_action)

            menu.exec(self.label_view.mapToGlobal(p))
