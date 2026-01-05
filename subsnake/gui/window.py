from subsnake.audio.engine import AudioEngine
from subsnake.gui.keys import Keys
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QMainWindow, QGridLayout,
    QSlider, QRadioButton,
    QLabel, QVBoxLayout,
    QHBoxLayout, QWidget,
    QButtonGroup, QPushButton,
    QGroupBox, QComboBox,
    QToolBar, QFrame)

key_conv = Keys()

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

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
        self.osc_grid = QGridLayout()
        osc_buttons = QHBoxLayout()
        midi_layout = QHBoxLayout()
        self.filt_grid = QGridLayout()
        filt_buttons = QHBoxLayout()
        self.env_grid = QGridLayout()
        self.window_grid = QGridLayout()

        #group boxes
        self.midi_group = QGroupBox("midi input")
        filt_group = QGroupBox("filter")
        osc_group = QGroupBox("oscillator")
        env_group = QGroupBox("envelope")
        self.midi_group.hide()

        #labels
        self.midi_input_label = QLabel("device:")
        self.midi_channel_label = QLabel("channel:")
        self.midi_input_label.setAlignment(Qt.AlignCenter)
        self.midi_channel_label.setAlignment(Qt.AlignCenter)

        self.filt_freq_label = QLabel("cutoff:")
        self.filt_res_label = QLabel("feedback:")
        self.filt_drive_label = QLabel("drive:")
        self.filt_sat_label = QLabel("saturate:")
        self.filt_alg_label = QLabel("type:")

        self.osc_freq_label = QLabel("pitch:")
        self.osc_amp_label = QLabel("level:")
        self.osc_width_label = QLabel("width:")
        self.osc_alg_label = QLabel("shape:")

        self.adsr_att_label = QLabel("attack:")
        self.adsr_dec_label = QLabel("decay:")
        self.adsr_sus_label = QLabel("sustain:")
        self.adsr_rel_label = QLabel("release:")
        self.adsr_gate_label = QLabel("gate:")

        #sliders
        self.filt_freq_slider = QSlider(Qt.Horizontal)
        self.filt_freq_slider.setSingleStep(1)
        self.filt_freq_slider.setRange(0, 800)
        self.filt_freq_slider.setValue(700)

        self.filt_res_slider = QSlider(Qt.Horizontal)
        self.filt_res_slider.setSingleStep(1)
        self.filt_res_slider.setRange(0, 200)
        self.filt_res_slider.setValue(0)

        self.filt_drive_slider = QSlider(Qt.Horizontal)
        self.filt_drive_slider.setSingleStep(1)
        self.filt_drive_slider.setRange(1, 360)
        self.filt_drive_slider.setValue(40)

        self.filt_sat_slider = QSlider(Qt.Horizontal)
        self.filt_sat_slider.setSingleStep(1)
        self.filt_sat_slider.setRange(100, 1200)
        self.filt_sat_slider.setValue(800)

        self.osc_freq_slider = QSlider(Qt.Horizontal)
        self.osc_freq_slider.setSingleStep(1)
        self.osc_freq_slider.setRange(-500, 500)
        self.osc_freq_slider.setValue(0)

        self.osc_amp_slider = QSlider(Qt.Horizontal)
        self.osc_amp_slider.setSingleStep(1)
        self.osc_amp_slider.setRange(0, 500)
        self.osc_amp_slider.setValue(250)

        self.osc_width_slider = QSlider(Qt.Horizontal)
        self.osc_width_slider.setSingleStep(1)
        self.osc_width_slider.setRange(0, 500)
        self.osc_width_slider.setValue(250)

        self.adsr_att_slider = QSlider(Qt.Horizontal)
        self.adsr_att_slider.setSingleStep(1)
        self.adsr_att_slider.setRange(1, 1000)
        self.adsr_att_slider.setValue(10)

        self.adsr_dec_slider = QSlider(Qt.Horizontal)
        self.adsr_dec_slider.setSingleStep(1)
        self.adsr_dec_slider.setRange(1, 1000)
        self.adsr_dec_slider.setValue(500)

        self.adsr_sus_slider = QSlider(Qt.Horizontal)
        self.adsr_sus_slider.setSingleStep(1)
        self.adsr_sus_slider.setRange(1, 1000)
        self.adsr_sus_slider.setValue(500)

        self.adsr_rel_slider = QSlider(Qt.Horizontal)
        self.adsr_rel_slider.setSingleStep(1)
        self.adsr_rel_slider.setRange(1, 1000)
        self.adsr_rel_slider.setValue(500)

        #radio buttons
        self.osc_alg_sin = QRadioButton("sine")
        self.osc_alg_saw = QRadioButton("saw")
        self.osc_alg_pulse = QRadioButton("pulse")
        self.osc_alg_pulse.setChecked(True)

        self.filt_alg_low = QRadioButton("low")
        self.filt_alg_high = QRadioButton("high")
        self.filt_alg_band = QRadioButton("band")
        self.filt_alg_notch = QRadioButton("notch")
        self.filt_alg_low.setChecked(True)

        #button groups
        self.osc_alg_group = QButtonGroup()
        self.osc_alg_group.addButton(self.osc_alg_sin)
        self.osc_alg_group.addButton(self.osc_alg_saw)
        self.osc_alg_group.addButton(self.osc_alg_pulse)

        self.filt_alg_group = QButtonGroup()
        self.filt_alg_group.addButton(self.filt_alg_low)
        self.filt_alg_group.addButton(self.filt_alg_high)
        self.filt_alg_group.addButton(self.filt_alg_band)
        self.filt_alg_group.addButton(self.filt_alg_notch)

        #combo boxes (midi)
        self.midi_select = QComboBox()
        self.midi_select.setEditable(False)
        self.midi_select.setInsertPolicy(QComboBox.InsertAtBottom)

        self.channel_select = QComboBox()
        self.midi_select.setEditable(False)
        self.midi_select.setInsertPolicy(QComboBox.InsertAtBottom)

        #refresh button
        self.midi_refresh = QPushButton("⟳")
        self.midi_refresh.setCheckable(False)

        #grid spacers
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
        filt_group.setObjectName("filt_group")
        osc_group.setObjectName("osc_group")
        env_group.setObjectName("env_group")
        self.midi_refresh.setObjectName("midi_refresh")

        #add labels
        self.filt_grid.addWidget(self.filt_freq_label, 0, 0)
        self.filt_grid.addWidget(self.filt_res_label, 1, 0)
        self.filt_grid.addWidget(self.filt_drive_label, 2, 0)
        self.filt_grid.addWidget(self.filt_sat_label, 3, 0)
        self.filt_grid.addWidget(self.filt_alg_label, 4, 0)

        self.osc_grid.addWidget(self.osc_freq_label, 0, 0)
        self.osc_grid.addWidget(self.osc_amp_label, 1, 0)
        self.osc_grid.addWidget(self.osc_width_label, 2, 0)
        self.osc_grid.addWidget(self.osc_alg_label, 3, 0)

        self.env_grid.addWidget(self.adsr_att_label, 0, 0)
        self.env_grid.addWidget(self.adsr_dec_label, 1, 0)
        self.env_grid.addWidget(self.adsr_sus_label, 2, 0)
        self.env_grid.addWidget(self.adsr_rel_label, 3, 0)
        self.env_grid.addWidget(self.adsr_gate_label, 4, 0)

        #add sliders
        self.filt_grid.addWidget(self.filt_freq_slider, 0, 1)
        self.filt_grid.addWidget(self.filt_res_slider, 1, 1)
        self.filt_grid.addWidget(self.filt_drive_slider, 2, 1)
        self.filt_grid.addWidget(self.filt_sat_slider, 3, 1)

        self.osc_grid.addWidget(self.osc_freq_slider, 0, 1)
        self.osc_grid.addWidget(self.osc_amp_slider, 1, 1)
        self.osc_grid.addWidget(self.osc_width_slider, 2, 1)

        self.env_grid.addWidget(self.adsr_att_slider, 0, 1)
        self.env_grid.addWidget(self.adsr_dec_slider, 1, 1)
        self.env_grid.addWidget(self.adsr_sus_slider, 2, 1)
        self.env_grid.addWidget(self.adsr_rel_slider, 3, 1)

        #add gate control
        self.env_gate = QPushButton("latch")
        self.env_gate.setObjectName("env_gate")
        self.env_gate.setCheckable(True)
        self.env_grid.addWidget(self.env_gate, 4, 1)

        #add radio buttons
        filt_buttons.addStretch()
        filt_buttons.addWidget(self.filt_alg_low)
        filt_buttons.addStretch()
        filt_buttons.addWidget(self.filt_alg_high)
        filt_buttons.addStretch()
        filt_buttons.addWidget(self.filt_alg_band)
        filt_buttons.addStretch()
        filt_buttons.addWidget(self.filt_alg_notch)
        filt_buttons.addStretch()
        self.filt_grid.addLayout(filt_buttons, 4, 1)

        osc_buttons.addStretch()
        osc_buttons.addWidget(self.osc_alg_sin)
        osc_buttons.addStretch()
        osc_buttons.addWidget(self.osc_alg_saw)
        osc_buttons.addStretch()
        osc_buttons.addWidget(self.osc_alg_pulse)
        osc_buttons.addStretch()
        self.osc_grid.addLayout(osc_buttons, 3, 1)

        #add labels & combo boxes (midi)
        midi_layout.addWidget(self.midi_refresh)
        midi_layout.addWidget(self.midi_input_label)
        midi_layout.addWidget(self.midi_select)
        midi_layout.addWidget(self.midi_channel_label)
        midi_layout.addWidget(self.channel_select)

        #add layouts to groups
        self.midi_group.setLayout(midi_layout)
        self.midi_group.setMaximumHeight(120)
        filt_group.setLayout(self.filt_grid)
        osc_group.setLayout(self.osc_grid)
        env_group.setLayout(self.env_grid)

        #add groups/midi to window
        self.window_grid.addWidget(self.grid_space_2, 0, 0)
        self.window_grid.addWidget(osc_group, 0, 1)
        self.window_grid.addWidget(self.grid_space_0, 0, 2)
        self.window_grid.addWidget(filt_group, 0, 3)
        self.window_grid.addWidget(self.grid_space_1, 0, 4)
        self.window_grid.addWidget(env_group, 0, 5)
        self.window_grid.addWidget(self.grid_space_3, 0, 6)
        self.window_grid.addWidget(self.midi_group, 1, 1)

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
        self.toggle_midi.toggled.connect(self.toggle_midi_box)

        self.filt_freq_slider.valueChanged.connect(self.update_filt_freq)
        self.filt_res_slider.valueChanged.connect(self.update_filt_res)
        self.filt_drive_slider.valueChanged.connect(self.update_filt_drive)
        self.filt_sat_slider.valueChanged.connect(self.update_filt_sat)
        self.filt_alg_group.buttonClicked.connect(self.update_filt_alg)

        self.osc_freq_slider.valueChanged.connect(self.update_osc_freq)
        self.osc_amp_slider.valueChanged.connect(self.update_osc_amp)
        self.osc_width_slider.valueChanged.connect(self.update_osc_width)
        self.osc_alg_group.buttonClicked.connect(self.update_osc_alg)

        self.adsr_att_slider.valueChanged.connect(self.update_env_attack)
        self.adsr_dec_slider.valueChanged.connect(self.update_env_decay)
        self.adsr_sus_slider.valueChanged.connect(self.update_env_sustain)
        self.adsr_rel_slider.valueChanged.connect(self.update_env_release)

        self.env_gate.clicked.connect(self.update_gate)

        self.setCentralWidget(window_widget)
    
    #slots
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

    def update_filt_freq(self, value):
        newFreq = 27.5 * 2**(float(value)/100.0)
        self.engine.update_cutoff(newFreq)

    def update_filt_res(self, value):
        newRes = 10.0 / (10.0**(value/100.0))
        self.engine.update_resonance(newRes)

    def update_filt_drive(self, value):
        newDrive = value/40.0
        self.engine.update_drive(newDrive)

    def update_filt_sat(self, value):
        newSat = float(value)/100.0
        self.engine.update_saturate(newSat)

    def update_filt_alg(self, button):
        text = button.text()
        if (text == "low"):
            newAlg = 0.0
        elif (text == "high"):
            newAlg = 1.0
        elif (text == "band"):
            newAlg = 2.0
        elif (text == "notch"):
            newAlg = 3.0
        self.engine.update_type(newAlg)
        

    def update_osc_freq(self, value):
        offset = float(value)/100.0
        self.engine.update_pitch(offset)

    def update_osc_amp(self, value):
        newAmp = float(value)/500.0
        self.engine.update_amplitude(newAmp)

    def update_osc_width(self, value):
        newWidth = float(value)/500.0
        self.engine.update_width(newWidth)

    def update_osc_alg(self, button):
        text = button.text()
        if (text == "sine"):
            newAlg = 0.0
        elif (text == "saw"):
            newAlg = 1.0
        elif (text == "pulse"):
            newAlg = 2.0
        self.engine.update_algorithm(newAlg)


    def update_env_attack(self, value):
        att = float(value)/1000.0
        self.engine.update_attack(att)

    def update_env_decay(self, value):
        dec = float(value)/100.0
        self.engine.update_decay(dec)

    def update_env_sustain(self, value):
        sus = float(value)/1000.0
        self.engine.update_sustain(sus)

    def update_env_release(self, value):
        rel = float(value)/1000.0
        self.engine.update_release(rel)
    
    def update_gate(self, checked):
        self.engine.update_gate(checked)


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
                    note = 3 + 12.0*self.engine.octave + offset
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
                    note = 3 + 12.0*self.engine.octave + offset
                    self.engine.key_released(note)

    def closeEvent(self, event):
        self.engine.close()
        return super().closeEvent(event)
