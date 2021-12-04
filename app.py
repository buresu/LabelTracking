import os
from PySide6.QtCore import Qt, Signal, QObject, QJsonDocument, QFile, QFileInfo
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
        self.image_formats = ['jpg', 'png']
        self.video_formats = ['m4v', 'mp4', 'mov']
        self.frame_position = 0
        self.frame = None
        self.vide_capture = cv.VideoCapture()

        # load config
        self.load()

    def save(self):
        self.save_config()
        self.save_frame()

    def save_config(self):
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        f = QFile(os.path.join(self.output_dir, 'config.json'))
        if f.open(QFile.WriteOnly):
            json = dict()
            json['version'] = self.version
            json['filePath'] = self.file_path
            json['framePosition'] = self.frame_position
            json['labels'] = [label.serialize() for label in self.labels]
            f.write(QJsonDocument.fromVariant(json).toJson())
            f.close()

    def save_frame(self):
        base_name = QFileInfo(self.file_path).baseName()
        if self.is_sequential():
            base_name += '_%s' % self.frame_position
        f = QFile(os.path.join(self.output_dir, base_name + '.json'))
        if f.open(QFile.WriteOnly):
            json = dict()
            json['labelAreas'] = [area.serialize()
                                  for area in self.label_areas]
            f.write(QJsonDocument.fromVariant(json).toJson())
            f.close()
            cv.imwrite(os.path.join(self.output_dir,
                       base_name + '.jpg'), self.frame)

    def load(self):
        self.load_config()
        self.load_frame()

    def load_config(self):
        f = QFile(os.path.join(self.output_dir, 'config.json'))
        if f.open(QFile.ReadOnly):
            try:
                json = QJsonDocument.fromJson(f.readAll()).object()
                self.version = json['version']
                self.file_path = json['filePath']
                self.frame_position = json['framePosition']
                self.labels = [Label.deserialized(
                    obj) for obj in json['labels']]
            except:
                print('Can not load config')
            f.close()
            self.open_file(self.file_path)
            self.set_frame_position(self.frame_position)
        self.request_update()

    def load_frame(self):
        base_name = QFileInfo(self.file_path).baseName()
        if self.is_sequential():
            base_name += '_%s' % self.frame_position
        f = QFile(os.path.join(self.output_dir, base_name + '.json'))
        if f.open(QFile.ReadOnly):
            try:
                json = QJsonDocument.fromJson(f.readAll()).object()
                self.label_areas = [LabelArea.deserialized(
                    obj) for obj in json['labelAreas']]
            except:
                pass
            f.close()
        self.request_update()

    def is_sequential(self):
        ext = QFileInfo(self.file_path).completeSuffix()
        if ext in self.video_formats:
            return True
        return False

    def open_file(self, filename):
        ext = QFileInfo(filename).completeSuffix()
        if ext in self.image_formats:
            self.open_image(filename)
        elif ext in self.video_formats:
            self.open_video(filename)

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
        self.file_path = filename
        self.frame_position = 0
        self.frame = cv.imread(filename, cv.IMREAD_COLOR)
        self.request_update()

    def open_video(self, filename):
        self.file_path = filename
        self.vide_capture.open(filename)
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
        self.frame_position += 1
        if not self.auto_tracking:
            self.load_frame()
        self.read_video_frame()

    def set_frame_position(self, pos):
        self.frame_position = pos
        if not self.auto_tracking:
            self.load_frame()
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
