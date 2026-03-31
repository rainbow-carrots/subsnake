from PySide6.QtWidgets import(
    QSlider, QLabel, QGridLayout, QToolTip,
    QRadioButton, QButtonGroup, QLCDNumber,
    QHBoxLayout, QGroupBox, QStyle, QStyleOptionGroupBox
)
from PySide6.QtCore import Signal, Qt, QEvent
from PySide6.QtGui import QPalette, QColor
from subsnake.gui.lcd import ClickLCD
from subsnake.gui.mod_gui import CoolDial

class OscillatorGUI(QGroupBox):
    #signals
    pitch_changed = Signal(float)
    detune_changed = Signal(float)
    width_changed = Signal(float)
    alg_changed = Signal(str)
    type_changed = Signal(int, int)

    def __init__(self, display_color=QColor("black")):
        super().__init__()
        self.display_color = display_color
        self.type = 0

        #set title
        self.setTitle("oscillator 1")

        #layouts
        osc_layout = QGridLayout()
        osc_buttons = QHBoxLayout()

        #dials
        self.osc_freq_mod_dial = CoolDial(1, -500, 500, "osc_freq")
        self.osc_det_mod_dial = CoolDial(1, -500, 500, "osc_det")
        self.osc_width_mod_dial = CoolDial(1, -500, 500, "osc_width")

        #labels
        self.osc_freq_label = QLabel("pitch:")
        self.osc_det_label = QLabel("detune:")
        self.osc_width_label = QLabel("width:")
        self.osc_alg_label = QLabel("shape:")

        #sliders
        self.osc_freq_slider = QSlider(Qt.Horizontal)
        self.osc_freq_slider.setSingleStep(1)
        self.osc_freq_slider.setRange(-500, 500)
        self.osc_freq_slider.setValue(1)

        self.osc_det_slider = QSlider(Qt.Horizontal)
        self.osc_det_slider.setSingleStep(1)
        self.osc_det_slider.setRange(-200, 200)
        self.osc_det_slider.setValue(1)

        self.osc_width_slider = QSlider(Qt.Horizontal)
        self.osc_width_slider.setSingleStep(1)
        self.osc_width_slider.setRange(0, 500)

        #displays
        self.osc_freq_display = self.configure_display(ClickLCD(), 3, QLCDNumber.Dec, QLCDNumber.Flat, True)
        self.osc_det_display = self.configure_display(ClickLCD(), 3, QLCDNumber.Dec, QLCDNumber.Flat, True)
        self.osc_width_display = self.configure_display(ClickLCD(), 3, QLCDNumber.Dec, QLCDNumber.Flat, True)

        #set display palettes
        self.set_palette(self.osc_freq_display)
        self.set_palette(self.osc_det_display)
        self.set_palette(self.osc_width_display)

        #radio buttons
        self.osc_alg_sin = QRadioButton("sine")
        self.osc_alg_tri = QRadioButton("triangle")
        self.osc_alg_saw = QRadioButton("saw")
        self.osc_alg_pulse = QRadioButton("pulse")
        self.osc_alg_pulse.setChecked(True)

        #button groups
        self.osc_alg_group = QButtonGroup()
        self.osc_alg_group.addButton(self.osc_alg_sin)
        self.osc_alg_group.addButton(self.osc_alg_tri)
        self.osc_alg_group.addButton(self.osc_alg_saw)
        self.osc_alg_group.addButton(self.osc_alg_pulse)

        #add dials
        osc_layout.addWidget(self.osc_freq_mod_dial, 0, 0)
        osc_layout.addWidget(self.osc_det_mod_dial, 1, 0)
        osc_layout.addWidget(self.osc_width_mod_dial, 2, 0)

        #add labels
        osc_layout.addWidget(self.osc_freq_label, 0, 1)
        osc_layout.addWidget(self.osc_det_label, 1, 1)
        osc_layout.addWidget(self.osc_width_label, 2, 1)
        osc_layout.addWidget(self.osc_alg_label, 3, 1)

        #add sliders
        osc_layout.addWidget(self.osc_freq_slider, 0, 2)
        osc_layout.addWidget(self.osc_det_slider, 1, 2)
        osc_layout.addWidget(self.osc_width_slider, 2, 2)

        #add displays
        osc_layout.addWidget(self.osc_freq_display, 0, 3)
        osc_layout.addWidget(self.osc_det_display, 1, 3)
        osc_layout.addWidget(self.osc_width_display, 2, 3)

        #add radio buttons
        osc_buttons.addStretch()
        osc_buttons.addWidget(self.osc_alg_sin)
        osc_buttons.addStretch()
        osc_buttons.addWidget(self.osc_alg_tri)
        osc_buttons.addStretch()
        osc_buttons.addWidget(self.osc_alg_saw)
        osc_buttons.addStretch()
        osc_buttons.addWidget(self.osc_alg_pulse)
        osc_buttons.addStretch()
        osc_layout.addLayout(osc_buttons, 3, 2)

        #connect signals
        self.osc_freq_slider.valueChanged.connect(self.change_pitch)
        self.osc_det_slider.valueChanged.connect(self.change_detune)
        self.osc_width_slider.valueChanged.connect(self.change_width)
        self.osc_alg_group.buttonClicked.connect(self.change_alg)

        self.osc_freq_display.double_clicked.connect(self.reset_pitch)
        self.osc_det_display.double_clicked.connect(self.reset_detune)
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
        elif new_wave == "triangle":
            self.osc_alg_tri.setChecked(True)
        elif new_wave == "saw":
            self.osc_alg_saw.setChecked(True)
        elif new_wave == "pulse":
            self.osc_alg_pulse.setChecked(True)
        self.alg_changed.emit(new_wave)

    def update_type(self, new_type):
        self.type = new_type
        self.type_changed.emit(1, self.type)

    #slots
    def change_pitch(self, value):
        offset = float(value)/250.0
        self.osc_freq_display.display(f"{offset:.2f}")
        self.pitch_changed.emit(offset)

    def change_detune(self, value):
        detune = value/20.0
        self.osc_det_display.display(f"{detune:.2f}")
        self.detune_changed.emit(detune)

    def change_width(self, value):
        newWidth = float(value)/500.0
        self.osc_width_display.display(f"{newWidth:.2f}")
        self.width_changed.emit(newWidth)

    def change_alg(self, button):
        self.alg_changed.emit(button.text())

    def reset_pitch(self):
        self.osc_freq_slider.setValue(0)

    def reset_detune(self):
        self.osc_det_slider.setValue(0)

    def reset_width(self):
        self.osc_width_slider.setValue(250)

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
                if self.type == 0:
                    type_text = "BLIT"
                elif self.type == 1:
                    type_text = "PolyBLEP"
                self.type_changed.emit(1, self.type)
                QToolTip.showText(event.globalPos(), type_text)
                event.accept()
                return
        super().mouseReleaseEvent(event)

    def event(self, event):
        if event.type() == QEvent.Type.ToolTip:
            style_option = QStyleOptionGroupBox()
            self.initStyleOption(style_option)
        
            title_rect = self.style().subControlRect(
                QStyle.ComplexControl.CC_GroupBox,
                style_option, QStyle.SubControl.SC_GroupBoxLabel, self 
            )

            if title_rect.contains(event.pos()):
                if self.type == 0:
                    type_text = "BLIT"
                elif self.type == 1:
                    type_text = "PolyBLEP"
                QToolTip.showText(event.globalPos(), type_text)
            else:
                QToolTip.hideText()
            event.accept()
            return True
        else:
            return super().event(event)
