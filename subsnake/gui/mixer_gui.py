from PySide6.QtWidgets import(
    QSlider, QLabel, QGridLayout,
    QLCDNumber, QGroupBox, QStyle, QStyleOptionGroupBox
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QPalette, QColor
from subsnake.gui.lcd import ClickLCD
from subsnake.gui.mod_gui import CoolDial

class MixerGUI(QGroupBox):
    level_1_changed = Signal(float)
    level_2_changed = Signal(float)
    level_3_changed = Signal(float)

    def __init__(self, display_color=QColor("black")):
        super().__init__()
        self.display_color = display_color

        #set title
        self.setTitle("mixer")

        #layouts
        mix_layout = QGridLayout()

        #dials
        self.osc1_amp_mod_dial = CoolDial(1, -500, 500, "osc_amp")
        self.osc2_amp_mod_dial = CoolDial(1, -500, 500, "osc2_amp")
        self.osc3_amp_mod_dial = CoolDial(1, -500, 500, "osc3_amp")

        #labels
        self.osc1_amp_label = QLabel("osc. 1:")
        self.osc2_amp_label = QLabel("osc. 2:")
        self.osc3_amp_label = QLabel("osc. 3:")

        #sliders
        self.osc1_amp_slider = QSlider(Qt.Horizontal)
        self.osc1_amp_slider.setSingleStep(1)
        self.osc1_amp_slider.setRange(0, 500)
        self.osc1_amp_slider.setObjectName("osc1_amp_slider")

        self.osc2_amp_slider = QSlider(Qt.Horizontal)
        self.osc2_amp_slider.setSingleStep(1)
        self.osc2_amp_slider.setRange(0, 500)
        self.osc2_amp_slider.setObjectName("osc2_amp_slider")

        self.osc3_amp_slider = QSlider(Qt.Horizontal)
        self.osc3_amp_slider.setSingleStep(1)
        self.osc3_amp_slider.setRange(0, 500)
        self.osc3_amp_slider.setObjectName("osc3_amp_slider")

        #displays
        self.osc1_amp_display = self.configure_display(ClickLCD(), 3, QLCDNumber.Dec, QLCDNumber.Flat, True)
        self.osc2_amp_display = self.configure_display(ClickLCD(), 3, QLCDNumber.Dec, QLCDNumber.Flat, True)
        self.osc3_amp_display = self.configure_display(ClickLCD(), 3, QLCDNumber.Dec, QLCDNumber.Flat, True)

        #set display palettes
        self.set_palette(self.osc1_amp_display)
        self.set_palette(self.osc2_amp_display)
        self.set_palette(self.osc3_amp_display)

        #add dials
        mix_layout.addWidget(self.osc1_amp_mod_dial, 0, 0)
        mix_layout.addWidget(self.osc2_amp_mod_dial, 1, 0)
        mix_layout.addWidget(self.osc3_amp_mod_dial, 2, 0)

        #add labels
        mix_layout.addWidget(self.osc1_amp_label, 0, 1)
        mix_layout.addWidget(self.osc2_amp_label, 1, 1)
        mix_layout.addWidget(self.osc3_amp_label, 2, 1)

        #add sliders
        mix_layout.addWidget(self.osc1_amp_slider, 0, 2)
        mix_layout.addWidget(self.osc2_amp_slider, 1, 2)
        mix_layout.addWidget(self.osc3_amp_slider, 2, 2)

        #add displays
        mix_layout.addWidget(self.osc1_amp_display, 0, 3)
        mix_layout.addWidget(self.osc2_amp_display, 1, 3)
        mix_layout.addWidget(self.osc3_amp_display, 2, 3)

        #connect signals
        self.osc1_amp_slider.valueChanged.connect(self.change_level_1)
        self.osc2_amp_slider.valueChanged.connect(self.change_level_2)
        self.osc3_amp_slider.valueChanged.connect(self.change_level_3)

        self.osc1_amp_display.double_clicked.connect(self.reset_level_1)
        self.osc2_amp_display.double_clicked.connect(self.reset_level_2)
        self.osc3_amp_display.double_clicked.connect(self.reset_level_3)

        self.setLayout(mix_layout)

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

    #slots
    def change_level_1(self, value):
        newAmp = float(value)/500.0
        self.osc1_amp_display.display(f"{newAmp:.2f}")
        self.level_1_changed.emit(newAmp)

    def change_level_2(self, value):
        newAmp = float(value)/500.0
        self.osc2_amp_display.display(f"{newAmp:.2f}")
        self.level_2_changed.emit(newAmp)

    def change_level_3(self, value):
        newAmp = float(value)/500.0
        self.osc3_amp_display.display(f"{newAmp:.2f}")
        self.level_3_changed.emit(newAmp)

    def reset_level_1(self):
        self.osc1_amp_slider.setValue(250)

    def reset_level_2(self):
        self.osc2_amp_slider.setValue(250)

    def reset_level_3(self):
        self.osc3_amp_slider.setValue(250)