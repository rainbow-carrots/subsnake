from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (
    QWidget, QComboBox, QPushButton,
    QHBoxLayout
)
from importlib import resources
import json
import subsnake.patches

class PatchManager(QWidget):
    patch_loaded = Signal(dict)
    def __init__(self):
        super().__init__()

        self.patch_select = QComboBox()
        self.patch_select.setFocusPolicy(Qt.NoFocus)
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

        #get path to patches
        self.patch_path = resources.files(subsnake.patches)
        self.patch_names = []

        #init patch_select
        for patch in self.patch_path.iterdir():
            if patch.is_file() and patch.name.endswith(".json"):
                filename = patch.name.removesuffix(".json")
                self.patch_names.append(filename)
        self.patch_select.addItems(self.patch_names)

        self.patch_select.currentTextChanged.connect(self.load_patch)

    def load_patch(self, patch_name):
        patch_file = patch_name + ".json"
        patch_path = self.patch_path / patch_file
        with open(patch_path, "r") as f:
            patch_data = json.load(f)
        self.patch_loaded.emit(patch_data)

