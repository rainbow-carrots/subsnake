from PySide6.QtWidgets import(
    QSlider, QLabel, QPushButton, QLCDNumber,
    QWidget, QGroupBox, QGridLayout, QStackedLayout,
    QButtonGroup
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QPalette, QColor
from subsnake.gui.lcd import ClickLCD
from subsnake.gui.mod_gui import CoolDial

class MixerGUI(QWidget):
    level_1_changed = Signal(float)
    level_2_changed = Signal(float)
    level_3_changed = Signal(float)
    pan_1_changed = Signal(float)
    pan_2_changed = Signal(float)
    pan_3_changed = Signal(float)

    def __init__(self, display_color=QColor("black")):
        super().__init__()
        self.display_color = display_color
        self.setObjectName("mixer_group")

        #layouts
        main_layout = QGridLayout()
        mix_layout = QGridLayout()
        pan_layout = QGridLayout()
        mode_select_layout = QGridLayout()
        self.mixer_stack_layout = QStackedLayout()
        mode_select_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)


        #stack widgets
        self.mix_widget = QWidget()
        self.pan_widget = QWidget()
        self.mixer_stack = QGroupBox()
        self.mixer_stack.setTitle("mixer")
        self.mixer_stack.setAttribute(Qt.WA_StyledBackground, True)

        #mix/pan select buttons
        self.mode_select = QWidget()
        self.mode_select_buttons = QButtonGroup()
        self.mix_select_button = QPushButton("mix")
        self.mix_select_button.setObjectName("mix_select")
        self.mix_select_button.setCheckable(True)
        self.mix_select_button.setChecked(True)
        self.pan_select_button = QPushButton("pan")
        self.pan_select_button.setObjectName("pan_select")
        self.pan_select_button.setCheckable(True)

        self.mode_select_buttons.addButton(self.mix_select_button)
        self.mode_select_buttons.addButton(self.pan_select_button)

        #dials
        self.osc1_amp_mod_dial = CoolDial(1, -500, 500, "osc_amp")
        self.osc2_amp_mod_dial = CoolDial(1, -500, 500, "osc2_amp")
        self.osc3_amp_mod_dial = CoolDial(1, -500, 500, "osc3_amp")
        self.osc1_pan_mod_dial = CoolDial(1, -500, 500, "osc_pan")
        self.osc2_pan_mod_dial = CoolDial(1, -500, 500, "osc2_pan")
        self.osc3_pan_mod_dial = CoolDial(1, -500, 500, "osc3_pan")

        #labels
        self.osc1_amp_label = QLabel("mix 1:")
        self.osc2_amp_label = QLabel("mix 2:")
        self.osc3_amp_label = QLabel("mix 3:")
        self.osc1_pan_label = QLabel("pan 1:")
        self.osc2_pan_label = QLabel("pan 2:")
        self.osc3_pan_label = QLabel("pan 3:")

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

        self.osc1_pan_slider = QSlider(Qt.Horizontal)
        self.osc1_pan_slider.setSingleStep(1)
        self.osc1_pan_slider.setRange(-250, 250)
        self.osc1_pan_slider.setObjectName("osc1_pan_slider")

        self.osc2_pan_slider = QSlider(Qt.Horizontal)
        self.osc2_pan_slider.setSingleStep(1)
        self.osc2_pan_slider.setRange(-250, 250)
        self.osc2_pan_slider.setObjectName("osc2_pan_slider")

        self.osc3_pan_slider = QSlider(Qt.Horizontal)
        self.osc3_pan_slider.setSingleStep(1)
        self.osc3_pan_slider.setRange(-250, 250)
        self.osc3_pan_slider.setObjectName("osc3_pan_slider")

        #displays
        self.osc1_amp_display = self.configure_display(ClickLCD(), 3, QLCDNumber.Dec, QLCDNumber.Flat, True)
        self.osc2_amp_display = self.configure_display(ClickLCD(), 3, QLCDNumber.Dec, QLCDNumber.Flat, True)
        self.osc3_amp_display = self.configure_display(ClickLCD(), 3, QLCDNumber.Dec, QLCDNumber.Flat, True)
        self.osc1_pan_display = self.configure_display(ClickLCD(), 3, QLCDNumber.Dec, QLCDNumber.Flat, True)
        self.osc2_pan_display = self.configure_display(ClickLCD(), 3, QLCDNumber.Dec, QLCDNumber.Flat, True)
        self.osc3_pan_display = self.configure_display(ClickLCD(), 3, QLCDNumber.Dec, QLCDNumber.Flat, True)

        #set display palettes
        self.set_palette(self.osc1_amp_display)
        self.set_palette(self.osc2_amp_display)
        self.set_palette(self.osc3_amp_display)
        self.set_palette(self.osc1_pan_display)
        self.set_palette(self.osc2_pan_display)
        self.set_palette(self.osc3_pan_display)

        #add dials
        mix_layout.addWidget(self.osc1_amp_mod_dial, 0, 0)
        mix_layout.addWidget(self.osc2_amp_mod_dial, 1, 0)
        mix_layout.addWidget(self.osc3_amp_mod_dial, 2, 0)
        pan_layout.addWidget(self.osc1_pan_mod_dial, 0, 0)
        pan_layout.addWidget(self.osc2_pan_mod_dial, 1, 0)
        pan_layout.addWidget(self.osc3_pan_mod_dial, 2, 0)

        #add labels
        mix_layout.addWidget(self.osc1_amp_label, 0, 1)
        mix_layout.addWidget(self.osc2_amp_label, 1, 1)
        mix_layout.addWidget(self.osc3_amp_label, 2, 1)
        pan_layout.addWidget(self.osc1_pan_label, 0, 1)
        pan_layout.addWidget(self.osc2_pan_label, 1, 1)
        pan_layout.addWidget(self.osc3_pan_label, 2, 1)

        #add sliders
        mix_layout.addWidget(self.osc1_amp_slider, 0, 2)
        mix_layout.addWidget(self.osc2_amp_slider, 1, 2)
        mix_layout.addWidget(self.osc3_amp_slider, 2, 2)
        pan_layout.addWidget(self.osc1_pan_slider, 0, 2)
        pan_layout.addWidget(self.osc2_pan_slider, 1, 2)
        pan_layout.addWidget(self.osc3_pan_slider, 2, 2)

        #add displays
        mix_layout.addWidget(self.osc1_amp_display, 0, 3)
        mix_layout.addWidget(self.osc2_amp_display, 1, 3)
        mix_layout.addWidget(self.osc3_amp_display, 2, 3)
        pan_layout.addWidget(self.osc1_pan_display, 0, 3)
        pan_layout.addWidget(self.osc2_pan_display, 1, 3)
        pan_layout.addWidget(self.osc3_pan_display, 2, 3)

        #mode select buttons
        mode_select_layout.addWidget(self.mix_select_button, 0, 0)
        mode_select_layout.addWidget(self.pan_select_button, 0, 1)
        self.mode_select.setLayout(mode_select_layout)

        #configure stack
        self.mix_widget.setLayout(mix_layout)
        self.pan_widget.setLayout(pan_layout)
        self.mixer_stack_layout.addWidget(self.mix_widget)
        self.mixer_stack_layout.addWidget(self.pan_widget)
        self.mixer_stack.setLayout(self.mixer_stack_layout)

        #main layout
        main_layout.addWidget(self.mixer_stack, 0, 0)
        main_layout.addWidget(self.mode_select, 1, 0)

        #connect signals
        self.mode_select_buttons.buttonClicked.connect(self.change_mode)

        self.osc1_amp_slider.valueChanged.connect(self.change_level_1)
        self.osc2_amp_slider.valueChanged.connect(self.change_level_2)
        self.osc3_amp_slider.valueChanged.connect(self.change_level_3)
        self.osc1_pan_slider.valueChanged.connect(self.change_pan_1)
        self.osc2_pan_slider.valueChanged.connect(self.change_pan_2)
        self.osc3_pan_slider.valueChanged.connect(self.change_pan_3)

        self.osc1_amp_display.double_clicked.connect(self.reset_level_1)
        self.osc2_amp_display.double_clicked.connect(self.reset_level_2)
        self.osc3_amp_display.double_clicked.connect(self.reset_level_3)
        self.osc1_pan_display.double_clicked.connect(self.reset_pan_1)
        self.osc2_pan_display.double_clicked.connect(self.reset_pan_2)
        self.osc3_pan_display.double_clicked.connect(self.reset_pan_3)

        self.setLayout(main_layout)

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
    def change_mode(self, button):
        mode = button.text()
        if mode == "mix":
            self.mixer_stack_layout.setCurrentIndex(0)
        elif mode == "pan":
            self.mixer_stack_layout.setCurrentIndex(1)

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

    def change_pan_1(self, value):
        newPan = float(value)/250.0
        self.osc1_pan_display.display(f"{newPan:.2f}")
        self.pan_1_changed.emit(newPan)

    def change_pan_2(self, value):
        newPan = float(value)/250.0
        self.osc2_pan_display.display(f"{newPan:.2f}")
        self.pan_2_changed.emit(newPan)

    def change_pan_3(self, value):
        newPan = float(value)/250.0
        self.osc3_pan_display.display(f"{newPan:.2f}")
        self.pan_3_changed.emit(newPan)

    def reset_pan_1(self):
        self.osc1_pan_slider.setValue(0)

    def reset_pan_2(self):
        self.osc2_pan_slider.setValue(0)

    def reset_pan_3(self):
        self.osc3_pan_slider.setValue(0)