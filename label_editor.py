from PySide6.QtCore import Qt, QRect
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QImage, QPainter
import cv2 as cv


class LabelEditor(QWidget):

    frame = None

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.setAutoFillBackground(True)
        self.setPalette(Qt.darkGray)

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

    def mat_to_qimage(self, mat):
        h, w, d = mat.shape
        if d == 1:
            return QImage(mat.data, w, h, QImage.Format_Grayscale8)
        if d == 3:
            return QImage(mat.ravel(), w, h, w * d, QImage.Format_BGR888)
        if d == 4:
            return QImage(mat.ravel(), w, h, w * d, QImage.Format_ARGB32)
        return None
