from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (
    QWidget, QComboBox, QPushButton,
    QHBoxLayout, QDialog, QDialogButtonBox,
    QLineEdit, QGridLayout
)
from importlib import resources
import json
import subsnake.patches

class PatchManager(QWidget):
    patch_loaded = Signal(dict)
    def __init__(self, sliders_dict, button_group_list):
        super().__init__()

        self.patch_select = QComboBox()
        self.patch_select.setFocusPolicy(Qt.NoFocus)
        self.save_patch = QPushButton("save")
        self.new_patch = QPushButton("new")
        self.patch_dialog = NewPatchDialog()
        self.default_patch = {"osc_freq": 0, "osc_amp": 250, "osc_width": 250, "osc_wave": "pulse",
                            "osc2_freq": 0, "osc2_det": 0, "osc2_amp": 250, "osc2_width": 250, "osc2_wave": "pulse",
                            "osc3_freq": 0, "osc3_det": 0, "osc3_amp": 250, "osc3_width": 250, "osc3_wave": "pulse",
                            "filt_freq": 700, "filt_res": 0, "filt_drive": 40, "filt_sat": 100, "filt_type": "low",
                            "fenv_att": 10, "fenv_dec": 500, "fenv_sus": 1000, "fenv_rel": 500, "fenv_amt": 0,
                            "env_att": 10, "env_dec": 500, "env_sus": 1000, "env_rel": 500,
                            "del_time": 100, "del_fback": 500, "del_mix": 0}
        self.current_patch = {}
        self.sliders_dict = sliders_dict
        self.button_group_list = button_group_list

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
        self.new_patch.clicked.connect(self.create_patch)
        self.save_patch.clicked.connect(self.save_patch_data)

    def load_patch(self, patch_name):
        patch_file = patch_name + ".json"
        patch_path = self.patch_path / patch_file
        with open(patch_path, "r") as f:
            patch_data = json.load(f)
        self.patch_loaded.emit(patch_data)

    def create_patch(self):
        if self.patch_dialog.exec():
            new_name = self.patch_dialog.get_name()
            if (new_name != ""):
                new_filename = new_name + ".json"
                new_path = self.patch_path / new_filename
                with open(new_path, "w") as f:
                    json.dump(self.default_patch, f, indent=4)
                self.patch_select.blockSignals(True)
                self.patch_select.addItem(new_name)
                self.patch_select.setCurrentIndex(self.patch_select.count()-1)
                self.patch_select.blockSignals(False)
                self.load_patch(new_name)
        self.patch_dialog.clear_name()

    def save_patch_data(self):
        new_name = self.patch_select.currentText()
        new_filename = new_name + ".json"
        new_path = self.patch_path / new_filename
        self.update_patch()
        with open(new_path, "w") as f:
            json.dump(self.current_patch, f, indent=4)

    def update_patch(self):
        for param in self.sliders_dict:
            self.current_patch.update({param: self.sliders_dict[param].value()})
        osc_wave_button = self.button_group_list[0].checkedButton()
        osc2_wave_button = self.button_group_list[1].checkedButton()
        osc3_wave_button = self.button_group_list[2].checkedButton()
        filt_alg_button = self.button_group_list[3].checkedButton()
        self.current_patch.update({"osc_wave": osc_wave_button.text()})
        self.current_patch.update({"osc2_wave": osc2_wave_button.text()})
        self.current_patch.update({"osc3_wave": osc3_wave_button.text()})
        self.current_patch.update({"filt_type": filt_alg_button.text()})

class NewPatchDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.name_input = QLineEdit()
        self.buttons = QDialogButtonBox(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        self.buttons.setFocusPolicy(Qt.NoFocus)

        layout = QGridLayout()
        layout.addWidget(self.name_input, 0, 0)
        layout.addWidget(self.buttons, 1, 0)

        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        self.setLayout(layout)
        self.setObjectName("new_patch_dialog")
        self.setWindowTitle("enter name:")

    def get_name(self):
        return self.name_input.text()
    
    def clear_name(self):
        self.name_input.setText("")
