from subsnake.audio.engine import AudioEngine
from subsnake.gui.keys import Keys
from subsnake.gui.midi_control import MIDIControl
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
        self.osc2_grid = QGridLayout()
        osc_buttons = QHBoxLayout()
        osc2_buttons = QHBoxLayout()
        midi_layout = QGridLayout()
        midi_stack = QGridLayout()
        self.filt_grid = QGridLayout()
        filt_buttons = QHBoxLayout()
        self.env_grid = QGridLayout()
        self.fenv_grid = QGridLayout()
        self.window_grid = QGridLayout()

        #group boxes
        self.midi_group = QGroupBox("midi input")
        self.midi_group.setFocusPolicy(Qt.NoFocus)
        filt_group = QGroupBox("filter")
        osc_group = QGroupBox("oscillator 1")
        osc2_group = QGroupBox("oscillator 2")
        env_group = QGroupBox("envelope")
        fenv_group = QGroupBox("filter envelope")
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

        self.osc2_freq_label = QLabel("pitch:")
        self.osc2_det_label = QLabel("detune:")
        self.osc2_amp_label = QLabel("level:")
        self.osc2_width_label = QLabel("width:")
        self.osc2_alg_label = QLabel("shape:")

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

        #sliders
        # filter
        self.filt_freq_slider = QSlider(Qt.Horizontal)
        self.filt_freq_slider.setSingleStep(1)
        self.filt_freq_slider.setRange(0, 800)

        self.filt_res_slider = QSlider(Qt.Horizontal)
        self.filt_res_slider.setSingleStep(1)
        self.filt_res_slider.setRange(0, 200)
        self.filt_res_slider.setValue(1)

        self.filt_drive_slider = QSlider(Qt.Horizontal)
        self.filt_drive_slider.setSingleStep(1)
        self.filt_drive_slider.setRange(1, 360)

        self.filt_sat_slider = QSlider(Qt.Horizontal)
        self.filt_sat_slider.setSingleStep(1)
        self.filt_sat_slider.setRange(100, 1200)

        # oscillator 1
        self.osc_freq_slider = QSlider(Qt.Horizontal)
        self.osc_freq_slider.setSingleStep(1)
        self.osc_freq_slider.setRange(-500, 500)
        self.osc_freq_slider.setValue(1)

        self.osc_amp_slider = QSlider(Qt.Horizontal)
        self.osc_amp_slider.setSingleStep(1)
        self.osc_amp_slider.setRange(0, 500)

        self.osc_width_slider = QSlider(Qt.Horizontal)
        self.osc_width_slider.setSingleStep(1)
        self.osc_width_slider.setRange(0, 500)

        # oscillator 2
        self.osc2_freq_slider = QSlider(Qt.Horizontal)
        self.osc2_freq_slider.setSingleStep(1)
        self.osc2_freq_slider.setRange(-200, 200)
        self.osc2_freq_slider.setValue(1)

        self.osc2_det_slider = QSlider(Qt.Horizontal)
        self.osc2_det_slider.setSingleStep(1)
        self.osc2_det_slider.setRange(-200, 200)
        self.osc2_det_slider.setValue(1)

        self.osc2_amp_slider = QSlider(Qt.Horizontal)
        self.osc2_amp_slider.setSingleStep(1)
        self.osc2_amp_slider.setRange(0, 500)

        self.osc2_width_slider = QSlider(Qt.Horizontal)
        self.osc2_width_slider.setSingleStep(1)
        self.osc2_width_slider.setRange(0, 500)


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
        # args: QLCDDisplay widget, # of digits, mode (hex, dec, oct, bin),
        # dig_style (outline, filled, flat), small decimal flag (for floats)
        self.osc_freq_display = self.configure_display(QLCDNumber(), 3, QLCDNumber.Dec, QLCDNumber.Flat, True)
        self.osc_amp_display = self.configure_display(QLCDNumber(), 3, QLCDNumber.Dec, QLCDNumber.Flat, True)
        self.osc_width_display = self.configure_display(QLCDNumber(), 3, QLCDNumber.Dec, QLCDNumber.Flat, True)

        self.osc2_freq_display = self.configure_display(QLCDNumber(), 3, QLCDNumber.Dec, QLCDNumber.Flat, True)
        self.osc2_det_display = self.configure_display(QLCDNumber(), 3, QLCDNumber.Dec, QLCDNumber.Flat, True)
        self.osc2_amp_display = self.configure_display(QLCDNumber(), 3, QLCDNumber.Dec, QLCDNumber.Flat, True)
        self.osc2_width_display = self.configure_display(QLCDNumber(), 3, QLCDNumber.Dec, QLCDNumber.Flat, True)

        self.filt_freq_display = self.configure_display(QLCDNumber(), 5, QLCDNumber.Dec, QLCDNumber.Flat, True)
        self.filt_fback_display = self.configure_display(QLCDNumber(), 5, QLCDNumber.Dec, QLCDNumber.Flat, True)
        self.filt_drive_display = self.configure_display(QLCDNumber(), 5, QLCDNumber.Dec, QLCDNumber.Flat, True)
        self.filt_sat_display = self.configure_display(QLCDNumber(), 5, QLCDNumber.Dec, QLCDNumber.Flat, True)

        self.adsr_att_display = self.configure_display(QLCDNumber(), 3, QLCDNumber.Dec, QLCDNumber.Flat, True)
        self.adsr_dec_display = self.configure_display(QLCDNumber(), 3, QLCDNumber.Dec, QLCDNumber.Flat, True)
        self.adsr_sus_display = self.configure_display(QLCDNumber(), 3, QLCDNumber.Dec, QLCDNumber.Flat, True)
        self.adsr_rel_display = self.configure_display(QLCDNumber(), 3, QLCDNumber.Dec, QLCDNumber.Flat, True)

        self.fenv_att_display = self.configure_display(QLCDNumber(), 3, QLCDNumber.Dec, QLCDNumber.Flat, True)
        self.fenv_dec_display = self.configure_display(QLCDNumber(), 3, QLCDNumber.Dec, QLCDNumber.Flat, True)
        self.fenv_sus_display = self.configure_display(QLCDNumber(), 3, QLCDNumber.Dec, QLCDNumber.Flat, True)
        self.fenv_rel_display = self.configure_display(QLCDNumber(), 3, QLCDNumber.Dec, QLCDNumber.Flat, True)
        self.fenv_amt_display = self.configure_display(QLCDNumber(), 3, QLCDNumber.Dec, QLCDNumber.Flat, True)

        #set display palettes
        self.set_palette(self.osc_freq_display, 0)
        self.set_palette(self.osc_amp_display, 0)
        self.set_palette(self.osc_width_display, 0)

        self.set_palette(self.osc2_freq_display, 3)
        self.set_palette(self.osc2_det_display, 3)
        self.set_palette(self.osc2_amp_display, 3)
        self.set_palette(self.osc2_width_display, 3)

        self.set_palette(self.filt_freq_display, 1)
        self.set_palette(self.filt_fback_display, 1)
        self.set_palette(self.filt_drive_display, 1)
        self.set_palette(self.filt_sat_display, 1)

        self.set_palette(self.adsr_att_display, 2)
        self.set_palette(self.adsr_dec_display, 2)
        self.set_palette(self.adsr_sus_display, 2)
        self.set_palette(self.adsr_rel_display, 2)

        self.set_palette(self.fenv_att_display, 2)
        self.set_palette(self.fenv_dec_display, 2)
        self.set_palette(self.fenv_sus_display, 2)
        self.set_palette(self.fenv_rel_display, 2)
        self.set_palette(self.fenv_amt_display, 2)

        #radio buttons
        self.osc_alg_sin = QRadioButton("sine")
        self.osc_alg_saw = QRadioButton("saw")
        self.osc_alg_pulse = QRadioButton("pulse")
        self.osc_alg_pulse.setChecked(True)

        self.osc2_alg_sin = QRadioButton("sine")
        self.osc2_alg_saw = QRadioButton("saw")
        self.osc2_alg_pulse = QRadioButton("pulse")
        self.osc2_alg_pulse.setChecked(True)

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

        self.osc2_alg_group = QButtonGroup()
        self.osc2_alg_group.addButton(self.osc2_alg_sin)
        self.osc2_alg_group.addButton(self.osc2_alg_saw)
        self.osc2_alg_group.addButton(self.osc2_alg_pulse)

        self.filt_alg_group = QButtonGroup()
        self.filt_alg_group.addButton(self.filt_alg_low)
        self.filt_alg_group.addButton(self.filt_alg_high)
        self.filt_alg_group.addButton(self.filt_alg_band)
        self.filt_alg_group.addButton(self.filt_alg_notch)

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

        # row 1
        #   add if needed

        #object names
        self.grid_space_0.setObjectName("grid_space_0")
        self.grid_space_1.setObjectName("grid_space_1")
        self.grid_space_2.setObjectName("grid_space_2")
        self.grid_space_3.setObjectName("grid_space_3")
        self.midi_group.setObjectName("midi_group")
        filt_group.setObjectName("filt_group")
        osc_group.setObjectName("osc_group")
        osc2_group.setObjectName("osc2_group")
        env_group.setObjectName("env_group")
        fenv_group.setObjectName("fenv_group")
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

        self.osc2_grid.addWidget(self.osc2_freq_label, 0, 0)
        self.osc2_grid.addWidget(self.osc2_det_label, 1, 0)
        self.osc2_grid.addWidget(self.osc2_amp_label, 2, 0)
        self.osc2_grid.addWidget(self.osc2_width_label, 3, 0)
        self.osc2_grid.addWidget(self.osc2_alg_label, 4, 0)

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

        #add sliders
        self.filt_grid.addWidget(self.filt_freq_slider, 0, 1)
        self.filt_grid.addWidget(self.filt_res_slider, 1, 1)
        self.filt_grid.addWidget(self.filt_drive_slider, 2, 1)
        self.filt_grid.addWidget(self.filt_sat_slider, 3, 1)

        self.osc_grid.addWidget(self.osc_freq_slider, 0, 1)
        self.osc_grid.addWidget(self.osc_amp_slider, 1, 1)
        self.osc_grid.addWidget(self.osc_width_slider, 2, 1)

        self.osc2_grid.addWidget(self.osc2_freq_slider, 0, 1)
        self.osc2_grid.addWidget(self.osc2_det_slider, 1, 1)
        self.osc2_grid.addWidget(self.osc2_amp_slider, 2, 1)
        self.osc2_grid.addWidget(self.osc2_width_slider, 3, 1)

        self.env_grid.addWidget(self.adsr_att_slider, 0, 1)
        self.env_grid.addWidget(self.adsr_dec_slider, 1, 1)
        self.env_grid.addWidget(self.adsr_sus_slider, 2, 1)
        self.env_grid.addWidget(self.adsr_rel_slider, 3, 1)

        self.fenv_grid.addWidget(self.fenv_att_slider, 0, 1)
        self.fenv_grid.addWidget(self.fenv_dec_slider, 1, 1)
        self.fenv_grid.addWidget(self.fenv_sus_slider, 2, 1)
        self.fenv_grid.addWidget(self.fenv_rel_slider, 3, 1)
        self.fenv_grid.addWidget(self.fenv_amt_slider, 4, 1)

        #add displays
        self.filt_grid.addWidget(self.filt_freq_display, 0, 2)
        self.filt_grid.addWidget(self.filt_fback_display, 1, 2)
        self.filt_grid.addWidget(self.filt_drive_display, 2, 2)
        self.filt_grid.addWidget(self.filt_sat_display, 3, 2)

        self.osc_grid.addWidget(self.osc_freq_display, 0, 2)
        self.osc_grid.addWidget(self.osc_amp_display, 1, 2)
        self.osc_grid.addWidget(self.osc_width_display, 2, 2)

        self.osc2_grid.addWidget(self.osc2_freq_display, 0, 2)
        self.osc2_grid.addWidget(self.osc2_det_display, 1, 2)
        self.osc2_grid.addWidget(self.osc2_amp_display, 2, 2)
        self.osc2_grid.addWidget(self.osc2_width_display, 3, 2)

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

        osc2_buttons.addStretch()
        osc2_buttons.addWidget(self.osc2_alg_sin)
        osc2_buttons.addStretch()
        osc2_buttons.addWidget(self.osc2_alg_saw)
        osc2_buttons.addStretch()
        osc2_buttons.addWidget(self.osc2_alg_pulse)
        osc2_buttons.addStretch()
        self.osc2_grid.addLayout(osc2_buttons, 4, 1)

        #add labels & combo boxes (midi)
        test_control = MIDIControl()
        test_control.cc_changed.connect(self.update_cc)
        test_control.param_changed.connect(self.update_param)
        midi_layout.addWidget(self.midi_refresh, 0, 0)
        midi_layout.addWidget(self.midi_input_label, 0, 1)
        midi_layout.addWidget(self.midi_select, 0, 2)
        midi_layout.addWidget(self.midi_channel_label, 0, 3)
        midi_layout.addWidget(self.channel_select, 0, 4)
        midi_stack.addLayout(midi_layout, 0, 0)
        midi_stack.addWidget(test_control, 1, 0)

        #add layouts to groups
        self.midi_group.setLayout(midi_stack)
        filt_group.setLayout(self.filt_grid)
        osc_group.setLayout(self.osc_grid)
        osc2_group.setLayout(self.osc2_grid)
        env_group.setLayout(self.env_grid)
        fenv_group.setLayout(self.fenv_grid)

        #add groups/midi to window
        self.window_grid.addWidget(self.grid_space_2, 0, 0)
        self.window_grid.addWidget(osc_group, 0, 1)
        self.window_grid.addWidget(self.grid_space_0, 0, 2)
        self.window_grid.addWidget(filt_group, 0, 3)
        self.window_grid.addWidget(self.grid_space_1, 0, 4)
        self.window_grid.addWidget(env_group, 0, 5)
        self.window_grid.addWidget(self.grid_space_3, 0, 6)
        self.window_grid.addWidget(osc2_group, 1, 1)
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

        self.osc2_freq_slider.valueChanged.connect(self.update_osc2_freq)
        self.osc2_det_slider.valueChanged.connect(self.update_osc2_det)
        self.osc2_amp_slider.valueChanged.connect(self.update_osc2_amp)
        self.osc2_width_slider.valueChanged.connect(self.update_osc2_width)
        self.osc2_alg_group.buttonClicked.connect(self.update_osc2_alg)

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
        self.filt_freq_slider.setValue(700)
        self.filt_res_slider.setValue(0)
        self.filt_drive_slider.setValue(40)
        self.filt_sat_slider.setValue(800)

        self.osc_freq_slider.setValue(0)
        self.osc_amp_slider.setValue(250)
        self.osc_width_slider.setValue(250)

        self.osc2_freq_slider.setValue(0)
        self.osc2_det_slider.setValue(0)
        self.osc2_amp_slider.setValue(250)
        self.osc2_width_slider.setValue(250)

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
    # filter
    def update_filt_freq(self, value):
        newFreq = 27.5 * 2**(float(value)/100.0)
        self.filt_freq_display.display(f"{newFreq:.1f}")
        self.engine.update_cutoff(newFreq)

    def update_filt_res(self, value):
        newRes = 10.0 / (10.0**(value/100.0))
        self.filt_fback_display.display(f"{1.0/newRes:.2f}")
        self.engine.update_resonance(newRes)

    def update_filt_drive(self, value):
        newDrive = value/40.0
        self.filt_drive_display.display(f"{newDrive:.2f}")
        self.engine.update_drive(newDrive)

    def update_filt_sat(self, value):
        newSat = float(value)/100.0
        self.filt_sat_display.display(f"{newSat:.2f}")
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
        
    # oscillator 1
    def update_osc_freq(self, value):
        offset = float(value)/100.0
        self.osc_freq_display.display(f"{offset:.2f}")
        self.engine.update_pitch(offset, 1)

    def update_osc_amp(self, value):
        newAmp = float(value)/500.0
        self.osc_amp_display.display(f"{newAmp:.2f}")
        self.engine.update_amplitude(newAmp, 1)

    def update_osc_width(self, value):
        newWidth = float(value)/500.0
        self.osc_width_display.display(f"{newWidth:.2f}")
        self.engine.update_width(newWidth, 1)

    def update_osc_alg(self, button):
        text = button.text()
        if (text == "sine"):
            newAlg = 0.0
        elif (text == "saw"):
            newAlg = 1.0
        elif (text == "pulse"):
            newAlg = 2.0
        self.engine.update_algorithm(newAlg, 1)

    # oscillator 2
    def update_osc2_freq(self, value):
        offset = float(value)/100.0
        self.osc2_freq_display.display(f"{offset:.2f}")
        self.engine.update_pitch(offset, 2)

    def update_osc2_det(self, value):
        detune = value/20.0
        self.osc2_det_display.display(f"{detune:.2f}")
        self.engine.update_detune(detune)

    def update_osc2_amp(self, value):
        newAmp = float(value)/500.0
        self.osc2_amp_display.display(f"{newAmp:.2f}")
        self.engine.update_amplitude(newAmp, 2)

    def update_osc2_width(self, value):
        newWidth = float(value)/500.0
        self.osc2_width_display.display(f"{newWidth:.2f}")
        self.engine.update_width(newWidth, 2)

    def update_osc2_alg(self, button):
        text = button.text()
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

    def update_param(self, cc, new_param):
        print(f"DEBUG: cc: {cc}, new parameter: {new_param}")

    def update_cc(self, new_cc, old_cc, param):
        print(f"DEBUG: new cc: {new_cc}, old cc: {old_cc}, parameter: {param}")

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
