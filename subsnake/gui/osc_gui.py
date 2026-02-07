from PySide6.QtWidgets import(
    QSlider, QLabel, QGridLayout,
    QRadioButton, QButtonGroup, QLCDNumber,
    QHBoxLayout, QGroupBox
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QPalette, QColor
from subsnake.gui.lcd import ClickLCD
from subsnake.gui.mod_gui import CoolDial

class OscillatorGUI(QGroupBox):
    #signals
    pitch_changed = Signal(float)
    level_changed = Signal(float)
    width_changed = Signal(float)
    alg_changed = Signal(str)

    def __init__(self, display_color=QColor("black")):
        super().__init__()
        self.display_color = display_color

        #set title
        self.setTitle("oscillator 1")

        #layouts
        osc_layout = QGridLayout()
        osc_buttons = QHBoxLayout()

        #dials
        self.osc_freq_mod_dial = CoolDial(1, -500, 500, "osc_freq")
        self.osc_amp_mod_dial = CoolDial(1, -500, 500, "osc_amp")
        self.osc_width_mod_dial = CoolDial(1, -500, 500, "osc_width")

        #labels
        self.osc_freq_label = QLabel("pitch:")
        self.osc_amp_label = QLabel("level:")
        self.osc_width_label = QLabel("width:")
        self.osc_alg_label = QLabel("shape:")

        #sliders
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

        #displays
        self.osc_freq_display = self.configure_display(ClickLCD(), 3, QLCDNumber.Dec, QLCDNumber.Flat, True)
        self.osc_amp_display = self.configure_display(ClickLCD(), 3, QLCDNumber.Dec, QLCDNumber.Flat, True)
        self.osc_width_display = self.configure_display(ClickLCD(), 3, QLCDNumber.Dec, QLCDNumber.Flat, True)

        #set display palettes
        self.set_palette(self.osc_freq_display)
        self.set_palette(self.osc_amp_display)
        self.set_palette(self.osc_width_display)

        #radio buttons
        self.osc_alg_sin = QRadioButton("sine")
        self.osc_alg_saw = QRadioButton("saw")
        self.osc_alg_pulse = QRadioButton("pulse")
        self.osc_alg_pulse.setChecked(True)

        #button groups
        self.osc_alg_group = QButtonGroup()
        self.osc_alg_group.addButton(self.osc_alg_sin)
        self.osc_alg_group.addButton(self.osc_alg_saw)
        self.osc_alg_group.addButton(self.osc_alg_pulse)

        #add dials
        osc_layout.addWidget(self.osc_freq_mod_dial, 0, 0)
        osc_layout.addWidget(self.osc_amp_mod_dial, 1, 0)
        osc_layout.addWidget(self.osc_width_mod_dial, 2, 0)

        #add labels
        osc_layout.addWidget(self.osc_freq_label, 0, 1)
        osc_layout.addWidget(self.osc_amp_label, 1, 1)
        osc_layout.addWidget(self.osc_width_label, 2, 1)
        osc_layout.addWidget(self.osc_alg_label, 3, 1)

        #add sliders
        osc_layout.addWidget(self.osc_freq_slider, 0, 2)
        osc_layout.addWidget(self.osc_amp_slider, 1, 2)
        osc_layout.addWidget(self.osc_width_slider, 2, 2)

        #add displays
        osc_layout.addWidget(self.osc_freq_display, 0, 3)
        osc_layout.addWidget(self.osc_amp_display, 1, 3)
        osc_layout.addWidget(self.osc_width_display, 2, 3)

        #add radio buttons
        osc_buttons.addStretch()
        osc_buttons.addWidget(self.osc_alg_sin)
        osc_buttons.addStretch()
        osc_buttons.addWidget(self.osc_alg_saw)
        osc_buttons.addStretch()
        osc_buttons.addWidget(self.osc_alg_pulse)
        osc_buttons.addStretch()
        osc_layout.addLayout(osc_buttons, 3, 2)

        #connect signals
        self.osc_freq_slider.valueChanged.connect(self.change_pitch)
        self.osc_amp_slider.valueChanged.connect(self.change_level)
        self.osc_width_slider.valueChanged.connect(self.change_width)
        self.osc_alg_group.buttonClicked.connect(self.change_alg)

        self.osc_freq_display.double_clicked.connect(self.reset_pitch)
        self.osc_amp_display.double_clicked.connect(self.reset_level)
        self.osc_width_display.double_clicked.connect(self.reset_width)

        #set object name
        self.setObjectName("osc_group")

        #set layout
        self.setLayout(osc_layout)

    #helpers
    def configure_display(self, display, num_digits, num_mode, dig_style, small_dec):
        display.setMode(num_mode)
        display.setDigitCount(num_digits)
        display.setSegmentStyle(dig_style)
        display.setSmallDecimalPoint(small_dec)
        return display
    
    def set_palette(self, display):
        text_color = self.display_color
        display_palette = display.palette()
        display_palette.setColor(QPalette.ColorRole.WindowText, text_color)
        display.setAutoFillBackground(True)
        display.setPalette(display_palette)

    def update_wave(self, new_wave):
        if new_wave == "sine":
            self.osc_alg_sin.setChecked(True)
        elif new_wave == "saw":
            self.osc_alg_saw.setChecked(True)
        elif new_wave == "pulse":
            self.osc_alg_pulse.setChecked(True)
        self.alg_changed.emit(new_wave)

    #slots
    def change_pitch(self, value):
        offset = float(value)/250.0
        self.osc_freq_display.display(f"{offset:.2f}")
        self.pitch_changed.emit(offset)

    def change_level(self, value):
        newAmp = float(value)/500.0
        self.osc_amp_display.display(f"{newAmp:.2f}")
        self.level_changed.emit(newAmp)

    def change_width(self, value):
        newWidth = float(value)/500.0
        self.osc_width_display.display(f"{newWidth:.2f}")
        self.width_changed.emit(newWidth)

    def change_alg(self, button):
        self.alg_changed.emit(button.text())

    def reset_pitch(self):
        self.osc_freq_slider.setValue(0)

    def reset_level(self):
        self.osc_amp_slider.setValue(250)

    def reset_width(self):
        self.osc_width_slider.setValue(250)
