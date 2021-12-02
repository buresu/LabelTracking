from PySide6.QtCore import Qt, QAbstractListModel, QModelIndex
from PySide6.QtGui import QPixmap, QIcon
from app import *


class LabelAreaListModel(QAbstractListModel):

    def __init__(self, parent=None):
        super(LabelAreaListModel, self).__init__(parent)
        self.app = App()
        self.app.update.connect(self.layoutChanged)

    def rowCount(self, parent=QModelIndex()):
        return len(self.app.label_areas)

    def data(self, index, role=Qt.DisplayRole):

        if not index.isValid():
            return None

        if not 0 <= index.row() < len(self.app.label_areas):
            return None

        if role == Qt.DisplayRole:
            return self.app.label_areas[index.row()].id
        elif role == Qt.DecorationRole:
            id = self.app.label_areas[index.row()].id
            return self.create_color_icon(self.app.get_label(id).color)

        else:
            return None

    def create_color_icon(self, color):
        pixmap = QPixmap(64, 64)
        pixmap.fill(color)
        return QIcon(pixmap)
