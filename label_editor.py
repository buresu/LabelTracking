from PySide6.QtCore import Qt, QRect, QUrl, QRectF, QPointF, QSizeF
from PySide6.QtWidgets import QWidget, QMenu
from PySide6.QtGui import QImage, QPainter, QAction, QCursor, QTransform, QPen, QFont
import cv2 as cv
from app import *
from label_select_dialog import *


class LabelEditor(QWidget):

    MODE_DRAW = 0
    MODE_EDIT = 1

    def __init__(self, parent=None):
        super(LabelEditor, self).__init__(parent)
        self.app = App()
        self.app.update.connect(self.update)

        self.setAutoFillBackground(True)
        self.setPalette(Qt.darkGray)

        self.setFocusPolicy(Qt.ClickFocus)

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.context_menu)

        self.view_zoom = 1.0
        self.view_press_start_pos = QPointF()
        self.view_translate_pos = QPointF()
        self.view_translate_start_pos = QPointF()
        self.draw_label_area = None

        self.set_mode(LabelEditor.MODE_DRAW)

    def context_menu(self, point):

        menu = QMenu(self)

        select_label_action = QAction('Select Label', self)
        select_label_action.setEnabled(self.mode == LabelEditor.MODE_EDIT)
        select_label_action.triggered.connect(self.select_label)
        menu.addAction(select_label_action)

        remove_area_action = QAction('Remove', self)
        remove_area_action.setEnabled(self.mode == LabelEditor.MODE_EDIT)
        remove_area_action.triggered.connect(self.remove_area)

        menu.addAction(remove_area_action)

        menu.exec_(self.mapToGlobal(point))

    def paintEvent(self, e):
        p = QPainter(self)
        p.setTransform(self.get_view_transform())

        # frame
        if self.app.frame is not None:
            p.drawImage(0, 0, self.mat_to_qimage(self.app.frame))

        # unselected area
        for i in range(len(self.app.label_areas)):
            area = self.app.label_areas[i]
            if not area.select and area.enabled:
                p.save()
                label = self.app.get_label(area.id)
                pen = QPen(Qt.white)
                pen.setWidthF(2 / self.view_zoom)
                p.setPen(pen)
                font = p.font()
                font.setPointSizeF(10 / self.view_zoom)
                p.setFont(font)
                if label != None:
                    pen.setColor(label.color)
                    p.setPen(pen)
                    p.drawText(area.rect.topLeft() +
                               QPointF(5, -5) / self.view_zoom, label.id)
                p.drawRect(area.rect)
                p.restore()

        # selected area
        for i in range(len(self.app.label_areas)):
            area = self.app.label_areas[i]
            if area.select and area.enabled:
                p.save()
                pen = QPen(Qt.yellow)
                pen.setWidthF(2 / self.view_zoom)
                p.setPen(pen)
                font = p.font()
                font.setPointSizeF(10 / self.view_zoom)
                p.setFont(font)
                label = self.app.get_label(area.id)
                if label != None:
                    p.drawText(area.rect.topLeft() +
                               QPointF(5, -5) / self.view_zoom, label.id)
                p.drawRect(area.rect)
                for key in area.key_points:
                    key_rect = QRectF(
                        0, 0, 7 / self.view_zoom, 7 / self.view_zoom)
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
            self.view_press_start_pos = e.position() / self.view_zoom
            self.view_translate_start_pos = self.view_translate_pos
            self.update()
            return

        if self.mode == LabelEditor.MODE_EDIT:
            # select area
            if e.button() == Qt.LeftButton:
                self.app.unselect_all_area()
                for i in range(len(self.app.label_areas)):
                    area = self.app.label_areas[i]
                    if area.rect.contains(local_pos) and area.enabled:
                        area.select = True
                        break

            # select key points
            for area in self.app.label_areas:
                if area.enabled:
                    for key in area.key_points:
                        key_rect = QRectF(
                            0, 0,  10 / self.view_zoom, 10 / self.view_zoom)
                        key_rect.moveCenter(key)
                        if key_rect.contains(local_pos):
                            area.key_points_selection[area.key_points.index(
                                key)] = True
                            break

        # draw label
        if self.mode == LabelEditor.MODE_DRAW:
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
        if not self.view_press_start_pos.isNull():
            self.view_translate_pos = self.view_translate_start_pos + \
                e.position() / self.view_zoom - self.view_press_start_pos

        if self.mode == LabelEditor.MODE_EDIT:
            # key point
            for area in self.app.label_areas:
                if area.enabled:
                    for i, b in enumerate(area.key_points_selection):
                        if b:
                            area.key_points[i] = local_pos
                            area.update()
                            break

        # draw label
        if self.mode == LabelEditor.MODE_DRAW and self.draw_label_area != None:
            self.draw_label_area.key_points[1] = local_pos
            self.draw_label_area.update()

        self.update()

    def mouseReleaseEvent(self, e):

        # transform
        t, _ = self.get_view_transform().inverted()
        local_pos = t.map(e.position())

        # view transform
        if not self.view_press_start_pos.isNull():
            self.view_translate_pos = self.view_translate_start_pos + \
                e.position() / self.view_zoom - self.view_press_start_pos
            self.view_press_start_pos = QPointF()
            self.view_translate_start_pos = QPointF()

        if self.mode == LabelEditor.MODE_EDIT:
            # key point
            for area in self.app.label_areas:
                if area.enabled:
                    for i, b in enumerate(area.key_points_selection):
                        if b:
                            area.key_points[i] = local_pos
                            area.update()
                            break
                    area.key_points_selection = [
                        False for i in area.key_points_selection]
                    if self.app.auto_tracking:
                        self.app.stop_tracking()
                        self.app.start_tracking()

        # draw label
        if self.mode == LabelEditor.MODE_DRAW and self.draw_label_area != None:
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
            if self.app.auto_tracking:
                self.app.stop_tracking()
                self.app.start_tracking()

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

    def remove_area(self):
        for area in self.app.label_areas:
            if area.select:
                self.app.label_areas.remove(area)
                if self.app.auto_tracking:
                    self.app.stop_tracking()
                    self.app.start_tracking()
                self.app.request_update()

    def select_label(self):
        for area in self.app.label_areas:
            if area.select:
                label = LabelSelectDialog.getLabel(self)
                if label != None:
                    area.id = label.id
                    self.app.request_update()

    def set_mode(self, mode):
        self.mode = mode
        if mode == LabelEditor.MODE_DRAW:
            self.setCursor(Qt.CrossCursor)
            self.app.unselect_all_area()
        elif mode == LabelEditor.MODE_EDIT:
            self.setCursor(Qt.ArrowCursor)
        self.update()

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
