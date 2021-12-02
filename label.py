from PySide6.QtCore import Qt, QRectF, QPointF


class Label(object):
    def __init__(self, id='label1', color=Qt.red, parent=None):
        self.id = id
        self.color = color


class LabelArea(object):
    def __init__(self, parent=None):
        self.id = ""
        self.enabled = True
        self.select = False
        self.rect = QRectF()
        self.key_points = [QPointF(), QPointF()]
        self.key_points_selection = [False, False]

    def update(self):
        self.rect.setTopLeft(self.key_points[0])
        self.rect.setBottomRight(self.key_points[1])
