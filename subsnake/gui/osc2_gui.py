from PySide6.QtWidgets import(
    QSlider, QLabel, QGridLayout,
    QRadioButton, QButtonGroup, QLCDNumber,
    QHBoxLayout, QGroupBox, QStyle, QStyleOptionGroupBox
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QPalette, QColor
from subsnake.gui.lcd import ClickLCD
from subsnake.gui.mod_gui import CoolDial

class Oscillator2GUI(QGroupBox):
    #signals
    pitch_changed = Signal(float)
    detune_changed = Signal(float)
    level_changed = Signal(float)
    width_changed = Signal(float)
    alg_changed = Signal(str)
    type_changed = Signal(int, int)

    def __init__(self, display_color=QColor("black")):
        super().__init__()
        self.display_color = display_color
        self.type = 0

        #set title
        self.setTitle("oscillator 2")

        #layouts
        osc2_layout = QGridLayout()
        osc2_buttons = QHBoxLayout()

        #dials
        self.osc2_freq_mod_dial = CoolDial(1, -500, 500, "osc2_freq")
        self.osc2_det_mod_dial = CoolDial(1, -500, 500, "osc2_det")
        self.osc2_amp_mod_dial = CoolDial(1, -500, 500, "osc2_amp")
        self.osc2_width_mod_dial = CoolDial(1, -500, 500, "osc2_width")

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
        self.osc2_freq_display = self.configure_display(ClickLCD(), 3, QLCDNumber.Dec, QLCDNumber.Flat, True)
        self.osc2_det_display = self.configure_display(ClickLCD(), 3, QLCDNumber.Dec, QLCDNumber.Flat, True)
        self.osc2_amp_display = self.configure_display(ClickLCD(), 3, QLCDNumber.Dec, QLCDNumber.Flat, True)
        self.osc2_width_display = self.configure_display(ClickLCD(), 3, QLCDNumber.Dec, QLCDNumber.Flat, True)

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

        #add dials
        osc2_layout.addWidget(self.osc2_freq_mod_dial, 0, 0)
        osc2_layout.addWidget(self.osc2_det_mod_dial, 1, 0)
        osc2_layout.addWidget(self.osc2_amp_mod_dial, 2, 0)
        osc2_layout.addWidget(self.osc2_width_mod_dial, 3, 0)

        #add labels
        osc2_layout.addWidget(osc2_freq_label, 0, 1)
        osc2_layout.addWidget(osc2_det_label, 1, 1)
        osc2_layout.addWidget(osc2_amp_label, 2, 1)
        osc2_layout.addWidget(osc2_width_label, 3, 1)
        osc2_layout.addWidget(osc2_alg_label, 4, 1)

        #add sliders
        osc2_layout.addWidget(self.osc2_freq_slider, 0, 2)
        osc2_layout.addWidget(self.osc2_det_slider, 1, 2)
        osc2_layout.addWidget(self.osc2_amp_slider, 2, 2)
        osc2_layout.addWidget(self.osc2_width_slider, 3, 2)

        #add displays
        osc2_layout.addWidget(self.osc2_freq_display, 0, 3)
        osc2_layout.addWidget(self.osc2_det_display, 1, 3)
        osc2_layout.addWidget(self.osc2_amp_display, 2, 3)
        osc2_layout.addWidget(self.osc2_width_display, 3, 3)

        #add radio buttons
        osc2_buttons.addStretch()
        osc2_buttons.addWidget(self.osc2_alg_sin)
        osc2_buttons.addStretch()
        osc2_buttons.addWidget(self.osc2_alg_saw)
        osc2_buttons.addStretch()
        osc2_buttons.addWidget(self.osc2_alg_pulse)
        osc2_buttons.addStretch()
        osc2_layout.addLayout(osc2_buttons, 4, 2)

        #connect signals
        self.osc2_freq_slider.valueChanged.connect(self.change_pitch)
        self.osc2_det_slider.valueChanged.connect(self.change_detune)
        self.osc2_amp_slider.valueChanged.connect(self.change_level)
        self.osc2_width_slider.valueChanged.connect(self.change_width)
        self.osc2_alg_group.buttonClicked.connect(self.change_alg)

        self.osc2_freq_display.double_clicked.connect(self.reset_pitch)
        self.osc2_det_display.double_clicked.connect(self.reset_detune)
        self.osc2_amp_display.double_clicked.connect(self.reset_level)
        self.osc2_width_display.double_clicked.connect(self.reset_width)

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
        text_color = self.display_color
        display_palette = display.palette()
        display_palette.setColor(QPalette.ColorRole.WindowText, text_color)
        display.setAutoFillBackground(True)
        display.setPalette(display_palette)

    def update_wave(self, new_wave):
        if new_wave == "sine":
            self.osc2_alg_sin.setChecked(True)
        elif new_wave == "saw":
            self.osc2_alg_saw.setChecked(True)
        elif new_wave == "pulse":
            self.osc2_alg_pulse.setChecked(True)
        self.alg_changed.emit(new_wave)

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

    def reset_pitch(self):
        self.osc2_freq_slider.setValue(0)

    def reset_detune(self):
        self.osc2_det_slider.setValue(0)

    def reset_level(self):
        self.osc2_amp_slider.setValue(250)

    def reset_width(self):
        self.osc2_width_slider.setValue(250)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            style_option = QStyleOptionGroupBox()
            self.initStyleOption(style_option)
        
            title_rect = self.style().subControlRect(
                QStyle.ComplexControl.CC_GroupBox,
                style_option, QStyle.SubControl.SC_GroupBoxLabel, self 
            )

            if title_rect.contains(event.position().toPoint()):
                if self.type < 1:
                    self.type += 1
                else:
                    self.type = 0
                self.type_changed.emit(2, self.type)
                event.accept()
                return
        super().mouseReleaseEvent(event)