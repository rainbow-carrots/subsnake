from subsnake.audio.engine import AudioEngine
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QMainWindow,
    QSlider, QRadioButton,
    QLabel, QVBoxLayout,
    QHBoxLayout, QWidget,
    QButtonGroup, QPushButton)

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        #layouts
        osc_labels = QVBoxLayout()
        osc_layout = QVBoxLayout()
        osc_buttons = QHBoxLayout()
        filt_labels = QVBoxLayout()
        filt_layout = QVBoxLayout()
        filt_buttons = QHBoxLayout()
        self.window_layout = QHBoxLayout()

        #labels
        self.filt_freq_label = QLabel("cutoff:")
        self.filt_res_label = QLabel("feedback:")
        self.filt_drive_label = QLabel("drive:")
        self.filt_alg_label = QLabel("type:")

        self.osc_freq_label = QLabel("pitch:")
        self.osc_amp_label = QLabel("level:")
        self.osc_width_label = QLabel("width:")
        self.osc_alg_label = QLabel("shape:")

        #sliders
        self.filt_freq_slider = QSlider(Qt.Horizontal)
        self.filt_freq_slider.setSingleStep(1)
        self.filt_freq_slider.setRange(0, 900)
        self.filt_freq_slider.setValue(700)

        self.filt_res_slider = QSlider(Qt.Horizontal)
        self.filt_res_slider.setSingleStep(1)
        self.filt_res_slider.setRange(0, 200)
        self.filt_res_slider.setValue(0)

        self.filt_drive_slider = QSlider(Qt.Horizontal)
        self.filt_drive_slider.setSingleStep(1)
        self.filt_drive_slider.setRange(1, 360)
        self.filt_drive_slider.setValue(40)

        self.osc_freq_slider = QSlider(Qt.Horizontal)
        self.osc_freq_slider.setSingleStep(1)
        self.osc_freq_slider.setRange(-500, 500)
        self.osc_freq_slider.setValue(-300)

        self.osc_amp_slider = QSlider(Qt.Horizontal)
        self.osc_amp_slider.setSingleStep(1)
        self.osc_amp_slider.setRange(0, 500)
        self.osc_amp_slider.setValue(250)

        self.osc_width_slider = QSlider(Qt.Horizontal)
        self.osc_width_slider.setSingleStep(1)
        self.osc_width_slider.setRange(0, 500)
        self.osc_width_slider.setValue(250)

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

        #add labels
        filt_labels.addWidget(self.filt_freq_label)
        filt_labels.addWidget(self.filt_res_label)
        filt_labels.addWidget(self.filt_drive_label)
        filt_labels.addWidget(self.filt_alg_label)

        osc_labels.addWidget(self.osc_freq_label)
        osc_labels.addWidget(self.osc_amp_label)
        osc_labels.addWidget(self.osc_width_label)
        osc_labels.addWidget(self.osc_alg_label)

        #add sliders
        filt_layout.addWidget(self.filt_freq_slider)
        filt_layout.addWidget(self.filt_res_slider)
        filt_layout.addWidget(self.filt_drive_slider)

        osc_layout.addWidget(self.osc_freq_slider)
        osc_layout.addWidget(self.osc_amp_slider)
        osc_layout.addWidget(self.osc_width_slider)

        #add radio buttons
        filt_buttons.addWidget(self.filt_alg_low)
        filt_buttons.addWidget(self.filt_alg_high)
        filt_buttons.addWidget(self.filt_alg_band)
        filt_buttons.addWidget(self.filt_alg_notch)
        filt_layout.addLayout(filt_buttons)

        osc_buttons.addWidget(self.osc_alg_sin)
        osc_buttons.addWidget(self.osc_alg_saw)
        osc_buttons.addWidget(self.osc_alg_pulse)
        osc_layout.addLayout(osc_buttons)

        #add layouts
        self.window_layout.addLayout(filt_labels)
        self.window_layout.addLayout(filt_layout)

        self.window_layout.addLayout(osc_labels)
        self.window_layout.addLayout(osc_layout)
        self.env_test = QPushButton("gate")
        self.env_test.setCheckable(True)
        self.window_layout.addWidget(self.env_test)

        #set layout of window
        window_widget = QWidget()
        window_widget.setLayout(self.window_layout)

        #start audio engine
        self.engine = AudioEngine()

        #connect signals
        self.filt_freq_slider.valueChanged.connect(self.update_filt_freq)
        self.filt_res_slider.valueChanged.connect(self.update_filt_res)
        self.filt_drive_slider.valueChanged.connect(self.update_filt_drive)
        self.filt_alg_group.buttonClicked.connect(self.update_filt_alg)

        self.osc_freq_slider.valueChanged.connect(self.update_osc_freq)
        self.osc_amp_slider.valueChanged.connect(self.update_osc_amp)
        self.osc_width_slider.valueChanged.connect(self.update_osc_width)
        self.osc_alg_group.buttonClicked.connect(self.update_osc_alg)

        self.env_test.clicked.connect(self.update_gate)

        self.setCentralWidget(window_widget)
    
    #slots
    def update_filt_freq(self, value):
        newFreq = 27.5 * 2**(float(value)/100.0)
        self.engine.filt.update_cutoff(newFreq)

    def update_filt_res(self, value):
        newRes = 10.0 / (10.0**(value/100.0))
        self.engine.filt.update_resonance(newRes)

    def update_filt_drive(self, value):
        newDrive = value/40.0
        self.engine.filt.update_drive(newDrive)

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
        self.engine.filt.update_type(newAlg)
        

    def update_osc_freq(self, value):
        newFreq = 440.0 * 2**(float(value)/100.0)
        self.engine.osc.update_pitch(newFreq)

    def update_osc_amp(self, value):
        newAmp = float(value)/500.0
        self.engine.osc.update_amplitude(newAmp)

    def update_osc_width(self, value):
        newWidth = float(value)/500.0
        self.engine.osc.update_width(newWidth)

    def update_osc_alg(self, button):
        text = button.text()
        if (text == "sine"):
            newAlg = 0.0
        elif (text == "saw"):
            newAlg = 1.0
        elif (text == "pulse"):
            newAlg = 2.0
        self.engine.osc.update_algorithm(newAlg)
    
    def update_gate(self, checked):
        self.engine.env.update_gate(checked)
