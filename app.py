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
        self.current_label = None

        self.auto_tracking = False
        self.trackers = []

        self.frame = None
        self.vide_capture = cv.VideoCapture()

    def save(self):
        pass

    def load(self):
        pass

    def add_label(self, id):
        idx = [i for i in range(len(self.labels)) if self.labels[i].id == id]
        if len(idx) == 0 and id != '':
            label = Label(id)
            self.labels.append(label)
            self.current_label = label
            self.request_update()
            return label

    def remove_label(self, id):
        idx = [i for i in range(len(self.labels)) if self.labels[i].id == id]
        if len(idx) > 0 and id != '':
            self.labels.remove(self.labels[idx[0]])
            if len(self.labels) == 0:
                self.current_label = None
            self.request_update()

    def get_label(self, id):
        idx = [i for i in range(len(self.labels)) if self.labels[i].id == id]
        if len(idx) > 0:
            return self.labels[idx[0]]
        return None

    def unselect_all_area(self):
        for a in self.label_areas:
            a.select = False

    def select_area(self, area):
        for a in self.label_areas:
            if a == area:
                a.select = True

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
            if self.auto_tracking:
                for area in self.label_areas:
                    ret, box = self.trackers[self.label_areas.index(
                        area)].update(self.frame)
                    if ret:
                        x1, y1, x2, y2 = box[0:4]
                        area.key_points[0] = QPointF(x1, y1)
                        area.key_points[1] = QPointF(x2, y2)
                        area.update()
        self.request_update()

    def start_tracking(self):
        if self.frame is not None:
            self.auto_tracking = True
            for area in self.label_areas:
                tracker = cv.TrackerCSRT_create()
                x1 = int(area.rect.topLeft().x())
                y1 = int(area.rect.topLeft().y())
                x2 = int(area.rect.bottomRight().x())
                y2 = int(area.rect.bottomRight().y())
                tracker.init(self.frame, [x1, y1, x2, y2])
                self.trackers.append(tracker)

    def stop_tracking(self):
        self.auto_tracking = False
        self.trackers.clear()

    def request_update(self):
        self.update.emit()
