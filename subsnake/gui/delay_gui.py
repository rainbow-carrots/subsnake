from PySide6.QtWidgets import(
    QSlider, QLabel, QGridLayout,
    QLCDNumber, QPushButton,
    QGroupBox
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QPalette, QColor
from subsnake.gui.lcd import ClickLCD
from subsnake.gui.mod_gui import CoolDial

class DelayGUI(QGroupBox):
    time_changed = Signal(float)
    feedback_changed = Signal(float)
    mix_changed = Signal(float)

    def __init__(self, display_color=QColor("black")):
        super().__init__()
        self.display_color = display_color

        #set title
        self.setTitle("delay")

        #layout
        del_layout = QGridLayout()

        #dials
        self.del_time_mod_dial = CoolDial(1, -500, 500, "del_time")
        self.del_feedback_mod_dial = CoolDial(1, -500, 500, "del_feedback")
        self.del_mix_mod_dial = CoolDial(1, -500, 500, "del_mix")

        #labels
        del_time_label = QLabel("time:")
        del_feedback_label = QLabel("feedback:")
        del_mix_label = QLabel("mix:")

        #sliders
        self.del_time_slider = QSlider(Qt.Horizontal)
        self.del_time_slider.setRange(1, 1000)
        self.del_time_slider.setSingleStep(1)

        self.del_feedback_slider = QSlider(Qt.Horizontal)
        self.del_feedback_slider.setRange(1, 1000)
        self.del_feedback_slider.setSingleStep(1)

        self.del_mix_slider = QSlider(Qt.Horizontal)
        self.del_mix_slider.setRange(0, 1000)
        self.del_mix_slider.setSingleStep(1)

        #displays
        self.del_time_display = self.configure_display(ClickLCD(), 3, QLCDNumber.Dec, QLCDNumber.Flat, True)
        self.del_feedback_display = self.configure_display(ClickLCD(), 3, QLCDNumber.Dec, QLCDNumber.Flat, True)
        self.del_mix_display = self.configure_display(ClickLCD(), 3, QLCDNumber.Dec, QLCDNumber.Flat, True)

        #set display palettes
        self.set_palette(self.del_time_display)
        self.set_palette(self.del_feedback_display)
        self.set_palette(self.del_mix_display)

        #add dials
        del_layout.addWidget(self.del_time_mod_dial, 0, 0)
        del_layout.addWidget(self.del_feedback_mod_dial, 1, 0)
        del_layout.addWidget(self.del_mix_mod_dial, 2, 0)

        #add labels
        del_layout.addWidget(del_time_label, 0, 1)
        del_layout.addWidget(del_feedback_label, 1, 1)
        del_layout.addWidget(del_mix_label, 2, 1)

        #add sliders
        del_layout.addWidget(self.del_time_slider, 0, 2)
        del_layout.addWidget(self.del_feedback_slider, 1, 2)
        del_layout.addWidget(self.del_mix_slider, 2, 2)

        #add displays
        del_layout.addWidget(self.del_time_display, 0, 3)
        del_layout.addWidget(self.del_feedback_display, 1, 3)
        del_layout.addWidget(self.del_mix_display, 2, 3)

        #connect signals
        self.del_time_slider.valueChanged.connect(self.change_time)
        self.del_feedback_slider.valueChanged.connect(self.change_feedback)
        self.del_mix_slider.valueChanged.connect(self.change_mix)

        self.del_time_display.double_clicked.connect(self.reset_time)
        self.del_feedback_display.double_clicked.connect(self.reset_feedback)
        self.del_mix_display.double_clicked.connect(self.reset_mix)

        #set layout & object name
        self.setLayout(del_layout)
        self.setObjectName("del_group")


    #slots
    def change_time(self, value):
        new_time = float(value)/1000.0
        self.del_time_display.display(f"{new_time:.2f}")
        self.time_changed.emit(new_time)

    def change_feedback(self, value):
        new_feedback = float(value)/1000.0
        self.del_feedback_display.display(f"{new_feedback:.2f}")
        self.feedback_changed.emit(new_feedback)

    def change_mix(self, value):
        new_mix = float(value)/1000.0
        self.del_mix_display.display(f"{new_mix:.2f}")
        self.mix_changed.emit(new_mix)

    def reset_time(self):
        self.del_time_slider.setValue(100)

    def reset_feedback(self):
        self.del_feedback_slider.setValue(500)

    def reset_mix(self):
        self.del_mix_slider.setValue(500)

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




