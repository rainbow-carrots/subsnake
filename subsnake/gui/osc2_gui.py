from PySide6.QtWidgets import(
    QSlider, QLabel, QGridLayout,
    QRadioButton, QButtonGroup, QLCDNumber,
    QHBoxLayout, QGroupBox
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QPalette, QColor

class Oscillator2GUI(QGroupBox):
    #signals
    pitch_changed = Signal(float)
    detune_changed = Signal(float)
    level_changed = Signal(float)
    width_changed = Signal(float)
    alg_changed = Signal(str)

    def __init__(self):
        super().__init__()
        #set title
        self.setTitle("oscillator 2")

        #layouts
        osc2_layout = QGridLayout()
        osc2_buttons = QHBoxLayout()

        #labels
        osc2_freq_label = QLabel("pitch:")
        osc2_det_label = QLabel("detune:")
        osc2_amp_label = QLabel("level:")
        osc2_width_label = QLabel("width:")
        osc2_alg_label = QLabel("shape:")

        #sliders
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

        #displays
        self.osc2_freq_display = self.configure_display(QLCDNumber(), 3, QLCDNumber.Dec, QLCDNumber.Flat, True)
        self.osc2_det_display = self.configure_display(QLCDNumber(), 3, QLCDNumber.Dec, QLCDNumber.Flat, True)
        self.osc2_amp_display = self.configure_display(QLCDNumber(), 3, QLCDNumber.Dec, QLCDNumber.Flat, True)
        self.osc2_width_display = self.configure_display(QLCDNumber(), 3, QLCDNumber.Dec, QLCDNumber.Flat, True)

        #set display palettes
        self.set_palette(self.osc2_freq_display)
        self.set_palette(self.osc2_det_display)
        self.set_palette(self.osc2_amp_display)
        self.set_palette(self.osc2_width_display)

        #radio buttons
        self.osc2_alg_sin = QRadioButton("sine")
        self.osc2_alg_saw = QRadioButton("saw")
        self.osc2_alg_pulse = QRadioButton("pulse")
        self.osc2_alg_pulse.setChecked(True)

        #button groups
        self.osc2_alg_group = QButtonGroup()
        self.osc2_alg_group.addButton(self.osc2_alg_sin)
        self.osc2_alg_group.addButton(self.osc2_alg_saw)
        self.osc2_alg_group.addButton(self.osc2_alg_pulse)

        #add labels
        osc2_layout.addWidget(osc2_freq_label, 0, 0)
        osc2_layout.addWidget(osc2_det_label, 1, 0)
        osc2_layout.addWidget(osc2_amp_label, 2, 0)
        osc2_layout.addWidget(osc2_width_label, 3, 0)
        osc2_layout.addWidget(osc2_alg_label, 4, 0)

        #add sliders
        osc2_layout.addWidget(self.osc2_freq_slider, 0, 1)
        osc2_layout.addWidget(self.osc2_det_slider, 1, 1)
        osc2_layout.addWidget(self.osc2_amp_slider, 2, 1)
        osc2_layout.addWidget(self.osc2_width_slider, 3, 1)

        #add displays
        osc2_layout.addWidget(self.osc2_freq_display, 0, 2)
        osc2_layout.addWidget(self.osc2_det_display, 1, 2)
        osc2_layout.addWidget(self.osc2_amp_display, 2, 2)
        osc2_layout.addWidget(self.osc2_width_display, 3, 2)

        #add radio buttons
        osc2_buttons.addStretch()
        osc2_buttons.addWidget(self.osc2_alg_sin)
        osc2_buttons.addStretch()
        osc2_buttons.addWidget(self.osc2_alg_saw)
        osc2_buttons.addStretch()
        osc2_buttons.addWidget(self.osc2_alg_pulse)
        osc2_buttons.addStretch()
        osc2_layout.addLayout(osc2_buttons, 4, 1)

        #connect signals
        self.osc2_freq_slider.valueChanged.connect(self.change_pitch)
        self.osc2_det_slider.valueChanged.connect(self.change_detune)
        self.osc2_amp_slider.valueChanged.connect(self.change_level)
        self.osc2_width_slider.valueChanged.connect(self.change_width)
        self.osc2_alg_group.buttonClicked.connect(self.change_alg)

        #set object name
        self.setObjectName("osc2_group")

        #set layout
        self.setLayout(osc2_layout)

    #helpers
    def configure_display(self, display, num_digits, num_mode, dig_style, small_dec):
        display.setMode(num_mode)
        display.setDigitCount(num_digits)
        display.setSegmentStyle(dig_style)
        display.setSmallDecimalPoint(small_dec)
        return display
    
    def set_palette(self, display):
        text_color = QColor("#bcd7f0")
        display_palette = display.palette()
        display_palette.setColor(QPalette.ColorRole.WindowText, text_color)
        display.setAutoFillBackground(True)
        display.setPalette(display_palette)

    #slots
    def change_pitch(self, value):
        offset = float(value)/100.0
        self.osc2_freq_display.display(f"{offset:.2f}")
        self.pitch_changed.emit(offset)

    def change_detune(self, value):
        detune = value/20.0
        self.osc2_det_display.display(f"{detune:.2f}")
        self.detune_changed.emit(detune)

    def change_level(self, value):
        newAmp = float(value)/500.0
        self.osc2_amp_display.display(f"{newAmp:.2f}")
        self.level_changed.emit(newAmp)

    def change_width(self, value):
        newWidth = float(value)/500.0
        self.osc2_width_display.display(f"{newWidth:.2f}")
        self.width_changed.emit(newWidth)

    def change_alg(self, button):
        self.alg_changed.emit(button.text())
