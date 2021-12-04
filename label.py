from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import QColor


class Label(object):
    def __init__(self, id='label1', color=Qt.red, parent=None):
        self.id = id
        self.color = QColor(color)

    def __repr__(self):
        return 'Label(id=%s,color=%s)' % (self.id, self.color.name())

    def serialize(self):
        obj = dict()
        obj['id'] = self.id
        obj['color'] = self.color.name()
        return obj

    def deserialize(self, obj):
        self.id = obj['id']
        self.color = QColor(obj['color'])


class LabelArea(object):
    def __init__(self, parent=None):
        self.id = ""
        self.enabled = True
        self.select = False
        self.rect = QRectF()
        self.key_points = [QPointF(), QPointF()]
        self.key_points_selection = [False, False]

    def serialize(self):
        obj = dict()
        obj['id'] = self.id
        obj['enabled'] = self.enabled
        obj['points'] = [[self.key_points[0].x(), self.key_points[0].y()], [
            self.key_points[1].x(), self.key_points[1].y()]]
        return obj

    def deserialize(self, obj):
        self.id = obj['id']
        self.enabled = obj['enabled']
        self.points = [QPointF(obj['points'][0][0], obj['points'][0][1]), QPointF(
            obj['points'][1][0], obj['points'][1][1])]
        self.update()

    def update(self):
        self.rect.setTopLeft(self.key_points[0])
        self.rect.setBottomRight(self.key_points[1])
