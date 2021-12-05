import os
import glob
import base64
import cv2 as cv
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
            f = QFile(os.path.join(dirname, basename))
            if f.open(QFile.WriteOnly):
                f2 = QFile(os.path.join(self.app.output_dir, basename))
                if f2.open(QFile.ReadOnly):
                    try:
                        json = QJsonDocument.fromJson(f2.readAll()).object()
                        label_areas = [LabelArea.deserialized(
                            obj) for obj in json['labelAreas']]
                        image_path = os.path.splitext(os.path.join(
                            self.app.output_dir, basename))[0] + '.jpg'
                        image_out_path = os.path.splitext(os.path.join(
                            dirname, basename))[0] + '.jpg'
                        image = cv.imread(image_path)
                        json = dict()
                        json['version'] = '4.6.1'
                        json['flags'] = {}
                        json['imageWidth'] = image.shape[1]
                        json['imageHeight'] = image.shape[0]
                        json['imagePath'] = os.path.relpath(
                            image_out_path, dirname)
                        ret, data = cv.imencode('.jpg', image)
                        json['imageData'] = base64.b64encode(
                            data.tobytes()).decode('utf-8')
                        areas = []
                        for area in label_areas:
                            area_json = dict()
                            area_json['label'] = area.id
                            area_json['group_id'] = None
                            area_json['flags'] = {}
                            area_json['shape_type'] = 'rectangle'
                            area_json['points'] = [[area.key_points[0].x(), area.key_points[0].y()], [
                                area.key_points[1].x(), area.key_points[1].y()]]
                            areas.append(area_json)
                        json['shapes'] = areas
                        f.write(QJsonDocument.fromVariant(json).toJson())
                        cv.imwrite(image_out_path, image)
                    except:
                        print('Export eccor')
                    f2.close()
                f.close()

    def read_data(self, filename):
        f = QFile(filename)
        if f.open(QFile.ReadOnly):
            data = f.readAll()
            f.close()
            return data
        return b''

    def save_data(self, filename, data):
        f = QFile(filename)
        if f.open(QFile.WriteOnly):
            f.write(data)
            f.close()
            return True
        return False
