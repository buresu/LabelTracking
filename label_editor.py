from PySide2.QtCore import Qt, QRect, QUrl
from PySide2.QtWidgets import QWidget, QMenu, QAction
from PySide2.QtGui import QImage, QPainter
from PySide2.QtMultimedia import QMediaPlayer
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

        self.frame = QImage()

        self.video_player = QMediaPlayer()
        #self.video_sink = QVideoSink()
        #self.video_sink.videoFrameChanged.connect(self.vide_frame_changed)
        #self.video_player.setVideoSink(self.video_sink)

    def context_menu(self, point):
        self.menu.exec_(self.mapToGlobal(point))

    def paintEvent(self, e):
        p = QPainter(self)
        if not self.frame.isNull():
            rw, rh = (self.width(), self.height())
            fw, fh = (self.frame.width(), self.frame.height())
            x, y, w, h = (0, 0, rw, rh)
            aspect1 = rw / rh
            aspect2 = fw / fh
            if aspect1 > aspect2:
                w = rh * aspect2
                x = (rw - w) / 2
            else:
                h = rw / aspect2
                y = (rh - h) / 2
            p.drawImage(QRect(x, y, w, h), self.frame)

    def open_image(self, filename):
        self.frame.load(filename)
        self.update()

    def open_video(self, filename):
        self.video_player.setSource(QUrl.fromLocalFile(filename))
        self.video_player.setPosition(0)
        self.update()

    def create_rectagle(self):
        print('create rectagle')

    def get_video_duration(self):
        return self.video_player.duration()

    def set_video_position(self, pos):
        print(pos)
        self.video_player.setPosition(pos)

    def vide_frame_changed(self, frame):
        self.frame = frame.toImage()
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
