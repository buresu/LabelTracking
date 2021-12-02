from PySide6.QtCore import Qt, QRectF


class Label(object):
    def __init__(self, id='label1', color=Qt.red, parent=None):
        self.id = id
        self.color = color


class LabelArea(object):
    def __init__(self, parent=None):
        self.id = ""
        self.select = False
        self.rect = QRectF()
