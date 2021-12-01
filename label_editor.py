from PySide6.QtCore import Qt, QRect, QUrl, QRectF, QPointF, QSizeF
from PySide6.QtWidgets import QWidget, QMenu
from PySide6.QtGui import QImage, QPainter, QAction, QCursor
import cv2 as cv
from app import *
from label_select_dialog import *


class LabelEditor(QWidget):

    MODE_INVALID = 0
    MODE_DRAW_LABEL = 1
    MODE_DRAW_LABEL_MOVE = 2
    MODE_EDIT_LABEL = 3

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
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

    def context_menu(self, point):
        self.menu.exec_(self.mapToGlobal(point))

    def paintEvent(self, e):
        p = QPainter(self)
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

        for i in range(len(self.app.label_areas)):
            area = self.app.label_areas[i]
            p.drawRect(area.rect)

    def mousePressEvent(self, e):

        if self.mode == self.MODE_DRAW_LABEL:
            area = LabelArea()
            area.rect = QRectF(e.position(), e.position())
            self.app.label_areas.append(area)
            self.mode = self.MODE_DRAW_LABEL_MOVE

        self.update()

    def mouseMoveEvent(self, e):

        if self.mode == self.MODE_DRAW_LABEL_MOVE:
            area = self.app.label_areas[-1]
            area.rect.setBottomRight(e.position())

        self.update()

    def mouseReleaseEvent(self, e):

        if self.mode == self.MODE_DRAW_LABEL_MOVE:
            area = self.app.label_areas[-1]
            area.rect.setBottomRight(e.position())
            self.mode = self.MODE_DRAW_LABEL
            label = LabelSelectDialog.getLabel(self)
            if label != None:
                area.id = label.id
            else:
                self.app.label_areas.remove(area)

        self.update()

    def create_rectagle(self):
        self.mode = self.MODE_DRAW_LABEL
        self.setCursor(Qt.CrossCursor)

    def mat_to_qimage(self, mat):
        h, w = mat.shape[:2]
        if len(mat.shape) == 2:
            return QImage(mat.data, w, h, QImage.Format_Grayscale8)
        else:
            return QImage(mat.ravel(), w, h, w * mat.shape[2], QImage.Format_BGR888)
        return None
