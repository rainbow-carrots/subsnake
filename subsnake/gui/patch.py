from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (
    QWidget, QComboBox, QPushButton,
    QHBoxLayout
)

class PatchManager(QWidget):
    def __init__(self):
        super().__init__()

        self.patch_select = QComboBox()
        self.save_patch = QPushButton("save")
        self.new_patch = QPushButton("new")

        layout = QHBoxLayout()
        layout.addStretch()
        layout.addWidget(self.patch_select)
        layout.addStretch()
        layout.addWidget(self.save_patch)
        layout.addStretch()
        layout.addWidget(self.new_patch)
        layout.addStretch()

        self.setLayout(layout)

        self.setObjectName("patch_manager")
        self.setAttribute(Qt.WA_StyledBackground, True)