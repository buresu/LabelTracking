from PySide6.QtWidgets import QFrame, QVBoxLayout, QListView, QMenu
from PySide6.QtGui import QAction
from app import *
from label_area_list_model import *


class LabelAreaView(QFrame):

    def __init__(self, parent=None):
        super(LabelAreaView, self).__init__(parent)
        self.app = App()

        self.setWindowTitle('Label Areas')

        self.model = LabelAreaListModel()

        self.label_area_view = QListView()
        self.label_area_view.setModel(self.model)
        self.label_area_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.label_area_view.customContextMenuRequested.connect(
            self.show_context_menu)
        self.label_area_view.selectionModel().selectionChanged.connect(self.label_area_changed)
        self.label_area_view.setCurrentIndex(self.model.index(0))

        vbox = QVBoxLayout()
        vbox.addWidget(self.label_area_view)

        self.setLayout(vbox)

    def label_area_changed(self, select):
        pass
        #self.label_input.setText(select.indexes()[0].data(Qt.DisplayRole))

    def remove_label_area(self):
        pass
        #index = self.label_view.currentIndex()
        #if index.isValid():
        #    self.app.remove_label(index.data(Qt.DisplayRole))
        #    self.model.update()

    def show_context_menu(self, p):
        index = self.label_area_view.indexAt(p)
        if index.isValid():
            menu = QMenu()

            remove_action = QAction('Remove', self)
            remove_action.triggered.connect(self.remove_label_area)
            menu.addAction(remove_action)

            menu.exec(self.label_view.mapToGlobal(p))
