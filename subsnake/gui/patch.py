from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (
    QGroupBox, QComboBox, QPushButton,
    QHBoxLayout, QDialog, QDialogButtonBox,
    QLineEdit, QGridLayout
)
from importlib import resources
import json
import subsnake.patches
from platformdirs import user_data_dir
from pathlib import Path

class PatchManager(QGroupBox):
    patch_loaded = Signal(dict)
    def __init__(self, sliders_dict, button_group_list, mod_dials_dict):
        super().__init__()
        self.setTitle("patch")

        self.patch_select = QComboBox()
        self.patch_select.setFocusPolicy(Qt.NoFocus)
        self.save_patch = QPushButton("save")
        self.new_patch = QPushButton("new")
        self.patch_dialog = NewPatchDialog()
        self.default_patch = {"osc_drift": 0, "osc_freq": 0, "osc_amp": 500, "osc_width": 250, "osc_wave": "pulse",
                            "osc2_freq": 0, "osc2_det": 0, "osc2_amp": 0, "osc2_width": 250, "osc2_wave": "saw",
                            "osc3_freq": 0, "osc3_det": 0, "osc3_amp": 0, "osc3_width": 250, "osc3_wave": "saw",
                            "filt_freq": 700, "filt_res": 0, "filt_drive": 40, "filt_sat": 100, "filt_type": "low",
                            "fenv_att": 10, "fenv_dec": 500, "fenv_sus": 1000, "fenv_rel": 500, "fenv_amt": 0,
                            "env_att": 10, "env_dec": 500, "env_sus": 1000, "env_rel": 250,
                            "del_time": 100, "del_fback": 500, "del_mix": 0,
                            "lfo1_freq": 100, "lfo1_phase": 0, "lfo2_freq": 267, "lfo2_phase": 500,
                            "lfo1_freq_ass": 0, "lfo1_freq_mod": 0, "lfo1_phase_ass": 0, "lfo1_phase_mod": 0,
                            "lfo2_freq_ass": 0, "lfo2_freq_mod": 0, "lfo2_phase_ass": 0, "lfo2_phase_mod": 0,
                            "menv1_att_ass": 0, "menv1_att_mod": 0, "menv1_rel_ass": 0, "menv1_rel_mod": 0,
                            "menv2_att_ass": 0, "menv2_att_mod": 0, "menv2_rel_ass": 0, "menv2_rel_mod": 0,
                            "menv1_att": 500, "menv1_rel": 500, "menv2_att": 250, "menv2_rel": 250,
                            "osc_freq_mod": 0, "osc_freq_ass": 0, "osc_amp_mod": 0, "osc_amp_ass": 0, "osc_width_mod": 0, "osc_width_ass": 0,
                            "osc2_freq_mod": 0, "osc2_freq_ass": 0, "osc2_det_mod": 0, "osc2_det_ass": 0,
                            "osc2_amp_mod": 0, "osc2_amp_ass": 0, "osc2_width_mod": 0, "osc2_width_ass": 0,
                            "osc3_freq_mod": 0, "osc3_freq_ass": 0, "osc3_det_mod": 0, "osc3_det_ass": 0,
                            "osc3_amp_mod": 0, "osc3_amp_ass": 0, "osc3_width_mod": 0, "osc3_width_ass": 0,
                            "filt_freq_mod": 0, "filt_freq_ass": 0, "filt_res_mod": 0, "filt_res_ass": 0,
                            "filt_drive_mod": 0, "filt_drive_ass": 0, "filt_sat_mod": 0, "filt_sat_ass": 0,
                            "fenv_att_mod": 0, "fenv_att_ass": 0, "fenv_dec_mod": 0, "fenv_dec_ass": 0,
                            "fenv_sus_mod": 0, "fenv_sus_ass": 0, "fenv_rel_mod": 0, "fenv_rel_ass": 0, "fenv_amt_mod": 0, "fenv_amt_ass": 0,
                            "env_att_mod": 0, "env_att_ass": 0, "env_dec_mod": 0, "env_dec_ass": 0,
                            "env_sus_mod": 0, "env_sus_ass": 0, "env_rel_mod": 0, "env_rel_ass": 0,
                            "del_time_mod": 0, "del_time_ass": 0, "del_fback_mod": 0, "del_fback_ass": 0, "del_mix_mod": 0, "del_mix_ass": 0,
                            "lfo1_shape": "sine", "lfo2_shape": "sine", "menv1_mode": "AR","menv2_mode": "Loop"}
        self.current_patch = {}
        self.sliders_dict = sliders_dict
        self.button_group_list = button_group_list
        self.mod_dials_dict = mod_dials_dict

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
        self.save_patch.setObjectName("save_patch")
        self.new_patch.setObjectName("new_patch")
        self.setAttribute(Qt.WA_StyledBackground, True)

        #get paths to patches & create name lists
        self.factory_patch_path = resources.files(subsnake.patches)
        self.factory_patch_names = []
        self.user_patch_path = Path(user_data_dir("subsnake", "rainbow-carrots")) / "patches"
        self.user_patch_names = []

        #ensure user patch directory exists
        self.check_user_dir()

        #init patch_select
        for patch in self.factory_patch_path.iterdir():
            if patch.is_file() and patch.name.endswith(".json"):
                filename = patch.name.removesuffix(".json")
                self.factory_patch_names.append(filename)

        for patch in self.user_patch_path.iterdir():
            if patch.is_file() and patch.name.endswith(".json"):
                filename = patch.name.removesuffix(".json")
                self.user_patch_names.append(filename)
        
        sorted_patches = sorted(list(set(self.factory_patch_names + self.user_patch_names)))
        self.patch_select.addItems(sorted_patches)

        self.patch_select.currentTextChanged.connect(self.load_patch)
        self.new_patch.clicked.connect(self.create_patch)
        self.save_patch.clicked.connect(self.save_patch_data)

    def load_patch(self, patch_name):
        patch_file = patch_name + ".json"
        if patch_name in self.user_patch_names:
            patch_path = self.user_patch_path / patch_file
        else:
            patch_path = Path(self.factory_patch_path / patch_file)
        with patch_path.open("r") as f:
            patch_data = json.load(f)
        self.patch_loaded.emit(patch_data)

    def create_patch(self):
        if self.patch_dialog.exec():
            new_name = self.patch_dialog.get_name()
            if new_name not in self.user_patch_names:
                    self.user_patch_names.append(new_name)
            if (new_name != ""):
                new_filename = new_name + ".json"
                new_path = self.user_patch_path / new_filename
                with new_path.open("w") as f:
                    json.dump(self.default_patch, f, indent=4)
                self.patch_select.blockSignals(True)
                self.patch_select.addItem(new_name)
                self.patch_select.setCurrentIndex(self.patch_select.count()-1)
                self.patch_select.blockSignals(False)
                self.load_patch(new_name)
        self.patch_dialog.clear_name()

    def save_patch_data(self):
        new_name = self.patch_select.currentText()
        if new_name not in self.user_patch_names:
            self.user_patch_names.append(new_name)
        new_filename = new_name + ".json"
        new_path = self.user_patch_path / new_filename
        self.update_patch()
        with new_path.open("w") as f:
            json.dump(self.current_patch, f, indent=4)

    def update_patch(self):
        for param in self.sliders_dict:
            self.current_patch.update({param: self.sliders_dict[param].value()})
        for param in self.mod_dials_dict:
            self.current_patch.update({param + "_mod": self.mod_dials_dict[param].value()})
            self.current_patch.update({param + "_ass": self.mod_dials_dict[param].get_mode()})
        osc_wave_button = self.button_group_list[0].checkedButton()
        osc2_wave_button = self.button_group_list[1].checkedButton()
        osc3_wave_button = self.button_group_list[2].checkedButton()
        filt_alg_button = self.button_group_list[3].checkedButton()
        lfo1_shape_button = self.button_group_list[4].checkedButton()
        lfo2_shape_button = self.button_group_list[5].checkedButton()
        menv1_mode_button = self.button_group_list[6].checkedButton()
        menv2_mode_button = self.button_group_list[7].checkedButton()
        self.current_patch.update({"osc_wave": osc_wave_button.text()})
        self.current_patch.update({"osc2_wave": osc2_wave_button.text()})
        self.current_patch.update({"osc3_wave": osc3_wave_button.text()})
        self.current_patch.update({"filt_type": filt_alg_button.text()})
        self.current_patch.update({"lfo1_shape": lfo1_shape_button.text()})
        self.current_patch.update({"lfo2_shape": lfo2_shape_button.text()})
        self.current_patch.update({"menv1_mode": menv1_mode_button.text()})
        self.current_patch.update({"menv2_mode": menv2_mode_button.text()})

    def check_user_dir(self):
        self.user_patch_path.mkdir(parents=True, exist_ok=True)

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
