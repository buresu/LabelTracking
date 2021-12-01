from PySide6.QtCore import Qt, QAbstractListModel
from app import *


class LabelListModel(QAbstractListModel):

    def __init__(self, parent=None):
        super(LabelListModel, self).__init__(parent)
        self.app = App()

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self.app.labels)

    def data(self, index, role=Qt.DisplayRole):

        if not index.isValid():
            return None

        if not 0 <= index.row() < len(self.app.labels):
            return None

        if role == Qt.DisplayRole:
            return self.self.app.labels[index.row()].id

        else:
            return None
