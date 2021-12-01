from PySide6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QListView, QDialogButtonBox
from app import *
from label_list_model import *


class LabelSelectDialog(QDialog):

    def __init__(self, parent=None):
        super(LabelSelectDialog, self).__init__(parent)
        self.app = App()

        self.label_input = QLineEdit()

        self.label_view = QListView()
        self.label_view.setModel(LabelListModel())

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Ok|QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        vbox = QVBoxLayout()
        vbox.addWidget(self.label_input)
        vbox.addWidget(self.label_view)
        vbox.addWidget(self.button_box)

        self.setLayout(vbox)
