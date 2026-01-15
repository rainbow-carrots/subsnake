from PySide6.QtWidgets import (
    QGroupBox, QGridLayout,
    QLabel, QComboBox,
    QPushButton
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QColor, QPalette
from subsnake.gui.midi_control import MIDIControl

class MIDISettings(QGroupBox):
    #signals (input)
    input_changed = Signal(str)
    channel_changed = Signal(int)
    inputs_refreshed = Signal()

    #signals (cc)
    cc_added = Signal(int, str, str)
    cc_param_changed = Signal(int, str, str)
    cc_changed = Signal(int, int, str, str)
    cc_deleted = Signal(int)

    def __init__(self):
        super().__init__()

        #attributes
        self.cc_rows = 0
        self.row_ccs = {}

        #layouts
        midi_layout = QGridLayout()
        midi_stack = QGridLayout()
        cc_layout = QGridLayout()
        self.cc_stack = QGridLayout()

        #internal group box
        self.cc_group = QGroupBox("cc assign")
        self.cc_group.setFocusPolicy(Qt.NoFocus)

        #labels (midi settings)
        self.midi_input_label = QLabel("device:")
        self.midi_channel_label = QLabel("channel:")
        self.midi_input_label.setAlignment(Qt.AlignCenter)
        self.midi_channel_label.setAlignment(Qt.AlignCenter)

        #labels (cc settings columns)
        self.cc_num_label = QLabel("CC")
        self.cc_group_label = QLabel("module")
        self.cc_param_label = QLabel("parameter")
        self.cc_num_label.setAlignment(Qt.AlignCenter)
        self.cc_group_label.setAlignment(Qt.AlignCenter)
        self.cc_param_label.setAlignment(Qt.AlignCenter)

        #combo boxes (midi settings)
        self.midi_select = QComboBox()
        self.midi_select.setEditable(False)
        self.midi_select.setInsertPolicy(QComboBox.InsertAtBottom)
        self.midi_select.setFocusPolicy(Qt.NoFocus)

        self.channel_select = QComboBox()
        self.channel_select.setEditable(False)
        self.channel_select.setInsertPolicy(QComboBox.InsertAtBottom)
        self.channel_select.setFocusPolicy(Qt.NoFocus)

        #pushbutton (device refresh)
        self.midi_refresh = QPushButton("⟳")
        self.midi_refresh.setCheckable(False)
        self.midi_refresh.setFocusPolicy(Qt.NoFocus)

        #pushbutton (add cc row)
        self.cc_add = QPushButton("+")
        self.cc_add.setCheckable(False)
        self.cc_add.setFocusPolicy(Qt.NoFocus)

        #object names
        self.cc_group.setObjectName("cc_group")
        self.midi_refresh.setObjectName("midi_refresh")
        self.cc_add.setObjectName("cc_add")
        self.setObjectName("midi_group")

        #add labels & combo boxes
        midi_layout.addWidget(self.midi_refresh, 0, 0)
        midi_layout.addWidget(self.midi_input_label, 0, 1)
        midi_layout.addWidget(self.midi_select, 0, 2)
        midi_layout.addWidget(self.midi_channel_label, 0, 3)
        midi_layout.addWidget(self.channel_select, 0, 4)

        #configure midi stack
        cc_layout.addWidget(self.cc_add, 0, 0)
        cc_layout.addWidget(self.cc_num_label, 0, 1)
        cc_layout.addWidget(self.cc_group_label, 0, 2)
        cc_layout.addWidget(self.cc_param_label, 0, 3)
        self.cc_stack.addLayout(cc_layout, 0, 0)
        self.cc_group.setLayout(self.cc_stack)
        midi_stack.addLayout(midi_layout, 0, 0)
        midi_stack.addWidget(self.cc_group, 1, 0)

        #set layout
        self.setLayout(midi_stack)

        #connect internal signals
        self.midi_select.currentTextChanged.connect(self.update_midi_in)
        self.channel_select.currentTextChanged.connect(self.update_midi_ch)
        self.midi_refresh.pressed.connect(self.refresh_midi_ins)
        self.cc_add.pressed.connect(self.add_cc)

    def update_midi_in(self, input_name):
        self.input_changed.emit(input_name)

    def update_midi_ch(self, channel):
        self.channel_changed.emit(int(channel))

    def refresh_midi_ins(self):
        self.inputs_refreshed.emit()

    def add_cc(self):
        new_cc = MIDIControl(self.row_ccs)
        cc_val = new_cc.cc_select.value()
        cc_param = new_cc.param_select.currentText()
        module = new_cc.module_select.currentText()
        self.cc_rows += 1
        new_cc.row = self.cc_rows
        self.row_ccs.update({new_cc.row: cc_val})
        print(self.row_ccs)
        self.cc_stack.addWidget(new_cc, self.cc_rows, 0)
        new_cc.cc_changed.connect(self.update_cc)
        new_cc.param_changed.connect(self.update_param)
        new_cc.cc_deleted.connect(self.delete_cc)
        self.cc_added.emit(cc_val, cc_param, module)

    def update_cc(self, new_cc, old_cc, param, module, row):
        self.row_ccs.update({row: new_cc})
        print(self.row_ccs)
        self.cc_changed.emit(new_cc, old_cc, param, module)

    def update_param(self, cc, new_param, module):
        self.cc_param_changed.emit(cc, new_param, module)

    def delete_cc(self, cc, row):
        print(f"DEBUG: delete row {row}")
        print(f"DEBUG: row_ccs before row deletion: {self.row_ccs}")
        if row in self.row_ccs:
            self.row_ccs.pop(row)
        cc_widget = self.cc_stack.itemAtPosition(row, 0).widget()
        cc_widget.cc_changed.disconnect(self.update_cc)
        cc_widget.param_changed.disconnect(self.update_param)
        cc_widget.cc_deleted.disconnect(self.delete_cc)
        if (row != self.cc_rows):
            for cc_index in range (row + 1, self.cc_rows + 1):
                cc_control = self.cc_stack.itemAtPosition(cc_index, 0).widget()
                self.cc_stack.removeWidget(cc_control)
                self.cc_stack.addWidget(cc_control, cc_index - 1, 0)
                if cc_control.row in self.row_ccs:
                    self.row_ccs.pop(cc_control.row)
                cc_control.row -= 1
                self.row_ccs.update({cc_control.row: cc_control.cc_select.value()})
        print(f"DEBUG: row_ccs after row deletion: {self.row_ccs}")
        self.cc_stack.removeWidget(cc_widget)
        self.cc_rows -= 1
        cc_widget.deleteLater()
        self.cc_deleted.emit(cc)
