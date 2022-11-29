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
        elif role == Qt.CheckStateRole:
            if self.app.label_areas[index.row()].enabled:
                return Qt.Checked
            else:
                return Qt.Unchecked
        elif role == Qt.DecorationRole:
            id = self.app.label_areas[index.row()].id
            label = self.app.get_label(id)
            if label != None:
                return self.create_color_icon(label.color)
            else:
                return self.create_color_icon(Qt.white)

        else:
            return None

    def setData(self, index, value, role=Qt.EditRole):

        if not index.isValid():
            return None

        if not 0 <= index.row() < len(self.app.label_areas):
            return None

        if role == Qt.CheckStateRole:
            if value == Qt.Checked.value:
                self.app.label_areas[index.row()].enabled = True
            else:
                self.app.label_areas[index.row()].enabled = False
            self.app.request_update()
            return True
        
        return False

    def flags(self, index):
        return super(LabelAreaListModel, self).flags(index) | Qt.ItemIsUserCheckable

    def create_color_icon(self, color):
        pixmap = QPixmap(64, 64)
        pixmap.fill(color)
        return QIcon(pixmap)
