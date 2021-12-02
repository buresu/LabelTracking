from PySide6.QtCore import Qt, QRect, QUrl, QRectF, QPointF, QSizeF
from PySide6.QtWidgets import QWidget, QMenu
from PySide6.QtGui import QImage, QPainter, QAction, QCursor, QTransform
import cv2 as cv
from app import *
from label_select_dialog import *


class LabelEditor(QWidget):

    MODE_INVALID = 0
    MODE_VIEW_TRANSFORM = 1
    MODE_DRAW_LABEL = 2

    def __init__(self, parent=None):
        super(LabelEditor, self).__init__(parent)
        self.app = App()
        self.app.update.connect(self.update)

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
        self.draw_label_area = None

    def context_menu(self, point):
        self.menu.exec_(self.mapToGlobal(point))

    def paintEvent(self, e):
        p = QPainter(self)
        p.setTransform(self.get_view_transform())

        # frame
        if self.app.frame is not None:
            p.drawImage(0, 0, self.mat_to_qimage(self.app.frame))

        # unselected area
        for i in range(len(self.app.label_areas)):
            area = self.app.label_areas[i]
            if not area.select:
                p.save()
                label = self.app.get_label(area.id)
                if label != None:
                    p.setPen(label.color)
                    p.drawText(area.rect.topLeft() + QPointF(1, -1), label.id)
                p.drawRect(area.rect)
                p.restore()

        # selected area
        for i in range(len(self.app.label_areas)):
            area = self.app.label_areas[i]
            if area.select:
                p.save()
                p.setPen(Qt.yellow)
                label = self.app.get_label(area.id)
                if label != None:
                    p.drawText(area.rect.topLeft() + QPointF(1, -1), label.id)
                p.drawRect(area.rect)
                for key in area.key_points:
                    key_rect = QRectF(0, 0, 5, 5)
                    key_rect.moveCenter(key)
                    p.fillRect(key_rect, Qt.yellow)
                p.restore()

        # draw area
        if self.draw_label_area != None:
            p.save()
            p.setPen(Qt.white)
            p.drawRect(self.draw_label_area.rect)
            p.restore()

    def mousePressEvent(self, e):

        # transform
        t, _ = self.get_view_transform().inverted()
        local_pos = t.map(e.position())

        # view transform
        if e.button() == Qt.LeftButton and e.modifiers() & Qt.ShiftModifier:
            self.mode = self.MODE_VIEW_TRANSFORM
            self.view_press_start_pos = e.position() / self.view_zoom
            self.view_translate_start_pos = self.view_translate_pos

        # select area
        self.app.unselect_all_area()
        for i in range(len(self.app.label_areas)):
            area = self.app.label_areas[i]
            if area.rect.contains(local_pos):
                area.select = True
                break

        # draw label
        if self.mode == self.MODE_DRAW_LABEL:
            self.draw_label_area = LabelArea()
            self.draw_label_area.key_points[0] = local_pos
            self.draw_label_area.key_points[1] = local_pos
            self.draw_label_area.update()

        self.update()

    def mouseMoveEvent(self, e):

        # transform
        t, _ = self.get_view_transform().inverted()
        local_pos = t.map(e.position())

        # view transform
        if self.mode == self.MODE_VIEW_TRANSFORM:
            self.view_translate_pos = self.view_translate_start_pos + \
                e.position() / self.view_zoom - self.view_press_start_pos

        # draw label
        if self.draw_label_area != None:
            self.draw_label_area.key_points[1] = local_pos
            self.draw_label_area.update()

        self.update()

    def mouseReleaseEvent(self, e):

        # transform
        t, _ = self.get_view_transform().inverted()
        local_pos = t.map(e.position())

        # view transform
        if self.mode == self.MODE_VIEW_TRANSFORM:
            self.view_translate_pos = self.view_translate_start_pos + \
                e.position() / self.view_zoom - self.view_press_start_pos
            self.view_press_start_pos = QPointF()
            self.view_translate_start_pos = QPointF()
            self.mode = self.MODE_DRAW_LABEL

        # draw label
        if self.draw_label_area != None:
            self.draw_label_area.key_points[1] = local_pos
            self.draw_label_area.update()

            if not self.draw_label_area.rect.isEmpty():
                if self.app.current_label != None:
                    self.draw_label_area.id = self.app.current_label.id
                    self.app.label_areas.append(self.draw_label_area)
                else:
                    label = LabelSelectDialog.getLabel(self)
                    if label != None:
                        self.draw_label_area.id = label.id
                        self.app.label_areas.append(self.draw_label_area)

            self.draw_label_area = None
            self.app.request_update()

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

        self.update()

    def create_rectagle(self):
        self.mode = self.MODE_DRAW_LABEL
        self.setCursor(Qt.CrossCursor)

    def get_view_transform(self):
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

            return t
        return QTransform()

    def mat_to_qimage(self, mat):
        h, w = mat.shape[:2]
        if len(mat.shape) == 2:
            return QImage(mat.data, w, h, QImage.Format_Grayscale8)
        else:
            return QImage(mat.ravel(), w, h, w * mat.shape[2], QImage.Format_BGR888)
        return None
