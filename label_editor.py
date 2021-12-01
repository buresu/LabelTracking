from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget


class LabelEditor(QWidget):

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.setAutoFillBackground(True)
        self.setPalette(Qt.darkGray)
