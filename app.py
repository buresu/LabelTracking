import os
from PySide6.QtCore import Qt, Signal, QObject, QJsonDocument, QFile
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

        self.version = '0.0.1'

        self.output_dir = './output'

        self.labels = []
        self.label_areas = []
        self.current_label = None

        self.auto_tracking = False
        self.trackers = []

        self.file_path = ''
        self.frame = None
        self.vide_capture = cv.VideoCapture()

        # load config
        self.load()

    def save(self):

        # save config
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        f = QFile(os.path.join(self.output_dir, 'config.json'))
        if f.open(QFile.WriteOnly):
            json = dict()
            json['version'] = self.version
            json['filePath'] = self.file_path
            json['labels'] = [label.serialize() for label in self.labels]
            f.write(QJsonDocument.fromVariant(json).toJson())
            f.close()

    def load(self):

        # load config
        f = QFile(os.path.join(self.output_dir, 'config.json'))
        if f.open(QFile.ReadOnly):
            try:
                json = QJsonDocument.fromJson(f.readAll()).object()
                self.version = json['version']
                self.file_path = json['filePath']
                self.labels = [Label.deserialized(
                    obj) for obj in json['labels']]
                print(self.labels)
            except:
                print('Can not load config')
            f.close()
            self.request_update()

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
                    if area.enabled:
                        ret, box = self.trackers[self.label_areas.index(
                            area)].update(self.frame)
                        if ret:
                            x, y, w, h = box[0:4]
                            area.key_points[0] = QPointF(x, y)
                            area.key_points[1] = QPointF(x + w, y + h)
                            area.update()
        self.request_update()

    def start_tracking(self):
        if self.frame is not None:
            self.auto_tracking = True
            for area in self.label_areas:
                tracker = cv.TrackerCSRT_create()
                x = int(area.rect.x())
                y = int(area.rect.y())
                w = int(area.rect.width())
                h = int(area.rect.height())
                tracker.init(self.frame, [x, y, w, h])
                self.trackers.append(tracker)

    def stop_tracking(self):
        self.auto_tracking = False
        self.trackers.clear()

    def request_update(self):
        self.update.emit()
