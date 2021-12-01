from PySide6.QtCore import Qt, QRect, QUrl
from PySide6.QtWidgets import QWidget, QMenu
from PySide6.QtGui import QImage, QPainter, QAction
import cv2 as cv

from app import *
from label_select_dialog import *

class LabelEditor(QWidget):

    MODE_INVALID=0
    MODE_DRAW_LABEL=1
    MODE_EDIT_LABEL=2

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

        self.dialog = LabelSelectDialog()
        self.dialog.show()

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

    def open_image(self, filename):
        self.app.frame = cv.imread(filename, cv.IMREAD_COLOR)
        self.update()

    def open_video(self, filename):
        self.app.vide_capture.open(filename)
        self.app.vide_capture.set(cv.CAP_PROP_POS_FRAMES, 0)
        ret, frame = self.app.vide_capture.read()
        if ret:
            self.app.frame = frame
            self.update()

    def create_rectagle(self):
        print('create rectagle')

    def get_frame_count(self):
        return int(self.app.vide_capture.get(cv.CAP_PROP_FRAME_COUNT))

    def get_frame_position(self):
        return int(self.app.vide_capture.get(cv.CAP_PROP_POS_FRAMES))

    def back_frame_position(self):
        pos = self.get_frame_position() - 2
        pos = max(0, pos)
        self.set_frame_position(pos)

    def next_frame_position(self):
        ret, frame = self.app.vide_capture.read()
        if ret:
            self.app.frame = frame
            self.update()

    def set_frame_position(self, pos):
        self.app.vide_capture.set(cv.CAP_PROP_POS_FRAMES, pos)
        ret, frame = self.app.vide_capture.read()
        if ret:
            self.app.frame = frame
            self.update()

    def mat_to_qimage(self, mat):
        h, w = mat.shape[:2]
        if len(mat.shape) == 2:
            return QImage(mat.data, w, h, QImage.Format_Grayscale8)
        else:
            return QImage(mat.ravel(), w, h, w * mat.shape[2], QImage.Format_BGR888)
        return None
