from PySide6.QtWidgets import (
    QPushButton, QSpinBox, QComboBox,
    QGridLayout, QWidget
)
from PySide6.QtCore import Signal

class MIDIControl(QWidget):
    
    #signals
    param_changed = Signal(int, str, str)
    cc_changed = Signal(int, int, str, str)
    cc_deleted = Signal(int, int)
    
    def __init__(self):
        super().__init__()

        #attributes
        self.prev_cc = 63
        self.row = 0

        #layout
        layout = QGridLayout()
        
        #widgets
        self.cc_delete = QPushButton("-")
        self.cc_select = QSpinBox()
        self.module_select = QComboBox()
        self.param_select = QComboBox()

        #param name LUT
        self.param_names = [["pitch", "level", "width"], ["pitch", "detune", "level", "width"],
                            ["cutoff", "feedback", "drive", "saturate"], ["attack", "decay", "sustain", "release", "depth"],
                            ["attack", "decay", "sustain", "release"]]

        #init widgets
        self.cc_select.setRange(0, 127)
        self.cc_select.setValue(63)
        self.module_select.addItems(["oscillator 1", "oscillator 2", "filter", "filter env", "envelope"])
        self.module_select.setCurrentIndex(0)
        self.param_select.addItems(self.param_names[0])
        self.param_select.setCurrentIndex(0)
        self.cc_delete.setObjectName("cc_delete")

        #add widgets to layout
        layout.addWidget(self.cc_delete, 0, 0)
        layout.addWidget(self.cc_select, 0, 1)
        layout.addWidget(self.module_select, 0, 2)
        layout.addWidget(self.param_select, 0, 3)
        
        #connect signals
        self.module_select.currentIndexChanged.connect(self.update_params_list)
        self.param_select.currentTextChanged.connect(self.update_param)
        self.cc_select.valueChanged.connect(self.update_cc)
        self.cc_delete.pressed.connect(self.delete_cc)

        #set widget layout
        self.setLayout(layout)
    
    def update_params_list(self, module_index):
        self.param_select.clear()
        self.param_select.addItems(self.param_names[module_index])

    def update_param(self, new_param):
        current_cc = self.cc_select.value()
        self.param_changed.emit(current_cc, new_param, self.module_select.currentText())

    def update_cc(self, new_cc):
        self.cc_changed.emit(new_cc, self.prev_cc, self.param_select.currentText(), self.module_select.currentText())
        self.prev_cc = new_cc

    def delete_cc(self):
        self.cc_deleted.emit(self.cc_select.value(), self.row)
