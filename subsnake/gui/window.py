from subsnake.audio.engine import AudioEngine
from subsnake.gui.keys import Keys
from subsnake.gui.midi_control import MIDIControl
from subsnake.gui.osc_gui import OscillatorGUI
from subsnake.gui.osc2_gui import Oscillator2GUI
from subsnake.gui.filt_gui import FilterGUI
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QColor, QPalette
from PySide6.QtWidgets import (
    QMainWindow, QGridLayout,
    QSlider, QRadioButton,
    QLabel, QLCDNumber,
    QHBoxLayout, QWidget,
    QButtonGroup, QPushButton,
    QGroupBox, QComboBox,
    QToolBar, QFrame)

key_conv = Keys()

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        #attributes
        self.midi_controls = []
        self.cc_rows = 0

        #toolbar
        self.main_toolbar = QToolBar()
        self.main_toolbar.setMovable(False)
        self.toggle_midi = QAction("midi", self)
        self.toggle_midi.setToolTip("show/hide midi menu")
        self.toggle_midi.setCheckable(True)
        self.toggle_midi.setChecked(False)
        self.main_toolbar.addAction(self.toggle_midi)
        midi_action = self.main_toolbar.widgetForAction(self.toggle_midi)
        midi_action.setObjectName("toggle_midi")
        self.addToolBar(self.main_toolbar)

        #layouts
        midi_layout = QGridLayout()
        midi_stack = QGridLayout()
        cc_layout = QGridLayout()
        self.cc_stack = QGridLayout()
        self.env_grid = QGridLayout()
        self.fenv_grid = QGridLayout()
        self.window_grid = QGridLayout()

        #group boxes
        self.midi_group = QGroupBox("midi input")
        self.midi_group.setFocusPolicy(Qt.NoFocus)
        self.cc_group = QGroupBox("cc assign")
        self.cc_group.setFocusPolicy(Qt.NoFocus)
        self.filt_group = FilterGUI()
        self.osc_group = OscillatorGUI()
        self.osc2_group = Oscillator2GUI()
        env_group = QGroupBox("envelope")
        fenv_group = QGroupBox("filter envelope")
        self.midi_group.hide()

        #labels
        self.midi_input_label = QLabel("device:")
        self.midi_channel_label = QLabel("channel:")
        self.midi_input_label.setAlignment(Qt.AlignCenter)
        self.midi_channel_label.setAlignment(Qt.AlignCenter)

        self.cc_num_label = QLabel("CC")
        self.cc_group_label = QLabel("module")
        self.cc_param_label = QLabel("parameter")
        self.cc_num_label.setAlignment(Qt.AlignCenter)
        self.cc_group_label.setAlignment(Qt.AlignCenter)
        self.cc_param_label.setAlignment(Qt.AlignCenter)

        self.adsr_att_label = QLabel("attack:")
        self.adsr_dec_label = QLabel("decay:")
        self.adsr_sus_label = QLabel("sustain:")
        self.adsr_rel_label = QLabel("release:")
        self.adsr_gate_label = QLabel("gate:")

        self.fenv_att_label = QLabel("attack:")
        self.fenv_dec_label = QLabel("decay:")
        self.fenv_sus_label = QLabel("sustain:")
        self.fenv_rel_label = QLabel("release:")
        self.fenv_amt_label = QLabel("depth:")

        # amp envelope
        self.adsr_att_slider = QSlider(Qt.Horizontal)
        self.adsr_att_slider.setSingleStep(1)
        self.adsr_att_slider.setRange(1, 1000)

        self.adsr_dec_slider = QSlider(Qt.Horizontal)
        self.adsr_dec_slider.setSingleStep(1)
        self.adsr_dec_slider.setRange(1, 1000)

        self.adsr_sus_slider = QSlider(Qt.Horizontal)
        self.adsr_sus_slider.setSingleStep(1)
        self.adsr_sus_slider.setRange(1, 1000)

        self.adsr_rel_slider = QSlider(Qt.Horizontal)
        self.adsr_rel_slider.setSingleStep(1)
        self.adsr_rel_slider.setRange(1, 1000)

        # filter envelope
        self.fenv_att_slider = QSlider(Qt.Horizontal)
        self.fenv_att_slider.setSingleStep(1)
        self.fenv_att_slider.setRange(1, 1000)

        self.fenv_dec_slider = QSlider(Qt.Horizontal)
        self.fenv_dec_slider.setSingleStep(1)
        self.fenv_dec_slider.setRange(1, 1000)

        self.fenv_sus_slider = QSlider(Qt.Horizontal)
        self.fenv_sus_slider.setSingleStep(1)
        self.fenv_sus_slider.setRange(1, 1000)

        self.fenv_rel_slider = QSlider(Qt.Horizontal)
        self.fenv_rel_slider.setSingleStep(1)
        self.fenv_rel_slider.setRange(1, 1000)

        self.fenv_amt_slider = QSlider(Qt.Horizontal)
        self.fenv_amt_slider.setSingleStep(1)
        self.fenv_amt_slider.setRange(-500, 500)
        self.fenv_amt_slider.setValue(1)

        #displays
        self.adsr_att_display = self.configure_display(QLCDNumber(), 3, QLCDNumber.Dec, QLCDNumber.Flat, True)
        self.adsr_dec_display = self.configure_display(QLCDNumber(), 3, QLCDNumber.Dec, QLCDNumber.Flat, True)
        self.adsr_sus_display = self.configure_display(QLCDNumber(), 3, QLCDNumber.Dec, QLCDNumber.Flat, True)
        self.adsr_rel_display = self.configure_display(QLCDNumber(), 3, QLCDNumber.Dec, QLCDNumber.Flat, True)

        self.fenv_att_display = self.configure_display(QLCDNumber(), 3, QLCDNumber.Dec, QLCDNumber.Flat, True)
        self.fenv_dec_display = self.configure_display(QLCDNumber(), 3, QLCDNumber.Dec, QLCDNumber.Flat, True)
        self.fenv_sus_display = self.configure_display(QLCDNumber(), 3, QLCDNumber.Dec, QLCDNumber.Flat, True)
        self.fenv_rel_display = self.configure_display(QLCDNumber(), 3, QLCDNumber.Dec, QLCDNumber.Flat, True)
        self.fenv_amt_display = self.configure_display(QLCDNumber(), 3, QLCDNumber.Dec, QLCDNumber.Flat, True)

        self.set_palette(self.adsr_att_display, 2)
        self.set_palette(self.adsr_dec_display, 2)
        self.set_palette(self.adsr_sus_display, 2)
        self.set_palette(self.adsr_rel_display, 2)

        self.set_palette(self.fenv_att_display, 2)
        self.set_palette(self.fenv_dec_display, 2)
        self.set_palette(self.fenv_sus_display, 2)
        self.set_palette(self.fenv_rel_display, 2)
        self.set_palette(self.fenv_amt_display, 2)

        #combo boxes (midi)
        self.midi_select = QComboBox()
        self.midi_select.setEditable(False)
        self.midi_select.setInsertPolicy(QComboBox.InsertAtBottom)
        self.midi_select.setFocusPolicy(Qt.NoFocus)

        self.channel_select = QComboBox()
        self.channel_select.setEditable(False)
        self.channel_select.setInsertPolicy(QComboBox.InsertAtBottom)
        self.channel_select.setFocusPolicy(Qt.NoFocus)

        #refresh button
        self.midi_refresh = QPushButton("⟳")
        self.midi_refresh.setCheckable(False)
        self.midi_refresh.setFocusPolicy(Qt.NoFocus)

        #add midi cc button
        self.cc_add = QPushButton("+")
        self.cc_add.setCheckable(False)
        self.cc_add.setFocusPolicy(Qt.NoFocus)

        #grid spacers
        # row 0
        self.grid_space_0 = QFrame()
        self.grid_space_0.setFrameShape(QFrame.NoFrame)
        self.grid_space_1 = QFrame()
        self.grid_space_1.setFrameShape(QFrame.NoFrame)
        self.grid_space_2 = QFrame()
        self.grid_space_2.setFrameShape(QFrame.NoFrame)
        self.grid_space_3 = QFrame()
        self.grid_space_3.setFrameShape(QFrame.NoFrame)

        #object names
        self.grid_space_0.setObjectName("grid_space_0")
        self.grid_space_1.setObjectName("grid_space_1")
        self.grid_space_2.setObjectName("grid_space_2")
        self.grid_space_3.setObjectName("grid_space_3")
        self.midi_group.setObjectName("midi_group")
        self.cc_group.setObjectName("cc_group")
        env_group.setObjectName("env_group")
        fenv_group.setObjectName("fenv_group")
        self.midi_refresh.setObjectName("midi_refresh")
        self.cc_add.setObjectName("cc_add")

        self.env_grid.addWidget(self.adsr_att_label, 0, 0)
        self.env_grid.addWidget(self.adsr_dec_label, 1, 0)
        self.env_grid.addWidget(self.adsr_sus_label, 2, 0)
        self.env_grid.addWidget(self.adsr_rel_label, 3, 0)
        self.env_grid.addWidget(self.adsr_gate_label, 4, 0)

        self.fenv_grid.addWidget(self.fenv_att_label, 0, 0)
        self.fenv_grid.addWidget(self.fenv_dec_label, 1, 0)
        self.fenv_grid.addWidget(self.fenv_sus_label, 2, 0)
        self.fenv_grid.addWidget(self.fenv_rel_label, 3, 0)
        self.fenv_grid.addWidget(self.fenv_amt_label, 4, 0)

        self.env_grid.addWidget(self.adsr_att_slider, 0, 1)
        self.env_grid.addWidget(self.adsr_dec_slider, 1, 1)
        self.env_grid.addWidget(self.adsr_sus_slider, 2, 1)
        self.env_grid.addWidget(self.adsr_rel_slider, 3, 1)

        self.fenv_grid.addWidget(self.fenv_att_slider, 0, 1)
        self.fenv_grid.addWidget(self.fenv_dec_slider, 1, 1)
        self.fenv_grid.addWidget(self.fenv_sus_slider, 2, 1)
        self.fenv_grid.addWidget(self.fenv_rel_slider, 3, 1)
        self.fenv_grid.addWidget(self.fenv_amt_slider, 4, 1)

        self.env_grid.addWidget(self.adsr_att_display, 0, 2)
        self.env_grid.addWidget(self.adsr_dec_display, 1, 2)
        self.env_grid.addWidget(self.adsr_sus_display, 2, 2)
        self.env_grid.addWidget(self.adsr_rel_display, 3, 2)

        self.fenv_grid.addWidget(self.fenv_att_display, 0, 2)
        self.fenv_grid.addWidget(self.fenv_dec_display, 1, 2)
        self.fenv_grid.addWidget(self.fenv_sus_display, 2, 2)
        self.fenv_grid.addWidget(self.fenv_rel_display, 3, 2)
        self.fenv_grid.addWidget(self.fenv_amt_display, 4, 2)

        #add gate control
        self.env_gate = QPushButton("latch")
        self.env_gate.setObjectName("env_gate")
        self.env_gate.setCheckable(True)
        self.env_grid.addWidget(self.env_gate, 4, 1)

        #add labels & combo boxes (midi)
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

        #add layouts to groups
        self.midi_group.setLayout(midi_stack)
        env_group.setLayout(self.env_grid)
        fenv_group.setLayout(self.fenv_grid)

        #add groups/midi to window
        self.window_grid.addWidget(self.grid_space_2, 0, 0)
        self.window_grid.addWidget(self.osc_group, 0, 1)
        self.window_grid.addWidget(self.grid_space_0, 0, 2)
        self.window_grid.addWidget(self.filt_group, 0, 3)
        self.window_grid.addWidget(self.grid_space_1, 0, 4)
        self.window_grid.addWidget(env_group, 0, 5)
        self.window_grid.addWidget(self.grid_space_3, 0, 6)
        self.window_grid.addWidget(self.osc2_group, 1, 1)
        self.window_grid.addWidget(fenv_group, 1, 3)
        self.window_grid.addWidget(self.midi_group, 2, 1)

        #set column spacing
        self.window_grid.setColumnMinimumWidth(5, 30)

        #set layout of window
        window_widget = QWidget()
        window_widget.setLayout(self.window_grid)

        #start audio engine
        self.engine = AudioEngine()

        #connect signals
        self.midi_select.currentTextChanged.connect(self.update_midi_in)
        self.channel_select.currentTextChanged.connect(self.update_midi_ch)
        self.midi_refresh.pressed.connect(self.refresh_midi_ins)
        self.cc_add.pressed.connect(self.add_cc)
        self.toggle_midi.toggled.connect(self.toggle_midi_box)

        self.filt_group.freq_changed.connect(self.update_filt_freq)
        self.filt_group.res_changed.connect(self.update_filt_res)
        self.filt_group.drive_changed.connect(self.update_filt_drive)
        self.filt_group.sat_changed.connect(self.update_filt_sat)
        self.filt_group.alg_changed.connect(self.update_filt_alg)

        self.osc_group.pitch_changed.connect(self.update_osc_freq)
        self.osc_group.level_changed.connect(self.update_osc_amp)
        self.osc_group.width_changed.connect(self.update_osc_width)
        self.osc_group.alg_changed.connect(self.update_osc_alg)

        self.osc2_group.pitch_changed.connect(self.update_osc2_freq)
        self.osc2_group.detune_changed.connect(self.update_osc2_det)
        self.osc2_group.level_changed.connect(self.update_osc2_amp)
        self.osc2_group.width_changed.connect(self.update_osc2_width)
        self.osc2_group.alg_changed.connect(self.update_osc2_alg)

        self.adsr_att_slider.valueChanged.connect(self.update_env_attack)
        self.adsr_dec_slider.valueChanged.connect(self.update_env_decay)
        self.adsr_sus_slider.valueChanged.connect(self.update_env_sustain)
        self.adsr_rel_slider.valueChanged.connect(self.update_env_release)

        self.fenv_att_slider.valueChanged.connect(self.update_fenv_attack)
        self.fenv_dec_slider.valueChanged.connect(self.update_fenv_decay)
        self.fenv_sus_slider.valueChanged.connect(self.update_fenv_sustain)
        self.fenv_rel_slider.valueChanged.connect(self.update_fenv_release)
        self.fenv_amt_slider.valueChanged.connect(self.update_fenv_amount)

        self.env_gate.clicked.connect(self.update_gate)

        self.init_params()
        self.setCentralWidget(window_widget)

    #helper functions
    # args: QLCDDisplay widget, # of digits, mode (hex, dec, oct, bin),
    # dig_style (outline, filled, flat), small decimal flag (for floats)
    def configure_display(self, display, num_digits, num_mode, dig_style, small_dec):
        display.setMode(num_mode)
        display.setDigitCount(num_digits)
        display.setSegmentStyle(dig_style)
        display.setSmallDecimalPoint(small_dec)
        return display
    
    def init_params(self):
        self.filt_group.filt_freq_slider.setValue(700)
        self.filt_group.filt_res_slider.setValue(0)
        self.filt_group.filt_drive_slider.setValue(40)
        self.filt_group.filt_sat_slider.setValue(800)

        self.osc_group.osc_freq_slider.setValue(0)
        self.osc_group.osc_amp_slider.setValue(250)
        self.osc_group.osc_width_slider.setValue(250)

        self.osc2_group.osc2_freq_slider.setValue(0)
        self.osc2_group.osc2_det_slider.setValue(0)
        self.osc2_group.osc2_amp_slider.setValue(250)
        self.osc2_group.osc2_width_slider.setValue(250)

        self.adsr_att_slider.setValue(10)
        self.adsr_dec_slider.setValue(500)
        self.adsr_sus_slider.setValue(1000)
        self.adsr_rel_slider.setValue(500)

        self.fenv_att_slider.setValue(10)
        self.fenv_dec_slider.setValue(500)
        self.fenv_sus_slider.setValue(1000)
        self.fenv_rel_slider.setValue(500)
        self.fenv_amt_slider.setValue(0)

    def set_palette(self, display, group):
        if group == 0:      #osc group
            text_color = QColor("#d2e9ff")
        elif group == 1:    #filt group
            text_color = QColor("#edfff2")
        elif group == 2:    #env group
            text_color = QColor("#fde7f1")
        elif group == 3:    #osc2 group
            text_color = QColor("#bcd7f0")
        display_palette = display.palette()
        display_palette.setColor(QPalette.ColorRole.WindowText, text_color)
        display.setAutoFillBackground(True)
        display.setPalette(display_palette)

    def assign_cc_function(self, module, param):
        cc_func = None
        if (module == "oscillator 1"):
            if (param == "pitch"):
                cc_func = self.update_osc_freq
            elif (param == "level"):
                cc_func = self.update_osc_amp
            elif (param == "width"):
                cc_func = self.update_osc_width
        elif (module == "oscillator 2"):
            if (param == "pitch"):
                cc_func = self.update_osc2_freq
            elif (param == "detune"):
                cc_func = self.update_osc2_det
            elif (param == "level"):
                cc_func = self.update_osc2_amp
            elif (param == "width"):
                cc_func = self.update_osc2_width
        elif (module == "filter"):
            if (param == "cutoff"):
                cc_func = self.update_filt_freq
            elif (param == "feedback"):
                cc_func = self.update_filt_res
            elif (param == "drive"):
                cc_func = self.update_filt_drive
            elif (param == "saturate"):
                cc_func = self.update_filt_sat
        elif (module == "filter env"):
            if (param == "attack"):
                cc_func = self.update_fenv_attack
            elif (param == "decay"):
                cc_func = self.update_fenv_decay
            elif (param == "sustain"):
                cc_func = self.update_fenv_sustain
            elif (param == "release"):
                cc_func = self.update_fenv_release
            elif (param == "depth"):
                cc_func = self.update_fenv_amount
        elif (module == "envelope"):
            if (param == "attack"):
                cc_func = self.update_env_attack
            elif (param == "decay"):
                cc_func = self.update_env_decay
            elif (param == "sustain"):
                cc_func = self.update_env_sustain
            elif (param == "release"):
                cc_func = self.update_env_release
        return cc_func

    #slots
    # midi
    def update_midi_in(self, input_name):
        self.engine.set_midi_input(input_name)

    def update_midi_ch(self, channel):
        self.engine.set_midi_channel(int(channel))

    def toggle_midi_box(self, state):
        self.midi_group.setVisible(state)

    def refresh_midi_ins(self):
        self.midi_select.clear()
        input_list = self.engine.get_midi_inputs()
        if input_list:
            self.midi_select.addItems(input_list)
            self.midi_select.setCurrentIndex(0)

    def add_cc(self):
        new_cc = MIDIControl()
        cc_val = new_cc.cc_select.value()
        cc_param = new_cc.param_select.currentText()
        module = new_cc.module_select.currentText()
        cc_func = self.assign_cc_function(module, cc_param)
        self.engine.midi_cc_dict.update({cc_val: cc_func})
        rows = self.cc_rows + 1
        new_cc.row = rows
        self.cc_rows += 1
        self.cc_stack.addWidget(new_cc, rows, 0)
        new_cc.cc_changed.connect(self.update_cc)
        new_cc.param_changed.connect(self.update_param)
        new_cc.cc_deleted.connect(self.delete_cc)

    def update_cc(self, new_cc, old_cc, param):
        print(f"DEBUG: new cc: {new_cc}, old cc: {old_cc}, parameter: {param}")

    def update_param(self, cc, new_param):
        print(f"DEBUG: cc: {cc}, new parameter: {new_param}")

    def delete_cc(self, cc, row):
        if cc in self.engine.midi_cc_dict:
            self.engine.midi_cc_dict.pop(cc)
        print(f"DEBUG: delete row {row}")
        cc_widget = self.cc_stack.itemAtPosition(row, 0).widget()
        cc_widget.cc_changed.disconnect(self.delete_cc)
        cc_widget.param_changed.disconnect(self.delete_cc)
        cc_widget.cc_deleted.disconnect(self.delete_cc)
        if (row != self.cc_rows):
            for cc_index in range (row + 1, self.cc_rows + 1):
                print(cc_index)
                cc_control = self.cc_stack.itemAtPosition(cc_index, 0).widget()
                self.cc_stack.removeWidget(cc_control)
                self.cc_stack.addWidget(cc_control, cc_index - 1, 0)
                print(f"DEBUG: old row: {cc_control.row}")
                cc_control.row -= 1
                print(f"DEBUG: new row: {cc_control.row}")
        self.cc_stack.removeWidget(cc_widget)
        self.cc_rows -= 1
        cc_widget.deleteLater()


    # filter
    def update_filt_freq(self, newFreq):
        self.engine.update_cutoff(newFreq)

    def update_filt_res(self, newRes):
        self.engine.update_resonance(newRes)

    def update_filt_drive(self, newDrive):
        self.engine.update_drive(newDrive)

    def update_filt_sat(self, newSat):
        self.engine.update_saturate(newSat)

    def update_filt_alg(self, text):
        if (text == "low"):
            newAlg = 0.0
        elif (text == "high"):
            newAlg = 1.0
        elif (text == "band"):
            newAlg = 2.0
        elif (text == "notch"):
            newAlg = 3.0
        self.engine.update_type(newAlg)
        
    # oscillator 1
    def update_osc_freq(self, value):
        self.engine.update_pitch(value, 1)

    def update_osc_amp(self, value):
        self.engine.update_amplitude(value, 1)

    def update_osc_width(self, value):
        self.engine.update_width(value, 1)

    def update_osc_alg(self, text):
        if (text == "sine"):
            newAlg = 0.0
        elif (text == "saw"):
            newAlg = 1.0
        elif (text == "pulse"):
            newAlg = 2.0
        self.engine.update_algorithm(newAlg, 1)

    # oscillator 2
    def update_osc2_freq(self, value):
        self.engine.update_pitch(value, 2)

    def update_osc2_det(self, value):
        self.engine.update_detune(value)

    def update_osc2_amp(self, value):
        self.engine.update_amplitude(value, 2)

    def update_osc2_width(self, value):
        self.engine.update_width(value, 2)

    def update_osc2_alg(self, text):
        if (text == "sine"):
            newAlg = 0.0
        elif (text == "saw"):
            newAlg = 1.0
        elif (text == "pulse"):
            newAlg = 2.0
        self.engine.update_algorithm(newAlg, 2)

    # envelope
    def update_env_attack(self, value):
        att = float(value)/1000.0
        self.adsr_att_display.display(f"{att:.2f}")
        self.engine.update_attack(att)

    def update_env_decay(self, value):
        dec = float(value)/1000.0
        self.adsr_dec_display.display(f"{dec:.2f}")
        self.engine.update_decay(dec)

    def update_env_sustain(self, value):
        sus = float(value)/1000.0
        self.adsr_sus_display.display(f"{sus:.2f}")
        self.engine.update_sustain(sus)

    def update_env_release(self, value):
        rel = float(value)/1000.0
        self.adsr_rel_display.display(f"{rel:.2f}")
        self.engine.update_release(rel)
    
    def update_gate(self, checked):
        self.engine.update_gate(checked)

    # filter envelope
    def update_fenv_attack(self, value):
        att = float(value)/1000.0
        self.fenv_att_display.display(f"{att:.2f}")
        self.engine.update_fenv_attack(att)

    def update_fenv_decay(self, value):
        dec = float(value)/1000.0
        self.fenv_dec_display.display(f"{dec:.2f}")
        self.engine.update_fenv_decay(dec)

    def update_fenv_sustain(self, value):
        sus = float(value)/1000.0
        self.fenv_sus_display.display(f"{sus:.2f}")
        self.engine.update_fenv_sustain(sus)

    def update_fenv_release(self, value):
        rel = float(value)/1000.0
        self.fenv_rel_display.display(f"{rel:.2f}")
        self.engine.update_fenv_release(rel)
    
    def update_fenv_amount(self, value):
        amt = float(value)/100.0
        self.fenv_amt_display.display(f"{amt:.2f}")
        self.engine.update_fenv_amount(amt)

    def keyPressEvent(self, event):
        if (event.isAutoRepeat()):
            return
        else:
            offset = key_conv.key_offset(event.key())
            if (offset is not None):
                if (offset < 18):
                    key_text = event.text()
                    print(f"pressed key: {key_text}, offset: {offset}")
                    #set pitch
                    note = 3 + 12*self.engine.octave + offset
                    self.engine.key_pressed(note, 127)
                    return super().keyPressEvent(event)
                else:
                    if (offset == 18):
                        if (self.engine.octave < 5):
                            self.engine.octave += 1
                    elif (offset == 19):
                        if (self.engine.octave > -5):
                            self.engine.octave -= 1
            else:
                print(f"DEBUG: key: {event.text()}, value: {event.key()}")
    
    def keyReleaseEvent(self, event):
        if (event.isAutoRepeat()):
            return
        else:
            offset = key_conv.key_offset(event.key())
            if (offset is not None):
                if (offset < 18):
                    key_text = event.text()
                    print(f"released key: {key_text}, offset: {offset}")
                    #release gate
                    note = 3 + 12*self.engine.octave + offset
                    self.engine.key_released(note)

    def closeEvent(self, event):
        self.engine.close()
        return super().closeEvent(event)
