from PySide6.QtWidgets import(
    QSlider, QLabel, QGridLayout,
    QRadioButton, QButtonGroup, QLCDNumber,
    QHBoxLayout, QGroupBox
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QPalette, QColor
from subsnake.gui.lcd import ClickLCD

class Oscillator3GUI(QGroupBox):
    #signals
    pitch_changed = Signal(float)
    detune_changed = Signal(float)
    level_changed = Signal(float)
    width_changed = Signal(float)
    alg_changed = Signal(str)

    def __init__(self):
        super().__init__()
        #set title
        self.setTitle("oscillator 3")

        #layouts
        osc3_layout = QGridLayout()
        osc3_buttons = QHBoxLayout()

        #labels
        osc3_freq_label = QLabel("pitch:")
        osc3_det_label = QLabel("detune:")
        osc3_amp_label = QLabel("level:")
        osc3_width_label = QLabel("width:")
        osc3_alg_label = QLabel("shape:")

        #sliders
        self.osc3_freq_slider = QSlider(Qt.Horizontal)
        self.osc3_freq_slider.setSingleStep(1)
        self.osc3_freq_slider.setRange(-200, 200)
        self.osc3_freq_slider.setValue(1)

        self.osc3_det_slider = QSlider(Qt.Horizontal)
        self.osc3_det_slider.setSingleStep(1)
        self.osc3_det_slider.setRange(-200, 200)
        self.osc3_det_slider.setValue(1)

        self.osc3_amp_slider = QSlider(Qt.Horizontal)
        self.osc3_amp_slider.setSingleStep(1)
        self.osc3_amp_slider.setRange(0, 500)

        self.osc3_width_slider = QSlider(Qt.Horizontal)
        self.osc3_width_slider.setSingleStep(1)
        self.osc3_width_slider.setRange(0, 500)

        #displays
        self.osc3_freq_display = self.configure_display(ClickLCD(), 3, QLCDNumber.Dec, QLCDNumber.Flat, True)
        self.osc3_det_display = self.configure_display(ClickLCD(), 3, QLCDNumber.Dec, QLCDNumber.Flat, True)
        self.osc3_amp_display = self.configure_display(ClickLCD(), 3, QLCDNumber.Dec, QLCDNumber.Flat, True)
        self.osc3_width_display = self.configure_display(ClickLCD(), 3, QLCDNumber.Dec, QLCDNumber.Flat, True)

        #set display palettes
        self.set_palette(self.osc3_freq_display)
        self.set_palette(self.osc3_det_display)
        self.set_palette(self.osc3_amp_display)
        self.set_palette(self.osc3_width_display)

        #radio buttons
        self.osc3_alg_sin = QRadioButton("sine")
        self.osc3_alg_saw = QRadioButton("saw")
        self.osc3_alg_pulse = QRadioButton("pulse")
        self.osc3_alg_pulse.setChecked(True)

        #button groups
        self.osc3_alg_group = QButtonGroup()
        self.osc3_alg_group.addButton(self.osc3_alg_sin)
        self.osc3_alg_group.addButton(self.osc3_alg_saw)
        self.osc3_alg_group.addButton(self.osc3_alg_pulse)

        #add labels
        osc3_layout.addWidget(osc3_freq_label, 0, 0)
        osc3_layout.addWidget(osc3_det_label, 1, 0)
        osc3_layout.addWidget(osc3_amp_label, 2, 0)
        osc3_layout.addWidget(osc3_width_label, 3, 0)
        osc3_layout.addWidget(osc3_alg_label, 4, 0)

        #add sliders
        osc3_layout.addWidget(self.osc3_freq_slider, 0, 1)
        osc3_layout.addWidget(self.osc3_det_slider, 1, 1)
        osc3_layout.addWidget(self.osc3_amp_slider, 2, 1)
        osc3_layout.addWidget(self.osc3_width_slider, 3, 1)

        #add displays
        osc3_layout.addWidget(self.osc3_freq_display, 0, 2)
        osc3_layout.addWidget(self.osc3_det_display, 1, 2)
        osc3_layout.addWidget(self.osc3_amp_display, 2, 2)
        osc3_layout.addWidget(self.osc3_width_display, 3, 2)

        #add radio buttons
        osc3_buttons.addStretch()
        osc3_buttons.addWidget(self.osc3_alg_sin)
        osc3_buttons.addStretch()
        osc3_buttons.addWidget(self.osc3_alg_saw)
        osc3_buttons.addStretch()
        osc3_buttons.addWidget(self.osc3_alg_pulse)
        osc3_buttons.addStretch()
        osc3_layout.addLayout(osc3_buttons, 4, 1)

        #connect signals
        self.osc3_freq_slider.valueChanged.connect(self.change_pitch)
        self.osc3_det_slider.valueChanged.connect(self.change_detune)
        self.osc3_amp_slider.valueChanged.connect(self.change_level)
        self.osc3_width_slider.valueChanged.connect(self.change_width)
        self.osc3_alg_group.buttonClicked.connect(self.change_alg)

        self.osc3_freq_display.double_clicked.connect(self.reset_pitch)
        self.osc3_det_display.double_clicked.connect(self.reset_detune)
        self.osc3_amp_display.double_clicked.connect(self.reset_level)
        self.osc3_width_display.double_clicked.connect(self.reset_width)

        #set object name
        self.setObjectName("osc3_group")

        #set layout
        self.setLayout(osc3_layout)

    #helpers
    def configure_display(self, display, num_digits, num_mode, dig_style, small_dec):
        display.setMode(num_mode)
        display.setDigitCount(num_digits)
        display.setSegmentStyle(dig_style)
        display.setSmallDecimalPoint(small_dec)
        return display
    
    def set_palette(self, display):
        text_color = QColor("black")
        display_palette = display.palette()
        display_palette.setColor(QPalette.ColorRole.WindowText, text_color)
        display.setAutoFillBackground(True)
        display.setPalette(display_palette)

    def update_wave(self, new_wave):
        if new_wave == "sine":
            self.osc3_alg_sin.setChecked(True)
        elif new_wave == "saw":
            self.osc3_alg_saw.setChecked(True)
        elif new_wave == "pulse":
            self.osc3_alg_pulse.setChecked(True)
        self.alg_changed.emit(new_wave)

    #slots
    def change_pitch(self, value):
        offset = float(value)/100.0
        self.osc3_freq_display.display(f"{offset:.2f}")
        self.pitch_changed.emit(offset)

    def change_detune(self, value):
        detune = value/20.0
        self.osc3_det_display.display(f"{detune:.2f}")
        self.detune_changed.emit(detune)

    def change_level(self, value):
        newAmp = float(value)/500.0
        self.osc3_amp_display.display(f"{newAmp:.2f}")
        self.level_changed.emit(newAmp)

    def change_width(self, value):
        newWidth = float(value)/500.0
        self.osc3_width_display.display(f"{newWidth:.2f}")
        self.width_changed.emit(newWidth)

    def change_alg(self, button):
        self.alg_changed.emit(button.text())

    def reset_pitch(self):
        self.osc3_freq_slider.setValue(0)

    def reset_detune(self):
        self.osc3_det_slider.setValue(0)

    def reset_level(self):
        self.osc3_amp_slider.setValue(250)

    def reset_width(self):
        self.osc3_width_slider.setValue(250)
