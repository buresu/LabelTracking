from PySide6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QListView, QDialogButtonBox
from app import *
from label_view import *


class LabelSelectDialog(QDialog):

    def __init__(self, parent=None):
        super(LabelSelectDialog, self).__init__(parent)
        self.app = App()

        self.setWindowTitle('Select Label')

        self.label_view = LabelView()

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        vbox = QVBoxLayout()
        vbox.addWidget(self.label_view)
        vbox.addWidget(self.button_box)

        self.setLayout(vbox)

    def getLabel(parent=None):
        dialog = LabelSelectDialog(parent)
        if dialog.exec() == QDialog.Accepted:
            return dialog.app.current_label
        return None
