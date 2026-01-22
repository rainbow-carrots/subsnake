from PySide6.QtWidgets import(
    QSlider, QLabel, QGridLayout,
    QRadioButton, QButtonGroup, QLCDNumber,
    QHBoxLayout, QGroupBox
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QPalette, QColor
from subsnake.gui.lcd import ClickLCD

class FilterGUI(QGroupBox):
    #signals
    freq_changed = Signal(float)
    res_changed = Signal(float)
    drive_changed = Signal(float)
    sat_changed = Signal(float)
    alg_changed = Signal(str)

    def __init__(self):
        super().__init__()
        #set title
        self.setTitle("filter")

        #layouts
        filt_layout = QGridLayout()
        filt_buttons = QHBoxLayout()

        #labels
        filt_freq_label = QLabel("cutoff:")
        filt_res_label = QLabel("feedback:")
        filt_drive_label = QLabel("drive:")
        filt_sat_label = QLabel("saturate:")
        filt_alg_label = QLabel("type:")

        #sliders
        self.filt_freq_slider = QSlider(Qt.Horizontal)
        self.filt_freq_slider.setSingleStep(1)
        self.filt_freq_slider.setRange(0, 800)

        self.filt_res_slider = QSlider(Qt.Horizontal)
        self.filt_res_slider.setSingleStep(1)
        self.filt_res_slider.setRange(0, 200)
        self.filt_res_slider.setValue(1)

        self.filt_drive_slider = QSlider(Qt.Horizontal)
        self.filt_drive_slider.setSingleStep(1)
        self.filt_drive_slider.setRange(1, 360)

        self.filt_sat_slider = QSlider(Qt.Horizontal)
        self.filt_sat_slider.setSingleStep(1)
        self.filt_sat_slider.setRange(100, 1200)

        #displays
        self.filt_freq_display = self.configure_display(ClickLCD(), 5, QLCDNumber.Dec, QLCDNumber.Flat, True)
        self.filt_fback_display = self.configure_display(ClickLCD(), 5, QLCDNumber.Dec, QLCDNumber.Flat, True)
        self.filt_drive_display = self.configure_display(ClickLCD(), 5, QLCDNumber.Dec, QLCDNumber.Flat, True)
        self.filt_sat_display = self.configure_display(ClickLCD(), 5, QLCDNumber.Dec, QLCDNumber.Flat, True)

        #set display palettes
        self.set_palette(self.filt_freq_display)
        self.set_palette(self.filt_fback_display)
        self.set_palette(self.filt_drive_display)
        self.set_palette(self.filt_sat_display)

        #radio buttons
        self.filt_alg_low = QRadioButton("low")
        self.filt_alg_high = QRadioButton("high")
        self.filt_alg_band = QRadioButton("band")
        self.filt_alg_notch = QRadioButton("notch")
        self.filt_alg_low.setChecked(True)

        #add buttons to group
        self.filt_alg_group = QButtonGroup()
        self.filt_alg_group.addButton(self.filt_alg_low)
        self.filt_alg_group.addButton(self.filt_alg_high)
        self.filt_alg_group.addButton(self.filt_alg_band)
        self.filt_alg_group.addButton(self.filt_alg_notch)

        #add labels to layout
        filt_layout.addWidget(filt_freq_label, 0, 0)
        filt_layout.addWidget(filt_res_label, 1, 0)
        filt_layout.addWidget(filt_drive_label, 2, 0)
        filt_layout.addWidget(filt_sat_label, 3, 0)
        filt_layout.addWidget(filt_alg_label, 4, 0)

        #add sliders to layout
        filt_layout.addWidget(self.filt_freq_slider, 0, 1)
        filt_layout.addWidget(self.filt_res_slider, 1, 1)
        filt_layout.addWidget(self.filt_drive_slider, 2, 1)
        filt_layout.addWidget(self.filt_sat_slider, 3, 1)

        #add displays to layout
        filt_layout.addWidget(self.filt_freq_display, 0, 2)
        filt_layout.addWidget(self.filt_fback_display, 1, 2)
        filt_layout.addWidget(self.filt_drive_display, 2, 2)
        filt_layout.addWidget(self.filt_sat_display, 3, 2)

        #add radio buttons to layout
        filt_buttons.addStretch()
        filt_buttons.addWidget(self.filt_alg_low)
        filt_buttons.addStretch()
        filt_buttons.addWidget(self.filt_alg_high)
        filt_buttons.addStretch()
        filt_buttons.addWidget(self.filt_alg_band)
        filt_buttons.addStretch()
        filt_buttons.addWidget(self.filt_alg_notch)
        filt_buttons.addStretch()
        filt_layout.addLayout(filt_buttons, 4, 1)

        #connect signals
        self.filt_freq_slider.valueChanged.connect(self.change_freq)
        self.filt_res_slider.valueChanged.connect(self.change_res)
        self.filt_drive_slider.valueChanged.connect(self.change_drive)
        self.filt_sat_slider.valueChanged.connect(self.change_sat)
        self.filt_alg_group.buttonClicked.connect(self.change_alg)

        self.filt_freq_display.double_clicked.connect(self.reset_freq)
        self.filt_fback_display.double_clicked.connect(self.reset_res)
        self.filt_drive_display.double_clicked.connect(self.reset_drive)
        self.filt_sat_display.double_clicked.connect(self.reset_sat)

        #set object name
        self.setObjectName("filt_group")

        #set layout
        self.setLayout(filt_layout)

    #helpers
    def configure_display(self, display, num_digits, num_mode, dig_style, small_dec):
        display.setMode(num_mode)
        display.setDigitCount(num_digits)
        display.setSegmentStyle(dig_style)
        display.setSmallDecimalPoint(small_dec)
        return display
    
    def set_palette(self, display):
        text_color = QColor("#edfff2")
        display_palette = display.palette()
        display_palette.setColor(QPalette.ColorRole.WindowText, text_color)
        display.setAutoFillBackground(True)
        display.setPalette(display_palette)

    def update_type(self, new_type):
        if new_type == "low":
            self.filt_alg_low.setChecked(True)
        elif new_type == "high":
            self.filt_alg_high.setChecked(True)
        elif new_type == "band":
            self.filt_alg_band.setChecked(True)
        elif new_type == "notch":
            self.filt_alg_notch.setChecked(True)
        self.alg_changed.emit(new_type)

    #slots
    def change_freq(self, value):
        newFreq = 27.5 * 2**(float(value)/100.0)
        self.filt_freq_display.display(f"{newFreq:.1f}")
        self.freq_changed.emit(newFreq)

    def change_res(self, value):
        newRes = 10.0 / (10.0**(value/100.0))
        self.filt_fback_display.display(f"{1.0/newRes:.2f}")
        self.res_changed.emit(newRes)

    def change_drive(self, value):
        newDrive = value/40.0
        self.filt_drive_display.display(f"{newDrive:.2f}")
        self.drive_changed.emit(newDrive)

    def change_sat(self, value):
        newSat = float(value)/100.0
        self.filt_sat_display.display(f"{newSat:.2f}")
        self.sat_changed.emit(newSat)

    def change_alg(self, button):
        self.alg_changed.emit(button.text())

    def reset_freq(self):
        self.filt_freq_slider.setValue(700)

    def reset_res(self):
        self.filt_res_slider.setValue(0)

    def reset_drive(self):
        self.filt_drive_slider.setValue(40)

    def reset_sat(self):
        self.filt_sat_slider.setValue(100)
