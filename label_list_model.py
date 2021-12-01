from PySide6.QtCore import Qt, QAbstractListModel, QModelIndex
from PySide6.QtGui import QPixmap, QIcon
from app import *


class LabelListModel(QAbstractListModel):

    def __init__(self, parent=None):
        super(LabelListModel, self).__init__(parent)
        self.app = App()

    def rowCount(self, parent=QModelIndex()):
        return len(self.app.labels)

    def data(self, index, role=Qt.DisplayRole):

        if not index.isValid():
            return None

        if not 0 <= index.row() < len(self.app.labels):
            return None

        if role == Qt.DisplayRole:
            return self.app.labels[index.row()].id
        elif role == Qt.DecorationRole:
            return self.create_color_icon(self.app.labels[index.row()].color)

        else:
            return None

    def create_color_icon(self, color):
        pixmap = QPixmap(64, 64)
        pixmap.fill(color)
        return QIcon(pixmap)
