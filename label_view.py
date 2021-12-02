from PySide6.QtWidgets import QFrame, QVBoxLayout, QLineEdit, QListView, QHBoxLayout, QPushButton
from app import *
from label_list_model import *


class LabelView(QFrame):

    def __init__(self, parent=None):
        super(LabelView, self).__init__(parent)
        self.app = App()

        self.setWindowTitle('Select Label')

        self.label_input = QLineEdit()
        self.label_input.setFocusPolicy(Qt.ClickFocus)

        self.label_add_button = QPushButton()
        self.label_add_button.setIcon(QIcon.fromTheme("document-new"))
        self.label_add_button.clicked.connect(self.add_label)

        hvox = QHBoxLayout()
        hvox.addWidget(self.label_input)
        hvox.addWidget(self.label_add_button)

        self.model = LabelListModel()

        self.label_view = QListView()
        self.label_view.setModel(self.model)
        self.label_view.selectionModel().selectionChanged.connect(self.label_changed)
        self.label_view.setCurrentIndex(self.model.index(0))

        vbox = QVBoxLayout()
        vbox.addLayout(hvox)
        vbox.addWidget(self.label_view)

        self.setLayout(vbox)

    def label_changed(self, select):
        self.label_input.setText(select.indexes()[0].data(Qt.DisplayRole))

    def add_label(self):
        self.app.add_label(self.label_input.text())
        self.model.update()

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
