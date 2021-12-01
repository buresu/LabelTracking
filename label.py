from PySide6.QtCore import Qt, QRectF


class Label():
    def __init__(self, parent=None):
        self.id = "label1"
        self.color = Qt.red

class LabelArea():
    def __init__(self, parent=None):
        self.id = ""
        self.rect = QRectF()