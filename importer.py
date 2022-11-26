import os
import glob
import shutil
from PySide6.QtWidgets import QApplication
from app import *


class Importer(object):
    def __init__(self):
        self.app = App()

    def import_from_labelme(self, dirname):

        # check for the directory
        if not os.path.exists(dirname):
            print('Can not find target directory')
            return

        # saerch files
        filenames = glob.glob(os.path.join(dirname, '*.json'))

        # file is empty
        if len(filenames) == 0:
            print('Can not find target files')
            return

        # remove existent files
        existent_files = glob.glob(os.path.join(self.app.output_dir, '*'))
        existent_files = [f for f in existent_files if 'config.json' not in f]
        for filename in existent_files:
            os.remove(filename)

        # load files
        for filename in filenames:
            basename = os.path.basename(filename)
            print(basename)
            frame_data = self.read_data(filename)
            try:
                json = QJsonDocument.fromJson(frame_data).object()
                image_path = json['imagePath']
                shapes = json['shapes']
                json = dict()
                json['fileName'] = image_path
                areas = []
                for shape in shapes:
                    area_json = dict()
                    area_json['enabled'] = True
                    area_json['id'] = shape['label']
                    area_json['points'] = shape['points']
                    areas.append(area_json)
                json['labelAreas'] = areas
                self.write_data(os.path.join(self.app.output_dir, basename),
                    QJsonDocument.fromVariant(json).toJson())
                image_in_path = os.path.join(dirname, os.path.basename(image_path))
                image_out_path = os.path.join(self.app.output_dir, os.path.basename(image_path))
                shutil.copyfile(image_in_path, image_out_path)
            except Exception as e:
                print(e)

            # process events
            QApplication.processEvents()

        # load first frame
        self.app.set_frame_position(0)

    def read_data(self, filename):
        f = QFile(filename)
        if f.open(QFile.ReadOnly):
            data = f.readAll()
            f.close()
            return data.data()
        return b''

    def write_data(self, filename, data):
        f = QFile(filename)
        if f.open(QFile.WriteOnly):
            f.write(data)
            f.close()
            return True
        return False
