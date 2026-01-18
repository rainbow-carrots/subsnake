from PySide6.QtWidgets import(
    QSlider, QLabel, QGridLayout,
    QLCDNumber, QPushButton,
    QGroupBox
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QPalette, QColor

class DelayGUI(QGroupBox):
    time_changed = Signal(float)
    feedback_changed = Signal(float)
    mix_changed = Signal(float)

    def __init__(self):
        super().__init__()

        #set title
        self.setTitle("delay")

        #layout
        del_layout = QGridLayout()

        #labels
        del_time_label = QLabel("time:")
        del_feedback_label = QLabel("feedback:")
        del_mix_label = QLabel("mix:")

        #sliders
        self.del_time_slider = QSlider(Qt.Horizontal)
        self.del_time_slider.setRange(1, 500)
        self.del_time_slider.setSingleStep(1)

        self.del_feedback_slider = QSlider(Qt.Horizontal)
        self.del_feedback_slider.setRange(1, 1000)
        self.del_feedback_slider.setSingleStep(1)

        self.del_mix_slider = QSlider(Qt.Horizontal)
        self.del_mix_slider.setRange(0, 1000)
        self.del_mix_slider.setSingleStep(1)

        #displays
        self.del_time_display = self.configure_display(QLCDNumber(), 3, QLCDNumber.Dec, QLCDNumber.Flat, True)
        self.del_feedback_display = self.configure_display(QLCDNumber(), 3, QLCDNumber.Dec, QLCDNumber.Flat, True)
        self.del_mix_display = self.configure_display(QLCDNumber(), 3, QLCDNumber.Dec, QLCDNumber.Flat, True)

        #set display palettes
        self.set_palette(self.del_time_display)
        self.set_palette(self.del_feedback_display)
        self.set_palette(self.del_mix_display)

        #add labels
        del_layout.addWidget(del_time_label, 0, 0)
        del_layout.addWidget(del_feedback_label, 1, 0)
        del_layout.addWidget(del_mix_label, 2, 0)

        #add sliders
        del_layout.addWidget(self.del_time_slider, 0, 1)
        del_layout.addWidget(self.del_feedback_slider, 1, 1)
        del_layout.addWidget(self.del_mix_slider, 2, 1)

        #add displays
        del_layout.addWidget(self.del_time_display, 0, 2)
        del_layout.addWidget(self.del_feedback_display, 1, 2)
        del_layout.addWidget(self.del_mix_display, 2, 2)

        #connect signals
        self.del_time_slider.valueChanged.connect(self.change_time)
        self.del_feedback_slider.valueChanged.connect(self.change_feedback)
        self.del_mix_slider.valueChanged.connect(self.change_mix)

        #set layout & object name
        self.setLayout(del_layout)
        self.setObjectName("del_group")


    #slots
    def change_time(self, value):
        new_time = float(value)/100.0
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

    #helpers
    def configure_display(self, display, num_digits, num_mode, dig_style, small_dec):
        display.setMode(num_mode)
        display.setDigitCount(num_digits)
        display.setSegmentStyle(dig_style)
        display.setSmallDecimalPoint(small_dec)
        return display
    
    def set_palette(self, display):
        text_color = QColor("#fdf6e7")
        display_palette = display.palette()
        display_palette.setColor(QPalette.ColorRole.WindowText, text_color)
        display.setAutoFillBackground(True)
        display.setPalette(display_palette)




