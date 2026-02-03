from PySide6.QtWidgets import(
    QSlider, QLabel, QGridLayout,
    QLCDNumber, QGroupBox
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QPalette, QColor
from subsnake.gui.lcd import ClickLCD
from subsnake.gui.mod_gui import CoolDial

class FilterEnvGUI(QGroupBox):
    #signals
    attack_changed = Signal(float)
    decay_changed = Signal(float)
    sustain_changed = Signal(float)
    release_changed = Signal(float)
    amount_changed = Signal(float)

    def __init__(self, display_color=QColor("black")):
        super().__init__()
        self.display_color = display_color

        #set title
        self.setTitle("filter env.")

        #layout
        fenv_layout = QGridLayout()

        #dials
        self.fenv_att_mod_dial = CoolDial(1, -500, 500, "fenv_att")
        self.fenv_dec_mod_dial = CoolDial(1, -500, 500, "fenv_dec")
        self.fenv_sus_mod_dial = CoolDial(1, -500, 500, "fenv_sus")
        self.fenv_rel_mod_dial = CoolDial(1, -500, 500, "fenv_rel")
        self.fenv_amt_mod_dial = CoolDial(1, -500, 500, "fenv_amt")

        #labels
        fenv_att_label = QLabel("attack:")
        fenv_dec_label = QLabel("decay:")
        fenv_sus_label = QLabel("sustain:")
        fenv_rel_label = QLabel("release:")
        fenv_amt_label = QLabel("depth:")

        #sliders
        self.fenv_att_slider = QSlider(Qt.Horizontal)
        self.fenv_att_slider.setSingleStep(1)
        self.fenv_att_slider.setRange(1, 1000)

        self.fenv_dec_slider = QSlider(Qt.Horizontal)
        self.fenv_dec_slider.setSingleStep(1)
        self.fenv_dec_slider.setRange(1, 1000)

        self.fenv_sus_slider = QSlider(Qt.Horizontal)
        self.fenv_sus_slider.setSingleStep(1)
        self.fenv_sus_slider.setRange(1, 1000)

        self.fenv_rel_slider = QSlider(Qt.Horizontal)
        self.fenv_rel_slider.setSingleStep(1)
        self.fenv_rel_slider.setRange(1, 1000)

        self.fenv_amt_slider = QSlider(Qt.Horizontal)
        self.fenv_amt_slider.setSingleStep(1)
        self.fenv_amt_slider.setRange(-500, 500)
        self.fenv_amt_slider.setValue(1)

        #displays
        self.fenv_att_display = self.configure_display(ClickLCD(), 3, QLCDNumber.Dec, QLCDNumber.Flat, True)
        self.fenv_dec_display = self.configure_display(ClickLCD(), 3, QLCDNumber.Dec, QLCDNumber.Flat, True)
        self.fenv_sus_display = self.configure_display(ClickLCD(), 3, QLCDNumber.Dec, QLCDNumber.Flat, True)
        self.fenv_rel_display = self.configure_display(ClickLCD(), 3, QLCDNumber.Dec, QLCDNumber.Flat, True)
        self.fenv_amt_display = self.configure_display(ClickLCD(), 3, QLCDNumber.Dec, QLCDNumber.Flat, True)

        #set display palettes
        self.set_palette(self.fenv_att_display)
        self.set_palette(self.fenv_dec_display)
        self.set_palette(self.fenv_sus_display)
        self.set_palette(self.fenv_rel_display)
        self.set_palette(self.fenv_amt_display)

        #add dials
        fenv_layout.addWidget(self.fenv_att_mod_dial, 0, 0)
        fenv_layout.addWidget(self.fenv_dec_mod_dial, 1, 0)
        fenv_layout.addWidget(self.fenv_sus_mod_dial, 2, 0)
        fenv_layout.addWidget(self.fenv_rel_mod_dial, 3, 0)
        fenv_layout.addWidget(self.fenv_amt_mod_dial, 4, 0)

        #add labels
        fenv_layout.addWidget(fenv_att_label, 0, 1)
        fenv_layout.addWidget(fenv_dec_label, 1, 1)
        fenv_layout.addWidget(fenv_sus_label, 2, 1)
        fenv_layout.addWidget(fenv_rel_label, 3, 1)
        fenv_layout.addWidget(fenv_amt_label, 4, 1)

        #add sliders
        fenv_layout.addWidget(self.fenv_att_slider, 0, 2)
        fenv_layout.addWidget(self.fenv_dec_slider, 1, 2)
        fenv_layout.addWidget(self.fenv_sus_slider, 2, 2)
        fenv_layout.addWidget(self.fenv_rel_slider, 3, 2)
        fenv_layout.addWidget(self.fenv_amt_slider, 4, 2)

        #add displays
        fenv_layout.addWidget(self.fenv_att_display, 0, 3)
        fenv_layout.addWidget(self.fenv_dec_display, 1, 3)
        fenv_layout.addWidget(self.fenv_sus_display, 2, 3)
        fenv_layout.addWidget(self.fenv_rel_display, 3, 3)
        fenv_layout.addWidget(self.fenv_amt_display, 4, 3)

        #connect signals
        self.fenv_att_slider.valueChanged.connect(self.change_attack)
        self.fenv_dec_slider.valueChanged.connect(self.change_decay)
        self.fenv_sus_slider.valueChanged.connect(self.change_sustain)
        self.fenv_rel_slider.valueChanged.connect(self.change_release)
        self.fenv_amt_slider.valueChanged.connect(self.change_amount)

        self.fenv_att_display.double_clicked.connect(self.reset_attack)
        self.fenv_dec_display.double_clicked.connect(self.reset_decay)
        self.fenv_sus_display.double_clicked.connect(self.reset_sustain)
        self.fenv_rel_display.double_clicked.connect(self.reset_release)
        self.fenv_amt_display.double_clicked.connect(self.reset_amount)

        #set layout
        self.setLayout(fenv_layout)

        #set object name
        self.setObjectName("fenv_group")
    
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

    #slots
    def change_attack(self, value):
        att = float(value)/1000.0
        self.fenv_att_display.display(f"{att:.2f}")
        self.attack_changed.emit(att)
    
    def change_decay(self, value):
        dec = float(value)/1000.0
        self.fenv_dec_display.display(f"{dec:.2f}")
        self.decay_changed.emit(dec)
    
    def change_sustain(self, value):
        sus = float(value)/1000.0
        self.fenv_sus_display.display(f"{sus:.2f}")
        self.sustain_changed.emit(sus)

    def change_release(self, value):
        rel = float(value)/1000.0
        self.fenv_rel_display.display(f"{rel:.2f}")
        self.release_changed.emit(rel)

    def change_amount(self, value):
        amt = float(value)/100.0
        self.fenv_amt_display.display(f"{amt:.2f}")
        self.amount_changed.emit(amt)

    def reset_attack(self):
        self.fenv_att_slider.setValue(10)

    def reset_decay(self):
        self.fenv_dec_slider.setValue(500)

    def reset_sustain(self):
        self.fenv_sus_slider.setValue(1000)

    def reset_release(self):
        self.fenv_rel_slider.setValue(500)

    def reset_amount(self):
        self.fenv_amt_slider.setValue(0)