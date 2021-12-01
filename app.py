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

        return self._instance
