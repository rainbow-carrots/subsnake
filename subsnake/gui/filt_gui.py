from PySide6.QtWidgets import(
    QSlider, QLabel, QGridLayout, QToolTip,
    QRadioButton, QButtonGroup, QLCDNumber,
    QHBoxLayout, QGroupBox, QStyle, QStyleOptionGroupBox
)
from PySide6.QtCore import Signal, Qt, QEvent
from PySide6.QtGui import QPalette, QColor
from subsnake.gui.lcd import ClickLCD
from subsnake.gui.mod_gui import CoolDial

class FilterGUI(QGroupBox):
    #signals
    freq_changed = Signal(float)
    res_changed = Signal(float)
    drive_changed = Signal(float)
    sat_changed = Signal(float)
    alg_changed = Signal(str)
    mode_changed = Signal(int)

    def __init__(self, display_color=QColor("black")):
        super().__init__()
        self.display_color = display_color
        self.mode = 0

        #set title
        self.setTitle("filter")

        #layouts
        filt_layout = QGridLayout()
        filt_buttons = QHBoxLayout()

        #dials
        self.filt_freq_mod_dial = CoolDial(1, -500, 500, "filt_freq")
        self.filt_res_mod_dial = CoolDial(1, -500, 500, "filt_res")
        self.filt_drive_mod_dial = CoolDial(1, -500, 500, "filt_drive")
        self.filt_sat_mod_dial = CoolDial(1, -500, 500, "filt_sat")

        #labels
        filt_freq_label = QLabel("cutoff:")
        filt_res_label = QLabel("feedback:")
        filt_drive_label = QLabel("drive:")
        filt_sat_label = QLabel("saturate:")
        filt_alg_label = QLabel("type:")

        #sliders
        self.filt_freq_slider = QSlider(Qt.Horizontal)
        self.filt_freq_slider.setSingleStep(1)
        self.filt_freq_slider.setRange(0, 900)

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

        #add dials
        filt_layout.addWidget(self.filt_freq_mod_dial, 0, 0)
        filt_layout.addWidget(self.filt_res_mod_dial, 1, 0)
        filt_layout.addWidget(self.filt_drive_mod_dial, 2, 0)
        filt_layout.addWidget(self.filt_sat_mod_dial, 3, 0)

        #add labels to layout
        filt_layout.addWidget(filt_freq_label, 0, 1)
        filt_layout.addWidget(filt_res_label, 1, 1)
        filt_layout.addWidget(filt_drive_label, 2, 1)
        filt_layout.addWidget(filt_sat_label, 3, 1)
        filt_layout.addWidget(filt_alg_label, 4, 1)

        #add sliders to layout
        filt_layout.addWidget(self.filt_freq_slider, 0, 2)
        filt_layout.addWidget(self.filt_res_slider, 1, 2)
        filt_layout.addWidget(self.filt_drive_slider, 2, 2)
        filt_layout.addWidget(self.filt_sat_slider, 3, 2)

        #add displays to layout
        filt_layout.addWidget(self.filt_freq_display, 0, 3)
        filt_layout.addWidget(self.filt_fback_display, 1, 3)
        filt_layout.addWidget(self.filt_drive_display, 2, 3)
        filt_layout.addWidget(self.filt_sat_display, 3, 3)

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
        filt_layout.addLayout(filt_buttons, 4, 2)

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
        text_color = self.display_color
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

    def update_mode(self, newMode):
        self.mode = newMode
        self.mode_changed.emit(newMode)

    #slots
    def change_freq(self, value):
        newFreq = 27.5 * 2**(float(value)/100.0)
        self.filt_freq_display.display(f"{newFreq:.1f}")
        self.freq_changed.emit(newFreq)

    def change_res(self, value):
        newRes = 5.0 / (10.0**(value/100.0))
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

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            style_option = QStyleOptionGroupBox()
            self.initStyleOption(style_option)
        
            title_rect = self.style().subControlRect(
                QStyle.ComplexControl.CC_GroupBox,
                style_option, QStyle.SubControl.SC_GroupBoxLabel, self 
            )

            if title_rect.contains(event.position().toPoint()):
                if self.mode == 0:
                    self.mode = 1
                else:
                    self.mode = 0
                if self.mode == 0:
                    type_text = "Chamberlin"
                elif self.mode == 1:
                    type_text = "ZDF"
                self.mode_changed.emit(self.mode)
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
                if self.mode == 0:
                    type_text = "Chamberlin"
                elif self.mode == 1:
                    type_text = "ZDF"
                QToolTip.showText(event.globalPos(), type_text)
            else:
                QToolTip.hideText()
            event.accept()
            return True
        else:
            return super().event(event)