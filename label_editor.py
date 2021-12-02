from PySide6.QtCore import Qt, QRect, QUrl, QRectF, QPointF, QSizeF
from PySide6.QtWidgets import QWidget, QMenu
from PySide6.QtGui import QImage, QPainter, QAction, QCursor, QTransform
import cv2 as cv
from app import *
from label_select_dialog import *


class LabelEditor(QWidget):

    MODE_INVALID = 0
    MODE_DRAW_LABEL = 1
    MODE_DRAW_LABEL_MOVE = 2
    MODE_EDIT_LABEL = 3

    def __init__(self, parent=None):
        super(LabelEditor, self).__init__(parent)
        self.app = App()

        self.setAutoFillBackground(True)
        self.setPalette(Qt.darkGray)

        self.setFocusPolicy(Qt.ClickFocus)

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.context_menu)

        self.menu = QMenu(self)

        create_rectagle_action = QAction('Create Rectagle', self)
        create_rectagle_action.setShortcut('Ctrl+R')
        create_rectagle_action.triggered.connect(self.create_rectagle)

        self.menu.addAction(create_rectagle_action)

        self.mode = self.MODE_DRAW_LABEL
        self.view_zoom = 1.0
        self.view_press_start_pos = QPointF()
        self.view_translate_pos = QPointF()
        self.view_translate_start_pos = QPointF()
        self.view_transform = QTransform()

    def context_menu(self, point):
        self.menu.exec_(self.mapToGlobal(point))

    def paintEvent(self, e):
        p = QPainter(self)
        '''
        if self.app.frame is not None:
            rw, rh = (self.width(), self.height())
            fh, fw = self.app.frame.shape[:2]
            x, y, w, h = (0, 0, rw, rh)
            aspect1 = rw / rh
            aspect2 = fw / fh
            if aspect1 > aspect2:
                w = rh * aspect2
                x = (rw - w) / 2
            else:
                h = rw / aspect2
                y = (rh - h) / 2
            p.drawImage(QRect(x, y, w, h), self.mat_to_qimage(self.app.frame))
        '''
        if self.app.frame is not None:
            p.setTransform(self.view_transform)
            p.drawImage(0, 0, self.mat_to_qimage(self.app.frame))

        for i in range(len(self.app.label_areas)):
            area = self.app.label_areas[i]
            p.drawRect(area.rect)

    def mousePressEvent(self, e):

        if e.button() == Qt.LeftButton and e.modifiers() & Qt.ShiftModifier:
            self.view_press_start_pos = e.position() / self.view_zoom
            self.view_translate_start_pos = self.view_translate_pos
        elif self.mode == self.MODE_DRAW_LABEL:
            area = LabelArea()
            t,_ = self.view_transform.inverted()
            area.rect = QRectF(t.map(e.position()), t.map(e.position()))
            self.app.label_areas.append(area)
            self.mode = self.MODE_DRAW_LABEL_MOVE

        self.update_view_transform()
        self.update()

    def mouseMoveEvent(self, e):

        if e.modifiers() & Qt.ShiftModifier:
            self.view_translate_pos = self.view_translate_start_pos + \
                e.position() / self.view_zoom - self.view_press_start_pos
        elif self.mode == self.MODE_DRAW_LABEL_MOVE:
            t,_ = self.view_transform.inverted()
            area = self.app.label_areas[-1]
            area.rect.setBottomRight(t.map(e.position()))

        self.update_view_transform()
        self.update()

    def mouseReleaseEvent(self, e):

        if not self.view_press_start_pos.isNull():
            self.view_translate_pos = self.view_translate_start_pos + \
                e.position() / self.view_zoom - self.view_press_start_pos
            self.view_press_start_pos = QPointF()
            self.view_translate_start_pos = QPointF()

        if self.mode == self.MODE_DRAW_LABEL_MOVE:
            t,_ = self.view_transform.inverted()
            area = self.app.label_areas[-1]
            area.rect.setBottomRight(t.map(e.position()))
            self.mode = self.MODE_DRAW_LABEL
            label = LabelSelectDialog.getLabel(self)
            if label != None:
                area.id = label.id
            else:
                self.app.label_areas.remove(area)

        self.update_view_transform()
        self.update()

    def wheelEvent(self, e):

        if not e.pixelDelta().isNull():
            speed = e.pixelDelta().y() * 0.02 * 0.75
            self.view_zoom += speed
            self.view_zoom = min(max(self.view_zoom, 0.1), 10)
        elif not e.angleDelta().isNull():
            speed = e.angleDelta().y() * 0.001 * 0.75
            self.view_zoom += speed
            self.view_zoom = min(max(self.view_zoom, 0.1), 10)

        self.update_view_transform()
        self.update()

    def create_rectagle(self):
        self.mode = self.MODE_DRAW_LABEL
        self.setCursor(Qt.CrossCursor)

    def update_view_transform(self):
        if self.app.frame is not None:

            rw, rh = (self.width(), self.height())
            fh, fw = self.app.frame.shape[:2]
            t = QTransform()

            t.translate(rw/2, rh/2)
            t.scale(self.view_zoom, self.view_zoom)
            t.translate(-rw/2, -rh/2)

            t.translate(rw/2 - fw/2, rh/2 - fh/2)
            t.translate(self.view_translate_pos.x(),
                        self.view_translate_pos.y())

            self.view_transform = t

    def mat_to_qimage(self, mat):
        h, w = mat.shape[:2]
        if len(mat.shape) == 2:
            return QImage(mat.data, w, h, QImage.Format_Grayscale8)
        else:
            return QImage(mat.ravel(), w, h, w * mat.shape[2], QImage.Format_BGR888)
        return None
