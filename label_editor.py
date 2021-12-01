from PySide6.QtCore import Qt, QRect, QUrl
from PySide6.QtWidgets import QWidget, QMenu
from PySide6.QtGui import QImage, QPainter, QAction
import cv2 as cv


class LabelEditor(QWidget):

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

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

        self.frame = None
        self.vide_capture = cv.VideoCapture()

    def context_menu(self, point):
        self.menu.exec_(self.mapToGlobal(point))

    def paintEvent(self, e):
        p = QPainter(self)
        if self.frame is not None:
            rw, rh = (self.width(), self.height())
            fh, fw = self.frame.shape[:2]
            x, y, w, h = (0, 0, rw, rh)
            aspect1 = rw / rh
            aspect2 = fw / fh
            if aspect1 > aspect2:
                w = rh * aspect2
                x = (rw - w) / 2
            else:
                h = rw / aspect2
                y = (rh - h) / 2
            p.drawImage(QRect(x, y, w, h), self.mat_to_qimage(self.frame))

    def open_image(self, filename):
        self.frame = cv.imread(filename, cv.IMREAD_COLOR)
        self.update()

    def open_video(self, filename):
        self.vide_capture.open(filename)
        self.vide_capture.set(cv.CAP_PROP_POS_FRAMES, 0)
        ret, frame = self.vide_capture.read()
        if ret:
            self.frame = frame
            self.update()

    def create_rectagle(self):
        print('create rectagle')

    def get_frame_count(self):
        return int(self.vide_capture.get(cv.CAP_PROP_FRAME_COUNT))

    def set_frame_position(self, pos):
        self.vide_capture.set(cv.CAP_PROP_POS_FRAMES, pos)
        ret, frame = self.vide_capture.read()
        if ret:
            self.frame = frame
            self.update()

    def mat_to_qimage(self, mat):
        h, w = mat.shape[:2]
        if len(mat.shape) == 2:
            return QImage(mat.data, w, h, QImage.Format_Grayscale8)
        else:
            return QImage(mat.ravel(), w, h, w * mat.shape[2], QImage.Format_BGR888)
        return None
