import os
import copy
from PySide6.QtCore import Qt, Signal, QObject, QJsonDocument, QFile, QFileInfo, QStandardPaths
from PySide6.QtGui import QUndoStack, QUndoCommand
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

class SaveAppStateCommand(QUndoCommand):
    def __init__(self):
        super(SaveAppStateCommand, self).__init__()
        self.app = App()

    def begin(self):
        self.begin_labels = copy.deepcopy(self.app.labels)
        self.begin_current_label = copy.deepcopy(self.app.current_label)

    def end(self):
        self.end_labels = copy.deepcopy(self.app.labels)
        self.end_current_label = copy.deepcopy(self.app.current_label)

    def undo(self):
        self.app.labels = copy.deepcopy(self.begin_labels)
        self.app.current_label = copy.deepcopy(self.begin_current_label)
        self.app.request_update()

    def redo(self):
        self.app.labels = copy.deepcopy(self.end_labels)
        self.app.current_label = copy.deepcopy(self.end_current_label)
        self.app.request_update()

class App(QObject, metaclass=Singleton):

    update = Signal()

    def __init__(self):
        super(App, self).__init__()

        self.version = '0.2.3'

        self.output_dir = os.path.abspath('./output')

        self.labels = []
        self.label_areas = []
        self.current_label = None

        self.auto_id = False
        self.auto_save = False

        self.auto_tracking = False

        self.file_path = ''
        self.image_formats = ['jpg', 'png']
        self.video_formats = ['m4v', 'mp4', 'mov']
        self.frame_position = 0
        self.frame = None
        self.vide_capture = cv.VideoCapture()

        # undo stack
        self.undo_stack = QUndoStack(self)

        # load config
        self.load_app_config()
        self.load()

    def save(self):
        self.save_app_config()
        self.save_config()
        self.save_frame()

    def save_app_config(self):
        config_dir = QStandardPaths.standardLocations(
            QStandardPaths.AppConfigLocation)[0]
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
        f = QFile(os.path.join(config_dir, 'config.json'))
        if f.open(QFile.WriteOnly):
            json = dict()
            json['lastOutputDir'] = self.output_dir
            f.write(QJsonDocument.fromVariant(json).toJson())
            f.close()

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
        if len(self.label_areas) == 0:
            return
        base_name = QFileInfo(self.file_path).baseName()
        if self.is_sequential():
            base_name += '_%s' % str(self.frame_position).zfill(
                len(str(self.get_frame_count())))
        f = QFile(os.path.join(self.output_dir, base_name + '.json'))
        if f.open(QFile.WriteOnly):
            json = dict()
            json['labelAreas'] = [area.serialize()
                                  for area in self.label_areas]
            filename = os.path.join(self.output_dir, base_name + '.jpg')
            json['fileName'] = filename
            f.write(QJsonDocument.fromVariant(json).toJson())
            f.close()
            ret, array = cv.imencode('.jpg', self.frame, [cv.IMWRITE_JPEG_QUALITY, 100])
            f = QFile(filename)
            if ret and f.open(QFile.WriteOnly):
                f.write(array.tobytes())
                f.close()

    def load(self):
        self.load_config()
        self.load_frame()

    def load_app_config(self):
        config_dir = QStandardPaths.standardLocations(
            QStandardPaths.AppConfigLocation)[0]
        f = QFile(os.path.join(config_dir, 'config.json'))
        if f.open(QFile.ReadOnly):
            try:
                json = QJsonDocument.fromJson(f.readAll()).object()
                self.output_dir = json['lastOutputDir']
            except:
                print('Can not load app config')
            f.close()

    def load_config(self):
        f = QFile(os.path.join(self.output_dir, 'config.json'))
        if f.open(QFile.ReadOnly):
            try:
                json = QJsonDocument.fromJson(f.readAll()).object()
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
        # store previous label areas
        previous_label_areas = self.label_areas.copy()
        # clear previous label areas
        self.label_areas.clear()
        # load file
        base_name = QFileInfo(self.file_path).baseName()
        if self.is_sequential():
            base_name += '_%s' % str(self.frame_position).zfill(
                len(str(self.get_frame_count())))
        f = QFile(os.path.join(self.output_dir, base_name + '.json'))
        if f.open(QFile.ReadOnly):
            try:
                json = QJsonDocument.fromJson(f.readAll()).object()
                self.label_areas = [LabelArea.deserialized(
                    obj) for obj in json['labelAreas']]
            except:
                pass
            f.close()
        # set new label id if auto id is enabled
        if self.auto_id:
            label_ids = [label.id for label in self.labels]
            for area in self.label_areas:
                if not area.id in label_ids and area.enabled:
                    for pre_area in previous_label_areas:
                        if area.get_iou(pre_area) > 0.5:
                            area.id = pre_area.id
                            break
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

    def import_label(self, filename):
        self.labels.clear()
        f = QFile(filename)
        if f.open(QFile.ReadOnly):
            try:
                json = QJsonDocument.fromJson(f.readAll()).object()
                self.labels = [Label.deserialized(
                    obj) for obj in json['labels']]
            except:
                print('Can not load label file')
            f.close()
        self.request_update()

    def export_label(self, filename):
        if len(self.labels) == 0:
            return
        f = QFile(filename)
        if f.open(QFile.WriteOnly):
            json = dict()
            json['labels'] = [label.serialize() for label in self.labels]
            f.write(QJsonDocument.fromVariant(json).toJson())
            f.close()

    def add_label(self, id):
        idx = [i for i in range(len(self.labels)) if self.labels[i].id == id]
        if len(idx) == 0 and id != '':

            cmd = SaveAppStateCommand()
            cmd.setText('Edit Label')
            cmd.begin()

            label = Label(id)
            self.labels.append(label)
            self.current_label = label

            cmd.end()
            self.undo_stack.push(cmd)

            self.request_update()
            return label

    def remove_label(self, id):
        idx = [i for i in range(len(self.labels)) if self.labels[i].id == id]
        if len(idx) > 0 and id != '':

            cmd = SaveAppStateCommand()
            cmd.setText('Edit Label')
            cmd.begin()

            self.labels.remove(self.labels[idx[0]])
            if len(self.labels) == 0:
                self.current_label = None

            cmd.end()
            self.undo_stack.push(cmd)

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
        if self.auto_save:
            self.save()
        pos = max(0, self.get_frame_position() - 2)
        self.frame_position = pos
        if not self.auto_tracking:
            self.load_frame()
        self.vide_capture.set(cv.CAP_PROP_POS_FRAMES, pos)
        self.read_video_frame()

    def next_frame_position(self):
        if self.auto_save:
            self.save()
        if self.frame_position + 1 >= self.get_frame_count():
            return
        self.frame_position += 1
        if not self.auto_tracking:
            self.load_frame()
        self.read_video_frame()

    def set_frame_position(self, pos):
        if self.auto_save:
            self.save()
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
                    area.update_tracker(self.frame)
        self.request_update()

    def start_tracking(self):
        if self.frame is not None:
            self.auto_tracking = True
            for area in self.label_areas:
                area.start_tracking(self.frame)

    def stop_tracking(self):
        self.auto_tracking = False
        for area in self.label_areas:
            area.stop_tracking()

    def request_update(self):
        self.update.emit()
