from PySide6.QtWidgets import(
    QSlider, QLabel, QGridLayout,
    QLCDNumber, QPushButton,
    QGroupBox
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QPalette, QColor
from subsnake.gui.lcd import ClickLCD
from subsnake.gui.mod_gui import CoolDial

class EnvelopeGUI(QGroupBox):
    #signals
    attack_changed = Signal(float)
    decay_changed = Signal(float)
    sustain_changed = Signal(float)
    release_changed = Signal(float)
    gate_changed = Signal(bool)

    def __init__(self, display_color=QColor("black")):
        super().__init__()
        self.display_color = display_color

        #set title
        self.setTitle("envelope")

        #layout
        env_layout = QGridLayout()

        #dials
        self.env_att_mod_dial = CoolDial(1, -500, 500)
        self.env_dec_mod_dial = CoolDial(1, -500, 500)
        self.env_sus_mod_dial = CoolDial(1, -500, 500)
        self.env_rel_mod_dial = CoolDial(1, -500, 500)

        #labels
        adsr_att_label = QLabel("attack:")
        adsr_dec_label = QLabel("decay:")
        adsr_sus_label = QLabel("sustain:")
        adsr_rel_label = QLabel("release:")
        adsr_gate_label = QLabel("gate:")

        #sliders
        self.adsr_att_slider = QSlider(Qt.Horizontal)
        self.adsr_att_slider.setSingleStep(1)
        self.adsr_att_slider.setRange(1, 1000)

        self.adsr_dec_slider = QSlider(Qt.Horizontal)
        self.adsr_dec_slider.setSingleStep(1)
        self.adsr_dec_slider.setRange(1, 1000)

        self.adsr_sus_slider = QSlider(Qt.Horizontal)
        self.adsr_sus_slider.setSingleStep(1)
        self.adsr_sus_slider.setRange(1, 1000)

        self.adsr_rel_slider = QSlider(Qt.Horizontal)
        self.adsr_rel_slider.setSingleStep(1)
        self.adsr_rel_slider.setRange(1, 1000)

        #displays
        self.adsr_att_display = self.configure_display(ClickLCD(), 3, QLCDNumber.Dec, QLCDNumber.Flat, True)
        self.adsr_dec_display = self.configure_display(ClickLCD(), 3, QLCDNumber.Dec, QLCDNumber.Flat, True)
        self.adsr_sus_display = self.configure_display(ClickLCD(), 3, QLCDNumber.Dec, QLCDNumber.Flat, True)
        self.adsr_rel_display = self.configure_display(ClickLCD(), 3, QLCDNumber.Dec, QLCDNumber.Flat, True)

        #set display palettes
        self.set_palette(self.adsr_att_display)
        self.set_palette(self.adsr_dec_display)
        self.set_palette(self.adsr_sus_display)
        self.set_palette(self.adsr_rel_display)

        #add dials
        env_layout.addWidget(self.env_att_mod_dial, 0, 0)
        env_layout.addWidget(self.env_dec_mod_dial, 1, 0)
        env_layout.addWidget(self.env_sus_mod_dial, 2, 0)
        env_layout.addWidget(self.env_rel_mod_dial, 3, 0)

        #add labels
        env_layout.addWidget(adsr_att_label, 0, 1)
        env_layout.addWidget(adsr_dec_label, 1, 1)
        env_layout.addWidget(adsr_sus_label, 2, 1)
        env_layout.addWidget(adsr_rel_label, 3, 1)
        env_layout.addWidget(adsr_gate_label, 4, 1)

        #add sliders
        env_layout.addWidget(self.adsr_att_slider, 0, 2)
        env_layout.addWidget(self.adsr_dec_slider, 1, 2)
        env_layout.addWidget(self.adsr_sus_slider, 2, 2)
        env_layout.addWidget(self.adsr_rel_slider, 3, 2)

        #add displays
        env_layout.addWidget(self.adsr_att_display, 0, 3)
        env_layout.addWidget(self.adsr_dec_display, 1, 3)
        env_layout.addWidget(self.adsr_sus_display, 2, 3)
        env_layout.addWidget(self.adsr_rel_display, 3, 3)

        #add gate control
        self.env_gate = QPushButton("latch")
        self.env_gate.setObjectName("env_gate")
        self.env_gate.setCheckable(True)
        env_layout.addWidget(self.env_gate, 4, 2)

        #connect signals
        self.adsr_att_slider.valueChanged.connect(self.change_attack)
        self.adsr_dec_slider.valueChanged.connect(self.change_decay)
        self.adsr_sus_slider.valueChanged.connect(self.change_sustain)
        self.adsr_rel_slider.valueChanged.connect(self.change_release)
        self.env_gate.clicked.connect(self.change_gate)

        self.adsr_att_display.double_clicked.connect(self.reset_attack)
        self.adsr_dec_display.double_clicked.connect(self.reset_decay)
        self.adsr_sus_display.double_clicked.connect(self.reset_sustain)
        self.adsr_rel_display.double_clicked.connect(self.reset_release)

        #set layout
        self.setLayout(env_layout)

        #set object name
        self.setObjectName("env_group")
    
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
        self.adsr_att_display.display(f"{att:.2f}")
        self.attack_changed.emit(att)
    
    def change_decay(self, value):
        dec = float(value)/1000.0
        self.adsr_dec_display.display(f"{dec:.2f}")
        self.decay_changed.emit(dec)
    
    def change_sustain(self, value):
        sus = float(value)/1000.0
        self.adsr_sus_display.display(f"{sus:.2f}")
        self.sustain_changed.emit(sus)

    def change_release(self, value):
        rel = float(value)/1000.0
        self.adsr_rel_display.display(f"{rel:.2f}")
        self.release_changed.emit(rel)
    
    def change_gate(self, checked):
        self.gate_changed.emit(checked)

    def reset_attack(self):
        self.adsr_att_slider.setValue(10)

    def reset_decay(self):
        self.adsr_dec_slider.setValue(500)

    def reset_sustain(self):
        self.adsr_sus_slider.setValue(1000)

    def reset_release(self):
        self.adsr_rel_slider.setValue(500)
