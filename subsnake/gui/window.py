from subsnake.audio.engine import AudioEngine
from subsnake.gui.keys import Keys
from subsnake.gui.osc_gui import OscillatorGUI
from subsnake.gui.osc2_gui import Oscillator2GUI
from subsnake.gui.filt_gui import FilterGUI
from subsnake.gui.env_gui import EnvelopeGUI
from subsnake.gui.fenv_gui import FilterEnvGUI
from subsnake.gui.midi import MIDISettings
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QMainWindow, QGridLayout,
    QFrame, QWidget,
    QToolBar)

key_conv = Keys()

class MainWindow(QMainWindow):

    def __init__(self, engine):
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
        self.window_grid = QGridLayout()

        #group boxes
        self.midi_group = MIDISettings()
        self.midi_group.setFocusPolicy(Qt.NoFocus)
        self.midi_group.hide()

        #module GUIs
        self.filt_group = FilterGUI()
        self.osc_group = OscillatorGUI()
        self.osc2_group = Oscillator2GUI()
        self.env_group = EnvelopeGUI()
        self.fenv_group = FilterEnvGUI()

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

        #add modules/midi groups to window
        self.window_grid.addWidget(self.grid_space_2, 0, 0)
        self.window_grid.addWidget(self.osc_group, 0, 1)
        self.window_grid.addWidget(self.grid_space_0, 0, 2)
        self.window_grid.addWidget(self.filt_group, 0, 3)
        self.window_grid.addWidget(self.grid_space_1, 0, 4)
        self.window_grid.addWidget(self.env_group, 0, 5)
        self.window_grid.addWidget(self.grid_space_3, 0, 6)
        self.window_grid.addWidget(self.osc2_group, 1, 1)
        self.window_grid.addWidget(self.fenv_group, 1, 3)
        self.window_grid.addWidget(self.midi_group, 2, 1)

        #set column spacing
        self.window_grid.setColumnMinimumWidth(5, 30)

        #set layout of window
        window_widget = QWidget()
        window_widget.setLayout(self.window_grid)

        #start audio engine
        self.engine = engine

        #connect signals
        self.midi_group.input_changed.connect(self.update_midi_in)
        self.midi_group.channel_changed.connect(self.update_midi_ch)
        self.midi_group.inputs_refreshed.connect(self.refresh_midi_ins)
        self.midi_group.cc_added.connect(self.add_cc)
        self.midi_group.cc_changed.connect(self.update_cc)
        self.midi_group.cc_param_changed.connect(self.update_param)
        self.midi_group.cc_deleted.connect(self.delete_cc)
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

        self.env_group.attack_changed.connect(self.update_env_attack)
        self.env_group.decay_changed.connect(self.update_env_decay)
        self.env_group.sustain_changed.connect(self.update_env_sustain)
        self.env_group.release_changed.connect(self.update_env_release)
        self.env_group.gate_changed.connect(self.update_env_gate)

        self.fenv_group.attack_changed.connect(self.update_fenv_attack)
        self.fenv_group.decay_changed.connect(self.update_fenv_decay)
        self.fenv_group.sustain_changed.connect(self.update_fenv_sustain)
        self.fenv_group.release_changed.connect(self.update_fenv_release)
        self.fenv_group.amount_changed.connect(self.update_fenv_amount)

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

        self.env_group.adsr_att_slider.setValue(10)
        self.env_group.adsr_dec_slider.setValue(500)
        self.env_group.adsr_sus_slider.setValue(1000)
        self.env_group.adsr_rel_slider.setValue(500)

        self.fenv_group.fenv_att_slider.setValue(10)
        self.fenv_group.fenv_dec_slider.setValue(500)
        self.fenv_group.fenv_sus_slider.setValue(1000)
        self.fenv_group.fenv_rel_slider.setValue(500)
        self.fenv_group.fenv_amt_slider.setValue(0)

    def assign_cc_function(self, module, param):
        cc_function = None
        if (module == "oscillator 1"):
            if (param == "pitch"):
                cc_function = self.engine.cc_change_pitch_1
            elif (param == "level"):
                cc_function = self.engine.cc_change_level_1
            elif (param == "width"):
                cc_function = self.engine.cc_change_width_1
        elif (module == "oscillator 2"):
            if (param == "pitch"):
                cc_function = self.engine.cc_change_pitch_2
            elif (param == "detune"):
                cc_function = self.engine.cc_change_detune_2
            elif (param == "level"):
                cc_function = self.engine.cc_change_level_2
            elif (param == "width"):
                cc_function = self.engine.cc_change_width_2
        elif (module == "filter"):
            if (param == "cutoff"):
                cc_function = self.engine.cc_change_cutoff
            elif (param == "feedback"):
                cc_function = self.engine.cc_change_resonance
            elif (param == "drive"):
                cc_function = self.engine.cc_change_drive
            elif (param == "saturate"):
                cc_function = self.engine.cc_change_saturate
        elif (module == "filter env"):
            if (param == "attack"):
                cc_function = self.engine.cc_change_fenv_attack
            elif (param == "decay"):
                cc_function = self.engine.cc_change_fenv_decay
            elif (param == "sustain"):
                cc_function = self.engine.cc_change_fenv_sustain
            elif (param == "release"):
                cc_function = self.engine.cc_change_fenv_release
            elif (param == "depth"):
                cc_function = self.engine.cc_change_fenv_amount
        elif (module == "envelope"):
            if (param == "attack"):
                cc_function = self.engine.cc_change_env_attack
            elif (param == "decay"):
                cc_function = self.engine.cc_change_env_decay
            elif (param == "sustain"):
                cc_function = self.engine.cc_change_env_sustain
            elif (param == "release"):
                cc_function = self.engine.cc_change_env_release
        return cc_function

    #slots
    # midi
    def update_midi_in(self, input_name):
        self.engine.set_midi_input(input_name)

    def update_midi_ch(self, channel):
        self.engine.set_midi_channel(channel)

    def toggle_midi_box(self, state):
        self.midi_group.setVisible(state)

    def refresh_midi_ins(self):
        self.midi_group.midi_select.clear()
        input_list = self.engine.get_midi_inputs()
        if input_list:
            self.midi_group.midi_select.addItems(input_list)
            self.midi_group.midi_select.setCurrentIndex(0)

    def add_cc(self, cc_val, cc_param, module):
        cc_function = self.assign_cc_function(module, cc_param)
        if cc_val not in self.engine.midi_cc_functions:
            self.engine.midi_cc_functions.update({cc_val: cc_function})

    def update_cc(self, new_cc, old_cc, param, module):
        if old_cc in self.engine.midi_cc_functions:
            self.engine.midi_cc_functions.pop(old_cc)
        if new_cc not in self.engine.midi_cc_functions:
            self.engine.midi_cc_functions.update({new_cc: self.assign_cc_function(module, param)})
            

    def update_param(self, cc, new_param, module):
        if cc in self.engine.midi_cc_functions:
            self.engine.midi_cc_functions.pop(cc)
        self.engine.midi_cc_functions.update({cc: self.assign_cc_function(module, new_param)})


    def delete_cc(self, cc):
        if cc in self.engine.midi_cc_functions:
            self.engine.midi_cc_functions.pop(cc)

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
        self.engine.update_pitch_1(value)

    def update_osc_amp(self, value):
        self.engine.update_amplitude_1(value)

    def update_osc_width(self, value):
        self.engine.update_width_1(value)

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
        self.engine.update_pitch_2(value)

    def update_osc2_det(self, value):
        self.engine.update_detune(value)

    def update_osc2_amp(self, value):
        self.engine.update_amplitude_2(value)

    def update_osc2_width(self, value):
        self.engine.update_width_2(value)

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
        self.engine.update_attack(value)

    def update_env_decay(self, value):
        self.engine.update_decay(value)

    def update_env_sustain(self, value):
        self.engine.update_sustain(value)

    def update_env_release(self, value):
        self.engine.update_release(value)
    
    def update_env_gate(self, checked):
        self.engine.update_gate(checked)

    # filter envelope
    def update_fenv_attack(self, value):
        self.engine.update_fenv_attack(value)

    def update_fenv_decay(self, value):
        self.engine.update_fenv_decay(value)

    def update_fenv_sustain(self, value):
        self.engine.update_fenv_sustain(value)

    def update_fenv_release(self, value):
        self.engine.update_fenv_release(value)
    
    def update_fenv_amount(self, value):
        self.engine.update_fenv_amount(value)

    def keyPressEvent(self, event):
        if (event.isAutoRepeat()):
            return
        else:
            offset = key_conv.key_offset(event.key())
            if (offset is not None):
                if (offset < 18):
                    key_text = event.text()
                    #set pitch
                    note = 12*self.engine.octave + offset + 60
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
                    #release gate
                    note = 12*self.engine.octave + offset + 60
                    self.engine.key_released(note)

    def closeEvent(self, event):
        self.engine.close()
        return super().closeEvent(event)
