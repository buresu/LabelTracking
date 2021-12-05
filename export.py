import os
import glob
import shutil
import base64
from PySide6.QtGui import QImageReader
from app import *


class Exporter(object):
    def __init__(self):
        self.app = App()

    def export_to_labelme(self, dirname):

        # create directory
        if not os.path.exists(dirname):
            os.makedirs(dirname)

        # saerch files
        filenames = glob.glob(os.path.join(self.app.output_dir, '*.json'))
        filenames = [f for f in filenames if 'config.json' not in f]

        # save files
        for filename in filenames:
            basename = os.path.basename(filename)
            print(basename)
            frame_data = self.read_data(
                os.path.join(self.app.output_dir, basename))
            try:
                json = QJsonDocument.fromJson(frame_data).object()
                label_areas = [LabelArea.deserialized(
                    obj) for obj in json['labelAreas']]
                image_path = os.path.splitext(os.path.join(
                    self.app.output_dir, basename))[0] + '.jpg'
                image_out_path = os.path.splitext(os.path.join(
                    dirname, basename))[0] + '.jpg'
                image = QImageReader(image_path)
                json = dict()
                json['version'] = '4.6.1'
                json['flags'] = {}
                json['imageWidth'] = image.size().width()
                json['imageHeight'] = image.size().height()
                json['imagePath'] = os.path.relpath(
                    image_out_path, dirname)
                image_data = self.read_data(image_path)
                json['imageData'] = base64.b64encode(
                    image_data).decode('utf-8')
                areas = []
                for area in label_areas:
                    if not area.enabled:
                        continue
                    area_json = dict()
                    area_json['label'] = area.id
                    area_json['group_id'] = None
                    area_json['flags'] = {}
                    area_json['shape_type'] = 'rectangle'
                    area_json['points'] = [[area.key_points[0].x(), area.key_points[0].y()], [
                        area.key_points[1].x(), area.key_points[1].y()]]
                    areas.append(area_json)
                json['shapes'] = areas
                self.write_data(os.path.join(dirname, basename),
                                QJsonDocument.fromVariant(json).toJson())
                shutil.copyfile(image_path, image_out_path)
            except:
                print('Export eccor')

    def read_data(self, filename):
        f = QFile(filename)
        if f.open(QFile.ReadOnly):
            data = f.readAll()
            f.close()
            return data
        return b''

    def write_data(self, filename, data):
        f = QFile(filename)
        if f.open(QFile.WriteOnly):
            f.write(data)
            f.close()
            return True
        return False
