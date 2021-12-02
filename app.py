from PySide6.QtCore import Qt, Signal, QObject
import cv2 as cv
from label import *


class Singleton(type(QObject), type):
    def __init__(cls, name, bases, dict):
        super().__init__(name, bases, dict)
        cls._instance = None

    def __call__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__call__(*args, **kwargs)
        return cls._instance


class App(QObject, metaclass=Singleton):

    update = Signal()

    def __init__(self):
        super(App, self).__init__()

        self.labels = []
        self.label_areas = []

        self.frame = None
        self.vide_capture = cv.VideoCapture()

    def add_label(self, id):
        idx = [i for i in range(len(self.labels)) if self.labels[i].id == id]
        if len(idx) == 0 and id != '':
            self.labels.append(Label(id))
        self.request_update()

    def remove_label(self, id):
        idx = [i for i in range(len(self.labels)) if self.labels[i].id == id]
        if len(idx) > 0 and id != '':
            self.labels.remove(self.labels[idx[0]])
        self.request_update()

    def get_label(self, id):
        idx = [i for i in range(len(self.labels)) if self.labels[i].id == id]
        if len(idx) > 0:
            return self.labels[idx[0]]
        return None

    def open_image(self, filename):
        self.frame = cv.imread(filename, cv.IMREAD_COLOR)
        self.request_update()

    def open_video(self, filename):
        self.vide_capture.open(filename)
        self.set_frame_position(0)
        self.request_update()

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
        self.request_update()

    def request_update(self):
        self.update.emit()
