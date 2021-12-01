from PySide6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QListView, QDialogButtonBox
from app import *
from label_list_model import *


class LabelSelectDialog(QDialog):

    def __init__(self, parent=None):
        super(LabelSelectDialog, self).__init__(parent)
        self.app = App()

        self.setWindowTitle('Select Label')

        self.label_input = QLineEdit()

        model = LabelListModel()

        self.label_view = QListView()
        self.label_view.setModel(model)
        self.label_view.selectionModel().selectionChanged.connect(self.label_changed)
        self.label_view.setCurrentIndex(model.index(0))

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        vbox = QVBoxLayout()
        vbox.addWidget(self.label_input)
        vbox.addWidget(self.label_view)
        vbox.addWidget(self.button_box)

        self.setLayout(vbox)

    def label_changed(self, select):
        self.label_input.setText(select.indexes()[0].data(Qt.DisplayRole))

    def getLabel(parent=None):
        dialog = LabelSelectDialog(parent)
        if dialog.exec() == QDialog.Accepted:
            id = dialog.label_input.text()
            idx = [i for i in range(len(dialog.app.labels)) if dialog.app.labels[i].id == id]
            if len(idx) > 0:
                return dialog.app.labels[idx[0]]
            elif id != '':
                label = Label(id)
                dialog.app.labels.append(label)
                return label
        return None
