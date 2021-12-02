import cv2 as cv
from label import *


class App(object):
    # Singleton
    _instance = None

    def __new__(self):
        if self._instance is None:
            self._instance = super(App, self).__new__(self)

            self.labels = []
            self.label_areas = []

            self.frame = None
            self.vide_capture = cv.VideoCapture()

        return self._instance

    def open_image(self, filename):
        self.frame = cv.imread(filename, cv.IMREAD_COLOR)

    def open_video(self, filename):
        self.vide_capture.open(filename)
        self.set_frame_position(0)

    def get_frame_count(self):
        return int(self.vide_capture.get(cv.CAP_PROP_FRAME_COUNT))

    def get_frame_position(self):
        return int(self.vide_capture.get(cv.CAP_PROP_POS_FRAMES))

    def back_frame_position(self):
        pos = self.get_frame_position() - 2
        pos = max(0, pos)
        self.set_frame_position(pos)

    def next_frame_position(self):
        self.read_video_frame()

    def set_frame_position(self, pos):
        self.vide_capture.set(cv.CAP_PROP_POS_FRAMES, pos)
        self.read_video_frame()

    def read_video_frame(self):
        ret, frame = self.vide_capture.read()
        if ret:
            self.frame = frame
